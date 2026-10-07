

import json
import re
from typing import Any, Dict, List, Optional

# LLM helper import (llm.py se)
try:
    from llm import get_llm_response
except ImportError:
    from backend.llm import get_llm_response


# ============================================================
# CONFIG
# ============================================================

PRIORITY_WEIGHTS = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
MAX_SIGNALS = 8
MIN_SIGNALS = 3


# ============================================================
# MAIN FUNCTION 1: Expected Profile Generate Karo
# ============================================================

def generate_expected_profile(claim: str) -> Dict[str, Any]:
    """
    Claim ke liye expected evidence signals generate karta hai.

    Input:  claim (string)
    Output: {
        "claim": "...",
        "signals": [
            {"signal": "...", "priority": "HIGH", "why": "..."},
            ...
        ]
    }
    """
    if not claim or not str(claim).strip():
        return {"claim": claim, "signals": []}

    # LLM ko prompt bhejo
    prompt = f"""You are an evidence-investigation agent.

CLAIM: "{claim}"

If this claim were TRUE, what specific kinds of evidence should
reasonably exist? Think about these categories:
  1. Primary sources (official announcements, press releases)
  2. Regulatory / legal records (filings, court documents)
  3. Independent journalism (major news outlets, wire services)
  4. Academic / expert sources (research, expert analysis)
  5. Data / statistical sources
  6. Follow-up reporting / long-term coverage

CRITICAL RULES:
- You MUST generate AT LEAST {MIN_SIGNALS} and AT MOST {MAX_SIGNALS} signals.
- Each signal must be CONCRETE and SEARCHABLE.
- Each signal must be from a DIFFERENT category above.
- Assign priority: HIGH / MEDIUM / LOW
- Give a short "why" (max 15 words).
- Return ONLY valid JSON, no commentary, no markdown.

Output format:
{{
  "signals": [
    {{"signal": "Official press release from X", "priority": "HIGH", "why": "Primary source for such claims"}},
    {{"signal": "SEC regulatory filing", "priority": "HIGH", "why": "Legal record required"}},
    {{"signal": "Reuters/Bloomberg coverage", "priority": "MEDIUM", "why": "Independent wire verification"}},
    {{"signal": "Academic expert analysis", "priority": "LOW", "why": "Expert commentary"}},
    {{"signal": "Follow-up news after 6 months", "priority": "LOW", "why": "Long-term confirmation"}}
  ]
}}
"""

    # 2 attempts (agar pehla fail ho)
    signals = []
    for attempt in range(2):
        try:
            response = get_llm_response(
                prompt,
                max_tokens=800,
                temperature=0.3 + attempt * 0.1
            )
            signals = _parse_json_signals(response or "")

            if len(signals) >= MIN_SIGNALS:
                break
            print(f"[eeg] attempt {attempt+1}: only {len(signals)} signals, retrying...")
        except Exception as e:
            print(f"[eeg] profile generation error: {e}")

    # Agar minimum nahi mile, fallback se complete karo
    if len(signals) < MIN_SIGNALS:
        print(f"[eeg] using fallback (got {len(signals)}, need {MIN_SIGNALS})")
        fallback = _fallback_signals(claim)
        existing = {s["signal"].lower() for s in signals}
        for fb in fallback:
            if len(signals) >= MIN_SIGNALS:
                break
            if fb["signal"].lower() not in existing:
                signals.append(fb)
                existing.add(fb["signal"].lower())

    return {"claim": claim, "signals": signals}


# ============================================================
# MAIN FUNCTION 2: Expected vs Found Match Karo
# ============================================================

def match_expected_vs_found(
    expected_profile: Dict[str, Any],
    found_evidence: List[Any],
) -> Dict[str, Any]:
    """
    Expected signals ko actual found evidence se match karta hai.

    Input:
        expected_profile: generate_expected_profile() ka output
        found_evidence:   list of evidence items (dict ya object)

    Output: {
        "found": [...],
        "missing": [...],
        "coverage": 40.0,
        "search_coverage": 100.0,
        "high_priority_missing": 2,
        "gap_severity": "MEDIUM",
        "summary": "..."
    }
    """
    signals = expected_profile.get("signals", [])
    if not signals:
        return _empty_eeg_result("No expected signals were generated.")

    # Evidence normalize karo (dict / Document / string sab handle)
    normalized_evidence = [_normalize_evidence(e) for e in (found_evidence or [])]

    found = []
    missing = []

    # Har expected signal ke liye evidence dhundho
    for sig in signals:
        match = _find_matching_evidence(sig.get("signal", ""), normalized_evidence)
        if match:
            found.append({
                "signal": sig.get("signal", ""),
                "priority": sig.get("priority", "MEDIUM"),
                "evidence_title": match.get("title", ""),
                "evidence_url": match.get("url", ""),
                "evidence_source": match.get("source", ""),
            })
        else:
            missing.append({
                "signal": sig.get("signal", ""),
                "priority": sig.get("priority", "MEDIUM"),
                "why": sig.get("why", ""),
            })

    # Metrics calculate karo
    total = len(signals)
    found_count = len(found)
    coverage = (found_count / total * 100) if total > 0 else 0.0
    search_coverage = 100.0  # Humne sab categories search ki

    high_priority_missing = sum(1 for m in missing if m.get("priority") == "HIGH")

    gap_severity = _compute_gap_severity(
        coverage=coverage,
        high_priority_missing=high_priority_missing,
        total=total,
    )

    summary = _build_summary(
        coverage=coverage,
        found_count=found_count,
        total=total,
        high_priority_missing=high_priority_missing,
        gap_severity=gap_severity,
    )

    return {
        "found": found,
        "missing": missing,
        "coverage": round(coverage, 1),
        "search_coverage": search_coverage,
        "high_priority_missing": high_priority_missing,
        "gap_severity": gap_severity,
        "summary": summary,
    }


# ============================================================
# MAIN FUNCTION 3: Kyun Expected Tha Explain Karo
# ============================================================

def explain_why_expected(signal: str, claim: str) -> str:
    """
    Ek signal ke liye explain karta hai ki woh kyun expected tha.
    UI tooltip ke liye useful.
    """
    prompt = f"""In 2 short sentences, explain why this evidence signal
would reasonably be expected if the claim were true.

CLAIM: "{claim}"
SIGNAL: "{signal}"

Keep it factual and brief. Do not invent specifics.
"""
    try:
        response = get_llm_response(prompt, max_tokens=150, temperature=0.3)
        return (response or "").strip() or "This type of evidence normally accompanies claims of this kind."
    except Exception:
        return "This type of evidence normally accompanies claims of this kind."


# ============================================================
# HELPER: LLM Response Se Signals Parse Karo
# ============================================================

def _parse_json_signals(response: str) -> List[Dict[str, str]]:
    """LLM response se signals extract karta hai."""
    text = (response or "").strip()

    # Markdown code fences hataao
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                text = part
                break

    signals = []
    try:
        data = json.loads(text)
        signals = data.get("signals", [])
    except Exception:
        signals = _regex_extract_signals(text)

    # Clean + validate
    cleaned = []
    for s in signals[:MAX_SIGNALS]:
        if not isinstance(s, dict):
            continue
        signal_text = str(s.get("signal", "")).strip()
        if not signal_text:
            continue
        priority = str(s.get("priority", "MEDIUM")).upper()
        if priority not in PRIORITY_WEIGHTS:
            priority = "MEDIUM"
        cleaned.append({
            "signal": signal_text,
            "priority": priority,
            "why": str(s.get("why", "")).strip(),
        })

    return cleaned


# ============================================================
# HELPER: Regex Fallback
# ============================================================

def _regex_extract_signals(text: str) -> List[Dict[str, str]]:
    """Agar JSON parse fail ho, toh regex se nikalo."""
    signals = []
    pattern = re.compile(
        r'"signal"\s*:\s*"([^"]+)"\s*,\s*'
        r'"priority"\s*:\s*"([^"]+)"\s*,\s*'
        r'"why"\s*:\s*"([^"]*)"',
        re.IGNORECASE,
    )
    for m in pattern.finditer(text):
        signals.append({
            "signal": m.group(1),
            "priority": m.group(2).upper(),
            "why": m.group(3),
        })
    return signals


# ============================================================
# HELPER: Fallback Signals
# ============================================================

def _fallback_signals(claim: str) -> List[Dict[str, str]]:
    """Agar LLM bilkul fail ho jaye, toh yeh 5 signals use karo."""
    return [
        {
            "signal": f"Official press release or announcement regarding: {claim}",
            "priority": "HIGH",
            "why": "Primary sources normally exist for such claims.",
        },
        {
            "signal": f"Regulatory or legal filing confirming: {claim}",
            "priority": "HIGH",
            "why": "Legal records support verifiable claims.",
        },
        {
            "signal": f"Independent news coverage (Reuters, AP, Bloomberg) of: {claim}",
            "priority": "MEDIUM",
            "why": "Major claims generate wire service reporting.",
        },
        {
            "signal": f"Academic or expert analysis of: {claim}",
            "priority": "MEDIUM",
            "why": "Experts typically comment on significant claims.",
        },
        {
            "signal": f"Follow-up reporting or long-term coverage of: {claim}",
            "priority": "LOW",
            "why": "Sustained claims receive ongoing coverage.",
        },
    ]


# ============================================================
# HELPER: Evidence Normalize Karo
# ============================================================

def _normalize_evidence(item: Any) -> Dict[str, str]:
    """Kisi bhi format ke evidence ko common dict mein convert karo."""
    if isinstance(item, dict):
        return {
            "title": str(item.get("title", "")),
            "source": str(item.get("source", "")),
            "url": str(item.get("url", "") or item.get("link", "")),
            "snippet": str(item.get("snippet", "") or item.get("text", "")),
        }

    # Document-style object (metadata + page_content)
    metadata = getattr(item, "metadata", {}) or {}
    page_content = getattr(item, "page_content", "")

    return {
        "title": str(metadata.get("title", "")),
        "source": str(metadata.get("source", "")),
        "url": str(metadata.get("url", "")),
        "snippet": str(page_content),
    }


# ============================================================
# HELPER: Tokenize (stopwords hataao)
# ============================================================

def _tokenize(text: str) -> set:
    """Text ko meaningful tokens mein todo."""
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
# HELPER: Signal Ke Liye Best Evidence Match Dhundho
# ============================================================

def _find_matching_evidence(
    signal: str,
    evidence_list: List[Dict[str, str]],
    threshold: float = 0.25,
) -> Optional[Dict[str, str]]:
    """
    Signal ke tokens aur evidence ke tokens compare karta hai.
    Best match return karta hai (agar score >= threshold).
    """
    signal_tokens = _tokenize(signal)
    if not signal_tokens:
        return None

    best_match = None
    best_score = 0.0

    for ev in evidence_list:
        ev_text = f"{ev.get('title', '')} {ev.get('snippet', '')}"
        ev_tokens = _tokenize(ev_text)

        if not ev_tokens:
            continue

        overlap = signal_tokens.intersection(ev_tokens)
        score = len(overlap) / len(signal_tokens)

        if score > best_score:
            best_score = score
            best_match = ev

    if best_score >= threshold:
        return best_match

    return None


# ============================================================
# HELPER: Gap Severity Calculate Karo
# ============================================================

def _compute_gap_severity(
    coverage: float,
    high_priority_missing: int,
    total: int,
) -> str:
    """Coverage aur missing signals se severity nikalo."""
    if total == 0:
        return "UNKNOWN"

    if coverage >= 75 and high_priority_missing == 0:
        return "NONE"

    if high_priority_missing >= 2 or coverage < 40:
        return "HIGH"

    if high_priority_missing == 1 or coverage < 60:
        return "MEDIUM"

    return "LOW"


# ============================================================
# HELPER: Summary Build Karo
# ============================================================

def _build_summary(
    coverage,
    found_count,
    total,
    high_priority_missing,
    gap_severity,
) -> str:
    """Human-readable summary banao."""
    base = (
        f"{found_count}/{total} expected evidence signals "
        f"were found (coverage {coverage:.1f}%)."
    )

    if gap_severity == "NONE":
        return base + " Expected evidence is well-represented."

    if gap_severity == "HIGH":
        return (
            base
            + f" {high_priority_missing} high-priority signal(s) missing. "
            + "This does not prove the claim false, but important "
            + "corroboration was not found in the searched sources."
        )

    return base + f" Gap severity: {gap_severity}."


# ============================================================
# HELPER: Empty EEG Result
# ============================================================

def _empty_eeg_result(reason: str) -> Dict[str, Any]:
    """Empty result jab kuch na mile."""
    return {
        "found": [],
        "missing": [],
        "coverage": 0.0,
        "search_coverage": 0.0,
        "high_priority_missing": 0,
        "gap_severity": "UNKNOWN",
        "summary": reason,
    }


# ============================================================
# UI HELPER: Streamlit Ke Liye KPIs
# ============================================================

def get_eeg_kpis(eeg_result: Dict[str, Any]) -> Dict[str, str]:
    """
    Streamlit UI mein dikhane ke liye KPI dict.
    UI label: '📊 Expected Evidence Gap (EEG)'
    """
    return {
        "Coverage": f"{eeg_result.get('coverage', 0.0):.1f}%",
        "Search Coverage": f"{eeg_result.get('search_coverage', 0.0):.1f}%",
        "Missing": str(len(eeg_result.get("missing", []))),
        "High-Priority Missing": str(eeg_result.get("high_priority_missing", 0)),
        "Gap Severity": str(eeg_result.get("gap_severity", "UNKNOWN")),
    }


# ============================================================
# TEST (sirf development ke liye)
# ============================================================

if __name__ == "__main__":
    claim = "Elon Musk acquired Twitter in 2022"

    print("=" * 60)
    print("EEG Engine — Expected Evidence Gap — Self-Test")
    print("=" * 60)

    # Step 1: Generate expected profile
    print("\n[1] Generating expected profile...")
    profile = generate_expected_profile(claim)
    print(f"Generated {len(profile['signals'])} signals:")
    for s in profile["signals"]:
        print(f"  [{s['priority']}] {s['signal']}")
        print(f"           why: {s['why']}")

    # Step 2: Fake evidence se match karo
    fake_evidence = [
        {
            "title": "Elon Musk completes Twitter acquisition",
            "source": "Reuters",
            "url": "https://reuters.com/...",
            "snippet": "Elon Musk officially completed the $44 billion acquisition of Twitter in October 2022.",
        },
        {
            "title": "SEC filing for Twitter acquisition",
            "source": "SEC",
            "url": "https://sec.gov/...",
            "snippet": "Regulatory filing confirms the Twitter acquisition by Elon Musk.",
        },
    ]

    print("\n[2] Matching vs found evidence...")
    eeg_result = match_expected_vs_found(profile, fake_evidence)

    print(f"\nCoverage: {eeg_result['coverage']}%")
    print(f"Gap Severity: {eeg_result['gap_severity']}")
    print(f"High-Priority Missing: {eeg_result['high_priority_missing']}")
    print(f"Summary: {eeg_result['summary']}")

    print("\n[3] Found:")
    for f in eeg_result["found"]:
        print(f"  ✓ {f['signal']}")
        print(f"      → {f['evidence_title'][:80]}")

    print("\n[4] Missing:")
    for m in eeg_result["missing"]:
        print(f"  ✗ [{m['priority']}] {m['signal']}")