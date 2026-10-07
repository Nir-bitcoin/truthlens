"""
TruthLens — CEE Engine (Counterfactual Evidence Engine)

Yeh module current verdict ko change karne ke liye decisive evidence
identify karta hai, phir targeted search karta hai.

Kaam:
    1. Current verdict + EEG gaps se decisive evidence targets nikalo
    2. Har target ke liye targeted SerpApi search
    3. Naya evidence mila toh verdict dobara calculate karo

Important Rules:
    - CEE "manufacture" evidence nahi karta — sirf search karta hai
    - Agar evidence nahi mila, toh verdict same rehta hai
    - Har target ka impact + direction batana zaroori hai
"""

import json
import re
from typing import Any, Dict, List, Optional

# LLM helper
try:
    from llm import get_llm_response
except ImportError:
    from backend.llm import get_llm_response

# SerpApi helper (targeted search ke liye)
try:
    from serpapi_evidence import _search_google, _search_news
except ImportError:
    from backend.serpapi_evidence import _search_google, _search_news


# ============================================================
# CONFIG
# ============================================================

MAX_TARGETS = 5
SEARCH_RESULTS_PER_TARGET = 3


# ============================================================
# MAIN FUNCTION 1: Decisive Evidence Identify Karo
# ============================================================

def identify_decisive_evidence(
    claim: str,
    verdict_result: Dict[str, Any],
    eeg_result: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    """
    Current verdict ko change karne ke liye kaunse evidence chahiye.

    Input:
        claim:           original claim
        verdict_result:  verdict_engine.py ka output
        eeg_result:      eeg_engine.py ka output

    Output:
        [
            {
                "evidence": "...",
                "impact": "VERY_HIGH / HIGH / MEDIUM",
                "direction": "upgrade / downgrade"
            },
            ...
        ]
    """
    if not claim:
        return []

    current_verdict = verdict_result.get("verdict", "UNKNOWN")

    # EEG ke missing signals collect karo
    missing_signals = []
    if eeg_result:
        for m in eeg_result.get("missing", []):
            missing_signals.append(
                f"[{m.get('priority', 'MEDIUM')}] {m.get('signal', '')}"
            )

    missing_text = "\n".join(missing_signals) if missing_signals else "None identified"

    prompt = f"""You are a counterfactual investigation agent.

CLAIM: "{claim}"

CURRENT VERDICT: {current_verdict}

MISSING EXPECTED EVIDENCE (from EEG):
{missing_text}

Your job: identify specific evidence that, if found, would CHANGE this verdict.

Think about:
- To UPGRADE to SUPPORTED: what primary sources would confirm the claim?
- To DOWNGRADE to CONTRADICTED: what official denial/filing would disprove it?

CRITICAL RULES:
- Do NOT make up evidence. Only identify SEARCHABLE targets.
- Each target must be specific (e.g., "SEC filing dated X" not "some document")
- Assign impact: VERY_HIGH / HIGH / MEDIUM
- Direction: "upgrade" (toward SUPPORTED) or "downgrade" (toward CONTRADICTED)
- Max {MAX_TARGETS} targets
- Return ONLY valid JSON, no markdown.

Output format:
{{
  "targets": [
    {{"evidence": "Official press release from X", "impact": "VERY_HIGH", "direction": "upgrade"}},
    {{"evidence": "Denial statement from Y", "impact": "HIGH", "direction": "downgrade"}}
  ]
}}
"""

    # 2 attempts
    for attempt in range(2):
        try:
            response = get_llm_response(
                prompt,
                max_tokens=600,
                temperature=0.2 + attempt * 0.1,
            )
            response = (response or "").strip()

            # Strip markdown fences
            if "```" in response:
                parts = response.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("json"):
                        part = part[4:].strip()
                    if part.startswith("{"):
                        response = part
                        break

            # Try direct JSON parse
            data = None
            try:
                data = json.loads(response)
            except Exception:
                # Regex fallback
                targets = _regex_extract_targets(response)
                if targets:
                    return targets
                continue

            targets = data.get("targets", [])[:MAX_TARGETS]

            # Validate + clean
            cleaned = []
            for t in targets:
                if not isinstance(t, dict):
                    continue
                evidence = str(t.get("evidence", "")).strip()
                if not evidence:
                    continue
                impact = str(t.get("impact", "MEDIUM")).upper()
                if impact not in ("VERY_HIGH", "HIGH", "MEDIUM"):
                    impact = "MEDIUM"
                direction = str(t.get("direction", "upgrade")).lower()
                if direction not in ("upgrade", "downgrade"):
                    direction = "upgrade"
                cleaned.append({
                    "evidence": evidence,
                    "impact": impact,
                    "direction": direction,
                })

            if cleaned:
                return cleaned

        except Exception as e:
            print(f"[cee] attempt {attempt+1} error: {e}")

    # Fallback
    print("[cee] using fallback targets")
    return _fallback_targets(claim, current_verdict)


# ============================================================
# HELPER: Regex Extract Targets
# ============================================================

def _regex_extract_targets(text: str) -> List[Dict[str, str]]:
    """Regex se targets nikalo agar JSON parse fail ho."""
    targets = []
    pattern = re.compile(
        r'"evidence"\s*:\s*"([^"]+)"\s*,\s*'
        r'"impact"\s*:\s*"([^"]+)"\s*,\s*'
        r'"direction"\s*:\s*"([^"]+)"',
        re.IGNORECASE,
    )
    for m in pattern.finditer(text):
        targets.append({
            "evidence": m.group(1),
            "impact": m.group(2).upper(),
            "direction": m.group(3).lower(),
        })
    return targets[:MAX_TARGETS]


# ============================================================
# MAIN FUNCTION 2: Targeted Search
# ============================================================

def targeted_search(targets: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Har target ke liye SerpApi se specifically search karo.

    Input:  targets list
    Output: combined evidence items with target metadata
    """
    if not targets:
        return []

    all_evidence = []

    for i, target in enumerate(targets):
        evidence_text = target.get("evidence", "")
        if not evidence_text:
            continue

        print(f"[cee] searching target {i+1}: {evidence_text[:60]}...")

        # Google search
        google_results = _search_google(evidence_text, num=SEARCH_RESULTS_PER_TARGET)

        # News search
        news_results = _search_news(evidence_text, num=SEARCH_RESULTS_PER_TARGET)

        # Tag each with target metadata
        for r in google_results + news_results:
            r["target"] = evidence_text
            r["target_impact"] = target.get("impact", "MEDIUM")
            r["target_direction"] = target.get("direction", "upgrade")
            all_evidence.append(r)

    return all_evidence


# ============================================================
# MAIN FUNCTION 3: Re-verify (Naya Verdict)
# ============================================================

def reverify(
    claim: str,
    all_evidence: List[Any],
    old_verdict: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Naya evidence mila toh verdict dobara calculate karo.

    Input:
        claim:        original claim
        all_evidence: purana + targeted (combined)
        old_verdict:  pehle ka verdict result

    Output:
        {
            "old_verdict": "INSUFFICIENT",
            "new_verdict": "SUPPORTED",
            "changed": True/False,
            "confidence_before": 64,
            "confidence_after": 78,
            "reason": "..."
        }
    """
    try:
        from verdict_engine import calculate_verdict
    except ImportError:
        try:
            from backend.verdict_engine import calculate_verdict
        except ImportError:
            return _fallback_reverify(old_verdict)

    new_verdict = calculate_verdict(claim, all_evidence)

    old_level = str(old_verdict.get("verdict", "UNKNOWN")).upper()
    new_level = str(new_verdict.get("verdict", "UNKNOWN")).upper()

    changed = old_level != new_level

    old_conf = old_verdict.get("confidence", 0)
    new_conf = new_verdict.get("confidence", 0)

    if changed:
        reason = (
            f"Verdict changed from {old_level} to {new_level} "
            f"after targeted evidence search."
        )
    else:
        reason = (
            f"Verdict remains {old_level} — targeted search "
            f"did not find decisive evidence."
        )

    return {
        "old_verdict": old_level,
        "new_verdict": new_level,
        "changed": changed,
        "confidence_before": old_conf,
        "confidence_after": new_conf,
        "reason": reason,
        "new_verdict_result": new_verdict,
    }


# ============================================================
# HELPER: Fallback Targets
# ============================================================

def _fallback_targets(claim: str, current_verdict: str) -> List[Dict[str, str]]:
    """Agar LLM fail ho, toh generic targets do."""
    return [
        {
            "evidence": f"Official press release or announcement regarding: {claim}",
            "impact": "VERY_HIGH",
            "direction": "upgrade",
        },
        {
            "evidence": f"Official denial or retraction related to: {claim}",
            "impact": "HIGH",
            "direction": "downgrade",
        },
        {
            "evidence": f"Regulatory or legal filing about: {claim}",
            "impact": "HIGH",
            "direction": "upgrade",
        },
    ]


# ============================================================
# HELPER: Fallback Reverify
# ============================================================

def _fallback_reverify(old_verdict: Dict[str, Any]) -> Dict[str, Any]:
    """Agar verdict_engine available nahi, toh fallback."""
    return {
        "old_verdict": str(old_verdict.get("verdict", "UNKNOWN")),
        "new_verdict": str(old_verdict.get("verdict", "UNKNOWN")),
        "changed": False,
        "confidence_before": old_verdict.get("confidence", 0),
        "confidence_after": old_verdict.get("confidence", 0),
        "reason": "Verdict engine not available — using fallback.",
        "new_verdict_result": old_verdict,
    }


# ============================================================
# UI HELPER: Streamlit KPIs
# ============================================================

def get_cee_kpis(cee_result: Dict[str, Any]) -> Dict[str, str]:
    """
    Streamlit UI ke liye KPI dict.
    UI label: '🔄 What Would Change This Verdict?'
    """
    return {
        "Old Verdict": str(cee_result.get("old_verdict", "UNKNOWN")),
        "New Verdict": str(cee_result.get("new_verdict", "UNKNOWN")),
        "Changed": "YES" if cee_result.get("changed") else "NO",
        "Confidence Before": f"{cee_result.get('confidence_before', 0)}%",
        "Confidence After": f"{cee_result.get('confidence_after', 0)}%",
    }


# ============================================================
# HELPER: Full CEE Pipeline
# ============================================================

def run_cee_pipeline(
    claim: str,
    old_verdict: Dict[str, Any],
    all_evidence: List[Any],
    eeg_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Complete CEE pipeline — targets → search → reverify.

    Returns dict with:
        targets, found_evidence, old_verdict, new_verdict, changed, reason
    """
    # Step 1: Targets identify karo
    targets = identify_decisive_evidence(claim, old_verdict, eeg_result)

    # Step 2: Targeted search
    found = targeted_search(targets)

    # Step 3: Combine old + new evidence
    combined = list(all_evidence or []) + found

    # Step 4: Re-verify
    result = reverify(claim, combined, old_verdict)

    result["targets"] = targets
    result["found_evidence"] = found

    return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    claim = "Elon Musk acquired Twitter in 2022"

    print("=" * 60)
    print("CEE Engine — Counterfactual Evidence — Self-Test")
    print("=" * 60)

    # Fake old verdict
    old_verdict = {
        "verdict": "INSUFFICIENT",
        "confidence": 60,
    }

    # Fake EEG result
    eeg_result = {
        "missing": [
            {"signal": "Official SEC filing", "priority": "HIGH"},
            {"signal": "Twitter press release", "priority": "HIGH"},
        ],
        "coverage": 40.0,
    }

    print("\n[1] Identifying decisive evidence targets...")
    targets = identify_decisive_evidence(claim, old_verdict, eeg_result)
    print(f"Found {len(targets)} targets:")
    for t in targets:
        print(f"  [{t['impact']}] [{t['direction']}] {t['evidence']}")

    print("\n[2] Targeted search (SerpApi)...")
    found = targeted_search(targets[:2])
    print(f"Found {len(found)} evidence items")

    print("\n[3] Sample found evidence:")
    for f in found[:3]:
        print(f"  → {f.get('title', '')[:70]}")
        print(f"      target: {f.get('target', '')[:50]}")