"""
TruthLens — Verdict Engine

Yeh module evidence se deterministic verdict nikalta hai.

IMPORTANT:
    - LLM FINAL truth decide nahi karta
    - LLM sirf explain karta hai (baad mein)
    - Missing evidence ≠ claim false
    - Source count ≠ independent evidence count

Verdict Types:
    - SUPPORTED      (evidence claim ko support karta hai)
    - CONFLICTED     (dono taraf evidence hai)
    - INSUFFICIENT   (evidence kam hai)
    - UNKNOWN        (koi evidence nahi)
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Sequence
from collections import defaultdict
import math
import re


# ============================================================
# CONFIG
# ============================================================

WEIGHTS = {
    "relevance": 0.22,
    "source_quality": 0.18,
    "independence": 0.18,
    "directness": 0.14,
    "primary_source": 0.12,
    "recency": 0.06,
    "specificity": 0.10,
}

MIN_USABLE_SCORE = 0.35

SUPPORTED_THRESHOLD = 0.68
CONFLICTED_THRESHOLD = 0.62
INSUFFICIENT_THRESHOLD = 0.45

DIRECTION_MARGIN = 0.12


# ============================================================
# DATACLASS
# ============================================================

@dataclass
class ScoredEvidence:
    """Ek evidence item ka scored representation."""
    index: int
    title: str
    source: str
    url: str
    stance: str

    relevance: float
    source_quality: float
    independence: float
    directness: float
    primary_source: float
    recency: float
    specificity: float

    evidence_score: float
    cluster_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# MAIN FUNCTION 1: calculate_verdict
# ============================================================

def calculate_verdict(
    claim: str,
    evidence: Sequence[Any],
    *,
    answerability: Optional[Dict[str, Any]] = None,
    cluster_data: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Evidence se verdict calculate karo (deterministic).
    """
    if not claim or not str(claim).strip():
        return _empty_verdict("No claim was provided.")

    # Evidence normalize karo
    normalized = [
        _normalize_evidence(item, index=i)
        for i, item in enumerate(evidence or [])
    ]

    # Cluster data attach karo
    if cluster_data:
        normalized = _attach_cluster_info(normalized, cluster_data)

    # Cluster sizes
    cluster_sizes = _build_cluster_sizes(normalized)

    # Har evidence ko score karo
    scored = [
        score_evidence(claim, item, index=i, cluster_sizes=cluster_sizes)
        for i, item in enumerate(normalized)
    ]

    # Stance mass
    stance_mass = _aggregate_stance(scored)

    # Independent clusters count
    independent_clusters = count_independent_clusters(scored)

    # Support/contradict scores
    total_directional = stance_mass["support"] + stance_mass["contradict"]

    if total_directional > 0:
        support_score = stance_mass["support"] / total_directional
        contradiction_score = stance_mass["contradict"] / total_directional
    else:
        support_score = 0.0
        contradiction_score = 0.0

    # Usable evidence
    usable_evidence = sum(
        1 for item in scored
        if item.evidence_score >= MIN_USABLE_SCORE
    )

    # Conflict ratio
    conflict_ratio = _calculate_conflict_ratio(stance_mass)

    # Answerability level
    answerability_level = None
    if answerability:
        answerability_level = (
            answerability.get("level")
            or answerability.get("status")
        )

    # Final verdict
    verdict = determine_verdict(
        support_score=support_score,
        contradict_score=contradiction_score,
        independent_clusters=independent_clusters,
        conflict_ratio=conflict_ratio,
        usable_evidence=usable_evidence,
        answerability_level=answerability_level,
    )

    # Confidence
    confidence = _calculate_confidence(
        verdict=verdict,
        scored=scored,
        independent_clusters=independent_clusters,
        conflict_ratio=conflict_ratio,
    )

    # Summary
    summary = _build_summary(
        verdict=verdict,
        confidence=confidence,
        support_score=support_score,
        contradiction_score=contradiction_score,
        independent_clusters=independent_clusters,
        usable_evidence=usable_evidence,
    )

    return {
        "verdict": verdict,
        "level": verdict.lower(),
        "confidence": confidence,
        "support_score": round(support_score, 4),
        "contradiction_score": round(contradiction_score, 4),
        "evidence_count": len(scored),
        "usable_evidence": usable_evidence,
        "independent_clusters": independent_clusters,
        "conflict_ratio": round(conflict_ratio, 4),
        "scored_evidence": [item.to_dict() for item in scored],
        "stance_mass": {
            k: round(v, 4) for k, v in stance_mass.items()
        },
        "summary": summary,
    }


# ============================================================
# MAIN FUNCTION 2: apply_eeg_gate
# ============================================================

def apply_eeg_gate(
    verdict_result: Dict[str, Any],
    eeg_result: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    EEG gap ko conservative gate ke roop mein apply karo.
    """
    if not eeg_result:
        return verdict_result

    current = str(verdict_result.get("verdict", "UNKNOWN")).upper()
    coverage = eeg_result.get("coverage", 0.0)
    search_coverage = eeg_result.get("search_coverage")
    severity = str(eeg_result.get("gap_severity", "UNKNOWN")).upper()
    high_priority_missing = int(eeg_result.get("high_priority_missing", 0))

    if current == "CONFLICTED":
        return verdict_result

    if search_coverage is None:
        return verdict_result

    if (
        current == "SUPPORTED"
        and severity == "HIGH"
        and search_coverage >= 70
        and coverage < 50
        and high_priority_missing >= 1
        and verdict_result.get("confidence", 0.0) < 85.0
    ):
        updated = dict(verdict_result)
        updated["verdict"] = "INSUFFICIENT"
        updated["level"] = "insufficient"
        updated["summary"] = (
            "Supporting evidence exists, but important expected "
            "corroboration was not found in sufficiently searched sources."
        )
        updated["eeg_gate_applied"] = True
        return updated

    return verdict_result


# ============================================================
# EVIDENCE SCORING
# ============================================================

def score_evidence(
    claim: str,
    evidence: Any,
    index: int = 0,
    cluster_sizes: Optional[Dict[str, int]] = None,
) -> ScoredEvidence:
    """Ek evidence item ko score karo."""
    normalized = _normalize_evidence(evidence, index=index)

    relevance = _calc_relevance(claim, normalized)
    source_quality = _infer_source_quality(normalized)
    independence = _infer_independence(normalized, cluster_sizes)
    directness = _infer_directness(normalized)
    primary_source = _infer_primary_source(normalized)
    recency = _infer_recency(normalized)
    specificity = _infer_specificity(claim, normalized)

    score = (
        WEIGHTS["relevance"] * relevance
        + WEIGHTS["source_quality"] * source_quality
        + WEIGHTS["independence"] * independence
        + WEIGHTS["directness"] * directness
        + WEIGHTS["primary_source"] * primary_source
        + WEIGHTS["recency"] * recency
        + WEIGHTS["specificity"] * specificity
    )

    return ScoredEvidence(
        index=index,
        title=normalized["title"],
        source=normalized["source"],
        url=normalized["url"],
        stance=normalized["stance"],
        relevance=round(relevance, 4),
        source_quality=round(source_quality, 4),
        independence=round(independence, 4),
        directness=round(directness, 4),
        primary_source=round(primary_source, 4),
        recency=round(recency, 4),
        specificity=round(specificity, 4),
        evidence_score=round(max(0.0, min(1.0, score)), 4),
        cluster_id=normalized.get("cluster_id"),
    )


# ============================================================
# NORMALIZE
# ============================================================

def _normalize_evidence(item: Any, index: int = 0) -> Dict[str, Any]:
    """Kisi bhi format ke evidence ko common dict mein convert karo."""
    if isinstance(item, dict):
        return {
            "title": str(item.get("title", "")),
            "source": str(item.get("source", "")),
            "url": str(item.get("url", "") or item.get("link", "")),
            "snippet": str(item.get("snippet", "") or item.get("text", "")),
            "date": item.get("date"),
            "stance": _normalize_stance(item.get("stance") or item.get("label")),
            "relevance": item.get("relevance"),
            "source_quality": item.get("source_quality"),
            "independence": item.get("independence"),
            "directness": item.get("directness"),
            "primary_source": item.get("primary_source"),
            "recency": item.get("recency"),
            "specificity": item.get("specificity"),
            "cluster_id": item.get("cluster_id"),
            "index": index,
        }

    metadata = getattr(item, "metadata", {}) or {}
    page_content = getattr(item, "page_content", "")

    return {
        "title": str(metadata.get("title", "")),
        "source": str(metadata.get("source", "") or metadata.get("author", "")),
        "url": str(metadata.get("url", "")),
        "snippet": str(page_content or metadata.get("snippet", "")),
        "date": metadata.get("date"),
        "stance": _normalize_stance(metadata.get("stance")),
        "relevance": metadata.get("relevance"),
        "source_quality": metadata.get("source_quality"),
        "independence": metadata.get("independence"),
        "directness": metadata.get("directness"),
        "primary_source": metadata.get("primary_source"),
        "recency": metadata.get("recency"),
        "specificity": metadata.get("specificity"),
        "cluster_id": metadata.get("cluster_id"),
        "index": index,
    }


def _normalize_stance(value: Any) -> str:
    """Stance ko standard form mein convert karo."""
    stance = str(value or "").strip().lower()

    # Already standard form — direct return
    if stance in ("support", "contradict", "neutral"):
        return stance

    aliases = {
        "supporting": "support",
        "supports": "support",
        "supported": "support",
        "pro": "support",
        "positive": "support",
        "for": "support",

        "contradicting": "contradict",
        "contradiction": "contradict",
        "contradicts": "contradict",
        "against": "contradict",
        "counter": "contradict",
        "negative": "contradict",
        "oppose": "contradict",
        "opposing": "contradict",

        "unknown": "neutral",
        "unclear": "neutral",
        "neither": "neutral",
        "mixed": "neutral",
    }

    return aliases.get(stance, "neutral")


# ============================================================
# SCORING HELPERS
# ============================================================

def _calc_relevance(claim: str, evidence: Dict[str, Any]) -> float:
    """Lexical relevance (token overlap)."""
    provided = evidence.get("relevance")
    if provided is not None:
        try:
            return max(0.0, min(1.0, float(provided)))
        except (TypeError, ValueError):
            pass

    claim_tokens = _tokenize(claim)
    evidence_text = f"{evidence.get('title', '')} {evidence.get('snippet', '')}"
    evidence_tokens = _tokenize(evidence_text)

    if not claim_tokens or not evidence_tokens:
        return 0.0

    overlap = claim_tokens.intersection(evidence_tokens)
    return min(1.0, len(overlap) / max(len(claim_tokens), 1))


def _infer_source_quality(evidence: Dict[str, Any]) -> float:
    """Source quality based on domain."""
    provided = evidence.get("source_quality")
    if provided is not None:
        try:
            return max(0.0, min(1.0, float(provided)))
        except (TypeError, ValueError):
            pass

    text = (
        f"{evidence.get('source', '')} "
        f"{evidence.get('url', '')} "
        f"{evidence.get('title', '')}"
    ).lower()

    high_quality = [
        ".gov", "sec.gov", "court", "reuters", "apnews",
        "nature.com", "science.org", "who.int", "un.org",
    ]
    if any(x in text for x in high_quality):
        return 0.90

    if evidence.get("primary_source"):
        return 0.88

    medium_quality = ["news", "times", "post", "guardian", "bbc"]
    if any(x in text for x in medium_quality):
        return 0.75

    low_quality = ["blog", "forum", "reddit", "twitter", "facebook"]
    if any(x in text for x in low_quality):
        return 0.45

    return 0.60


def _infer_primary_source(evidence: Dict[str, Any]) -> float:
    """Primary source detect karo."""
    value = evidence.get("primary_source")
    if value is not None:
        return 1.0 if bool(value) else 0.0

    text = (
        f"{evidence.get('source', '')} "
        f"{evidence.get('url', '')} "
        f"{evidence.get('title', '')}"
    ).lower()

    official = [
        ".gov", "sec.gov", "company.com", "official",
        "press release", "filing", "court",
    ]

    return 0.85 if any(p in text for p in official) else 0.0


def _infer_directness(evidence: Dict[str, Any]) -> float:
    """Direct evidence hai ya indirect?"""
    provided = evidence.get("directness")
    if provided is not None:
        try:
            return max(0.0, min(1.0, float(provided)))
        except (TypeError, ValueError):
            pass

    text = str(evidence.get("snippet", "")).lower()

    direct_markers = [
        "according to", "announced", "confirmed", "statement",
        "filing", "official", "the company said", "court order",
    ]

    if any(m in text for m in direct_markers):
        return 0.80

    if len(text) >= 100:
        return 0.60

    return 0.40


def _infer_recency(evidence: Dict[str, Any]) -> float:
    """Recency (date-based)."""
    provided = evidence.get("recency")
    if provided is not None:
        try:
            return max(0.0, min(1.0, float(provided)))
        except (TypeError, ValueError):
            pass

    return 0.50


def _infer_specificity(claim: str, evidence: Dict[str, Any]) -> float:
    """Claim ke saath specific match."""
    provided = evidence.get("specificity")
    if provided is not None:
        try:
            return max(0.0, min(1.0, float(provided)))
        except (TypeError, ValueError):
            pass

    claim_tokens = _tokenize(claim)
    snippet_tokens = _tokenize(str(evidence.get("snippet", "")))

    if not claim_tokens or not snippet_tokens:
        return 0.0

    overlap = claim_tokens.intersection(snippet_tokens)
    return min(1.0, len(overlap) / len(claim_tokens))


def _infer_independence(
    evidence: Dict[str, Any],
    cluster_sizes: Optional[Dict[str, int]] = None,
) -> float:
    """Independence based on cluster size."""
    provided = evidence.get("independence")
    if provided is not None:
        try:
            return max(0.0, min(1.0, float(provided)))
        except (TypeError, ValueError):
            pass

    cluster_id = evidence.get("cluster_id")
    if not cluster_id or not cluster_sizes:
        return 0.70

    size = cluster_sizes.get(str(cluster_id), 1)
    score = 1.0 / math.sqrt(max(size, 1))
    return max(0.0, min(1.0, score))


# ============================================================
# TOKENIZE
# ============================================================

def _tokenize(text: str) -> set:
    """Text ko tokens mein todo."""
    words = re.findall(r"[a-zA-Z0-9]{3,}", text.lower())

    stopwords = {
        "the", "and", "for", "with", "that", "this", "from",
        "was", "were", "are", "has", "have", "had", "not",
        "but", "into", "than", "their", "they", "them", "then",
        "its", "his", "her", "our", "your", "you", "can",
        "could", "would", "should", "may", "might", "will",
        "about", "after", "before", "during", "over", "under",
    }

    return {w for w in words if w not in stopwords}


# ============================================================
# STANCE AGGREGATION
# ============================================================

def _aggregate_stance(scored: Sequence[ScoredEvidence]) -> Dict[str, float]:
    """Support/contradict mass calculate karo."""
    support = 0.0
    contradict = 0.0
    neutral = 0.0

    for item in scored:
        if item.evidence_score < MIN_USABLE_SCORE:
            continue

        if item.stance == "support":
            support += item.evidence_score
        elif item.stance == "contradict":
            contradict += item.evidence_score
        else:
            neutral += item.evidence_score

    return {
        "support": support,
        "contradict": contradict,
        "neutral": neutral,
    }


def _calculate_conflict_ratio(stance_mass: Dict[str, float]) -> float:
    """Support vs contradict ka ratio."""
    support = stance_mass["support"]
    contradict = stance_mass["contradict"]
    total = support + contradict

    if total <= 0:
        return 0.0

    return min(support, contradict) / total


# ============================================================
# CLUSTER HELPERS
# ============================================================

def _build_cluster_sizes(evidence: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    """Cluster sizes count karo."""
    counts = defaultdict(int)
    for item in evidence:
        cid = item.get("cluster_id")
        if cid:
            counts[str(cid)] += 1
    return dict(counts)


def count_independent_clusters(scored: Sequence[ScoredEvidence]) -> int:
    """Independent clusters count karo."""
    clusters = set()

    for item in scored:
        if item.evidence_score < MIN_USABLE_SCORE:
            continue

        if item.cluster_id:
            clusters.add(f"cluster:{item.cluster_id}")
            continue

        source = (
            item.source.strip().lower()
            or item.url.strip().lower()
            or f"unknown:{item.index}"
        )
        clusters.add(f"source:{source}")

    return len(clusters)


def _attach_cluster_info(
    evidence: List[Dict[str, Any]],
    cluster_data: Any,
) -> List[Dict[str, Any]]:
    """Cluster IDs ko evidence items pe attach karo."""
    if isinstance(cluster_data, dict):
        clusters = cluster_data.get("clusters", [])
    elif isinstance(cluster_data, list):
        clusters = cluster_data
    else:
        return evidence

    updated = [dict(item) for item in evidence]

    for cluster in clusters:
        if not isinstance(cluster, dict):
            continue

        cluster_id = cluster.get("cluster_id") or cluster.get("id")
        indices = (
            cluster.get("source_indices")
            or cluster.get("indices")
            or cluster.get("members")
            or []
        )

        if cluster_id is None:
            continue

        for raw_index in indices:
            try:
                idx = int(raw_index)
            except (TypeError, ValueError):
                continue
            if 0 <= idx < len(updated):
                updated[idx]["cluster_id"] = str(cluster_id)

    return updated


# ============================================================
# VERDICT DECISION
# ============================================================

def determine_verdict(
    support_score: float,
    contradict_score: float,
    independent_clusters: int,
    conflict_ratio: float,
    usable_evidence: int,
    answerability_level: Optional[str] = None,
) -> str:
    """Verdict decide karo (deterministic)."""

    support_score = max(0.0, min(1.0, support_score))
    contradict_score = max(0.0, min(1.0, contradict_score))

    if usable_evidence == 0:
        return "UNKNOWN"

    if answerability_level:
        level = str(answerability_level).lower()
        if level in {"unknown", "none", "insufficient", "weak"}:
            if max(support_score, contradict_score) < 0.80:
                return "INSUFFICIENT"

    if (
        support_score >= CONFLICTED_THRESHOLD
        and contradict_score >= CONFLICTED_THRESHOLD
        and conflict_ratio >= 0.20
    ):
        return "CONFLICTED"

    if (
        support_score >= SUPPORTED_THRESHOLD
        and support_score - contradict_score >= DIRECTION_MARGIN
        and independent_clusters >= 1
    ):
        return "SUPPORTED"

    if (
        contradict_score >= CONFLICTED_THRESHOLD
        and contradict_score - support_score >= DIRECTION_MARGIN
        and independent_clusters >= 1
    ):
        return "CONFLICTED"

    if max(support_score, contradict_score) >= INSUFFICIENT_THRESHOLD:
        return "INSUFFICIENT"

    return "UNKNOWN"


# ============================================================
# CONFIDENCE
# ============================================================

def _calculate_confidence(
    verdict: str,
    scored: Sequence[ScoredEvidence],
    independent_clusters: int,
    conflict_ratio: float,
) -> float:
    """Bounded confidence score (0-100)."""
    usable = [
        item for item in scored
        if item.evidence_score >= MIN_USABLE_SCORE
    ]

    if not usable:
        return 0.0

    mean_quality = sum(item.evidence_score for item in usable) / len(usable)
    independence_factor = min(independent_clusters / 4.0, 1.0)
    conflict_penalty = min(conflict_ratio, 1.0)

    confidence = (
        0.60 * mean_quality
        + 0.25 * independence_factor
        + 0.15 * (1.0 - conflict_penalty)
    )

    if verdict == "CONFLICTED":
        confidence *= 0.90
    if verdict == "UNKNOWN":
        confidence *= 0.70

    return round(max(0.0, min(1.0, confidence)) * 100, 1)


# ============================================================
# SUMMARY + EMPTY
# ============================================================

def _build_summary(
    verdict: str,
    confidence: float,
    support_score: float,
    contradiction_score: float,
    independent_clusters: int,
    usable_evidence: int,
) -> str:
    if verdict == "SUPPORTED":
        return (
            f"Evidence currently supports the claim with "
            f"{confidence:.1f}% evidence confidence across "
            f"{independent_clusters} apparent independent evidence cluster(s)."
        )

    if verdict == "CONFLICTED":
        return (
            f"Material evidence exists on both sides of the claim. "
            f"Support={support_score:.2f}, contradiction={contradiction_score:.2f}, "
            f"across {independent_clusters} apparent independent cluster(s)."
        )

    if verdict == "INSUFFICIENT":
        return (
            f"Some relevant evidence was found ({usable_evidence} usable item(s)), "
            f"but it is not sufficient for a reliable directional verdict."
        )

    return "The available evidence is too weak or unclear to determine the claim reliably."


def _empty_verdict(reason: str) -> Dict[str, Any]:
    return {
        "verdict": "UNKNOWN",
        "level": "unknown",
        "confidence": 0.0,
        "support_score": 0.0,
        "contradiction_score": 0.0,
        "evidence_count": 0,
        "usable_evidence": 0,
        "independent_clusters": 0,
        "conflict_ratio": 0.0,
        "scored_evidence": [],
        "stance_mass": {"support": 0, "contradict": 0, "neutral": 0},
        "summary": reason,
    }


# ============================================================
# UI HELPERS
# ============================================================

def get_verdict_badge(verdict: str) -> str:
    """UI badge string."""
    badges = {
        "SUPPORTED": "✅ SUPPORTED",
        "CONFLICTED": "⚠️ CONFLICTED",
        "INSUFFICIENT": "🟡 INSUFFICIENT",
        "UNKNOWN": "❓ UNKNOWN",
    }
    return badges.get(str(verdict).upper(), "❓ UNKNOWN")


def get_kpi_cards(verdict_result: Dict[str, Any]) -> Dict[str, str]:
    """Streamlit-ready KPI dict."""
    return {
        "Verdict": str(verdict_result.get("verdict", "UNKNOWN")),
        "Confidence": f"{verdict_result.get('confidence', 0.0):.1f}%",
        "Support": f"{verdict_result.get('support_score', 0.0) * 100:.1f}%",
        "Contradict": f"{verdict_result.get('contradiction_score', 0.0) * 100:.1f}%",
        "Evidence": str(verdict_result.get("evidence_count", 0)),
        "Independent": str(verdict_result.get("independent_clusters", 0)),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    claim = "Elon Musk acquired Twitter in 2022"

    demo_evidence = [
        {
            "title": "Elon Musk completes Twitter acquisition",
            "source": "Reuters",
            "url": "https://reuters.com/article",
            "snippet": "Elon Musk officially completed the $44 billion acquisition of Twitter in October 2022.",
            "stance": "support",
            "source_quality": 0.90,
            "primary_source": False,
            "directness": 0.85,
            "cluster_id": "cluster_news",
        },
        {
            "title": "SEC filing confirms Twitter acquisition",
            "source": "SEC",
            "url": "https://sec.gov/filing",
            "snippet": "Official regulatory filing confirms the acquisition by Elon Musk.",
            "stance": "support",
            "source_quality": 0.95,
            "primary_source": True,
            "directness": 0.95,
            "cluster_id": "cluster_official",
        },
        {
            "title": "Twitter denies acquisition rumor",
            "source": "Blog",
            "url": "https://someblog.com/x",
            "snippet": "Rumor says acquisition might not go through.",
            "stance": "contradict",
            "source_quality": 0.40,
            "directness": 0.40,
            "cluster_id": "cluster_blog",
        },
    ]

    print("=" * 60)
    print("Verdict Engine — Self-Test")
    print("=" * 60)

    result = calculate_verdict(claim, demo_evidence)

    print(f"\nVerdict:        {get_verdict_badge(result['verdict'])}")
    print(f"Confidence:     {result['confidence']}%")
    print(f"Support:        {result['support_score']}")
    print(f"Contradiction:  {result['contradiction_score']}")
    print(f"Independent:    {result['independent_clusters']}")
    print(f"Conflict Ratio: {result['conflict_ratio']}")
    print(f"\nSummary: {result['summary']}")