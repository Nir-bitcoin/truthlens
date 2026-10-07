"""
SerpApi Live Evidence Fetcher for TruthLens 2.0
Fetches claim-specific evidence from 4 surfaces:
  - Google Web (supporting + contradicting)
  - Google News (temporal + source drift)
  - Google Fact Check (direct verdict)
  - Google Scholar (academic evidence)
"""

import os
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from serpapi import GoogleSearch
from dotenv import load_dotenv

# Load env
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Cache directory
CACHE_DIR = Path("cache/serpapi")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Import LLM helper
try:
    from llm import get_llm_response
except ImportError:
    from backend.llm import get_llm_response


# ============================================================
# CACHE HELPERS
# ============================================================

def _cache_key(claim: str, engine: str) -> str:
    raw = f"{claim.strip().lower()}|{engine}"
    return hashlib.md5(raw.encode()).hexdigest()


def _load_cache(claim: str, engine: str) -> Optional[dict]:
    key = _cache_key(claim, engine)
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cached_at = datetime.fromisoformat(data.get("_cached_at", "2000-01-01"))
            if (datetime.now() - cached_at).total_seconds() < 86400:
                return data
        except Exception:
            pass
    return None


def _save_cache(claim: str, engine: str, data: dict):
    key = _cache_key(claim, engine)
    path = CACHE_DIR / f"{key}.json"
    data["_cached_at"] = datetime.now().isoformat()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ============================================================
# AGENTIC QUERY GENERATION
# ============================================================

def llm_generate_queries(claim: str) -> dict:
    prompt = f"""Generate search queries for investigating this claim.

CLAIM: "{claim}"

Return JSON with support, contradict, and fact_check queries.
Max 3 queries per category, short (4-8 words).

Output format:
{{
  "support": ["query1", "query2"],
  "contradict": ["query1", "query2"],
  "fact_check": "single best query"
}}
"""

    try:
        response = get_llm_response(prompt, max_tokens=400, temperature=0.1)
        response = (response or "").strip()
        if "```" in response:
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        queries = json.loads(response.strip())
        return queries
    except Exception as e:
        print(f"[serpapi] query generation fallback: {e}")
        return {
            "support": [claim, f"{claim} confirmed"],
            "contradict": [f"{claim} debunked", f"{claim} false"],
            "fact_check": claim
        }


# ============================================================
# ENGINE FETCHERS
# ============================================================

def _search_google(query: str, num: int = 10) -> list:
    try:
        search = GoogleSearch({
            "q": query, "api_key": SERPAPI_KEY,
            "num": num, "gl": "in", "hl": "en"
        })
        results = search.get_dict().get("organic_results", [])
        return [
            {
                "title": r.get("title", ""),
                "link": r.get("link", ""),
                "snippet": r.get("snippet", ""),
                "source": r.get("source", ""),
                "date": r.get("date", ""),
                "type": "web"
            }
            for r in results
        ]
    except Exception as e:
        print(f"[serpapi] google error: {e}")
        return []


def _search_news(query: str, num: int = 10) -> list:
    try:
        search = GoogleSearch({
            "q": query, "api_key": SERPAPI_KEY,
            "engine": "google_news", "num": num, "gl": "in", "hl": "en"
        })
        results = search.get_dict().get("news_results", [])
        cleaned = []
        for r in results:
            source = r.get("source", "")
            if isinstance(source, dict):
                source = source.get("name", "")
            cleaned.append({
                "title": r.get("title", ""),
                "link": r.get("link", ""),
                "snippet": r.get("snippet", ""),
                "source": source,
                "date": r.get("date", ""),
                "type": "news"
            })
        return cleaned
    except Exception as e:
        print(f"[serpapi] news error: {e}")
        return []


def _search_fact_check(query: str) -> list:
    try:
        search = GoogleSearch({
            "q": query, "api_key": SERPAPI_KEY,
            "engine": "google_fact_check"
        })
        results = search.get_dict().get("fact_check_results", [])
        return [
            {
                "title": r.get("title", ""),
                "link": r.get("link", ""),
                "snippet": r.get("snippet", ""),
                "source": r.get("source", ""),
                "rating": r.get("rating", ""),
                "date": r.get("date", ""),
                "type": "fact_check"
            }
            for r in results
        ]
    except Exception as e:
        print(f"[serpapi] fact_check error: {e}")
        return []


def _search_scholar(query: str, num: int = 5) -> list:
    try:
        search = GoogleSearch({
            "q": query, "api_key": SERPAPI_KEY,
            "engine": "google_scholar", "num": num
        })
        results = search.get_dict().get("organic_results", [])
        cleaned = []
        for r in results:
            pub_info = r.get("publication_info", {})
            summary = pub_info.get("summary", "") if isinstance(pub_info, dict) else ""
            cleaned.append({
                "title": r.get("title", ""),
                "link": r.get("link", ""),
                "snippet": r.get("snippet", ""),
                "source": summary,
                "date": summary,
                "type": "scholar"
            })
        return cleaned
    except Exception as e:
        print(f"[serpapi] scholar error: {e}")
        return []


# ============================================================
# MAIN FETCHER
# ============================================================

def fetch_live_evidence(claim: str, use_cache: bool = True) -> dict:
    if not SERPAPI_KEY:
        return {
            "error": "SERPAPI_KEY not set in .env",
            "supporting": [], "contradicting": [],
            "fact_checks": [], "news": [], "scholar": [],
            "queries_used": {}, "gap_flag": True, "total_results": 0
        }

    if use_cache:
        cached = _load_cache(claim, "full")
        if cached:
            cached["_from_cache"] = True
            return cached

    queries = llm_generate_queries(claim)

    supporting = []
    contradicting = []

    for q in queries.get("support", [])[:2]:
        supporting.extend(_search_google(q, num=5))

    for q in queries.get("contradict", [])[:2]:
        contradicting.extend(_search_google(q, num=5))

    news = _search_news(claim, num=10)
    fact_checks = _search_fact_check(queries.get("fact_check", claim))
    scholar = _search_scholar(claim, num=5)

    result = {
        "supporting": supporting,
        "contradicting": contradicting,
        "fact_checks": fact_checks,
        "news": news,
        "scholar": scholar,
        "queries_used": queries,
        "gap_flag": len(supporting) + len(contradicting) + len(fact_checks) == 0,
        "total_results": (
            len(supporting) + len(contradicting) +
            len(news) + len(fact_checks) + len(scholar)
        ),
        "_from_cache": False
    }

    if use_cache:
        _save_cache(claim, "full", result)

    return result


# ============================================================
# STANCE CLASSIFICATION HELPERS
# ============================================================

def _extract_stances(text: str) -> list:
    """Extract stances list from LLM response."""
    if not text:
        return []

    text = text.strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            for key in ("stances", "results", "classifications", "items"):
                if key in parsed and isinstance(parsed[key], list):
                    return parsed[key]
    except Exception:
        pass

    match = re.search(r"\[[^\]]*\]", text)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    keywords = re.findall(r"\b(support|contradict|neutral)\b", text.lower())
    return keywords


def _keyword_classify(item: dict, claim: str) -> str:
    """Deterministic keyword-based stance classifier."""
    text = (
        f"{item.get('title', '')} "
        f"{item.get('snippet', '')}"
    ).lower()

    if not text.strip():
        return "neutral"

    # Claim ke keywords
    claim_words = set(re.findall(r"\b[a-z]{4,}\b", claim.lower()))
    claim_words -= {"that", "this", "with", "from", "were", "have", "will", "been"}

    item_words = set(re.findall(r"\b[a-z]{4,}\b", text))
    overlap = claim_words.intersection(item_words)

    # Agar claim se related nahi
    if len(overlap) < 1:
        return "neutral"

    # Strong contradiction signals
    contradict_signals = [
        "debunk", "false", "fake", "misleading", "hoax", "denied",
        "no evidence", "not true", "incorrect", "wrong", "myth",
        "refuted", "disputed", "untrue", "fabricated", "misinformation",
        "criticized", "questioned", "doubtful", "skeptical", "no proof",
        "rumor", "unconfirmed", "alleged", "baseless"
    ]

    # Strong support signals
    support_signals = [
        "confirmed", "announced", "official", "verified", "approved",
        "signed", "agreed", "completed", "reported", "according to",
        "revealed", "stated", "affirmed", "acquired", "acquisition",
        "completes", "finalized", "closed", "deal", "merger",
        "announcement", "confirm", "agreement", "press release"
    ]

    contra_score = sum(1 for s in contradict_signals if s in text)
    supp_score = sum(1 for s in support_signals if s in text)

    if contra_score > supp_score:
        return "contradict"
    if supp_score > contra_score:
        return "support"
    return "neutral"


# ============================================================
# STANCE CLASSIFICATION
# ============================================================

def classify_live_evidence(evidence: dict, claim: str) -> dict:
    """Classify each evidence item as support/contradict/neutral (keyword-based)."""

    all_items = (
        evidence.get("supporting", []) +
        evidence.get("contradicting", []) +
        evidence.get("news", []) +
        evidence.get("scholar", [])
    )

    if not all_items:
        return evidence

    # Keyword-based classification for ALL items
    for item in all_items:
        item["stance"] = _keyword_classify(item, claim)

    # Rebuild lists
    supporting = [i for i in all_items if i.get("stance") == "support"]
    contradicting = [i for i in all_items if i.get("stance") == "contradict"]
    neutral = [i for i in all_items if i.get("stance") == "neutral"]

    print(f"[serpapi] Keyword classified {len(all_items)} items")

    evidence["supporting"] = supporting
    evidence["contradicting"] = contradicting
    evidence["neutral"] = neutral

    return evidence


# ============================================================
# KPI HELPERS
# ============================================================

def get_serpapi_kpis(evidence: dict) -> dict:
    return {
        "Total Sources": str(evidence.get("total_results", 0)),
        "Supporting": str(len(evidence.get("supporting", []))),
        "Contradicting": str(len(evidence.get("contradicting", []))),
        "News": str(len(evidence.get("news", []))),
        "Fact Checks": str(len(evidence.get("fact_checks", []))),
        "Scholar": str(len(evidence.get("scholar", []))),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    test_claim = "Elon Musk acquired Twitter in 2022"

    print("=" * 60)
    print(f"Testing claim: {test_claim}")
    print("=" * 60)

    result = fetch_live_evidence(test_claim)

    print(f"\n[RESULTS]")
    print(f"  Supporting:    {len(result['supporting'])}")
    print(f"  Contradicting: {len(result['contradicting'])}")
    print(f"  News:          {len(result['news'])}")
    print(f"  Fact Checks:   {len(result['fact_checks'])}")
    print(f"  Scholar:       {len(result['scholar'])}")
    print(f"  Total:         {result['total_results']}")

    print(f"\n[QUERIES USED]")
    print(json.dumps(result['queries_used'], indent=2))

    print(f"\n[CLASSIFYING STANCES...]")
    classified = classify_live_evidence(result, test_claim)
    print(f"  After classification:")
    print(f"    Support:    {len(classified['supporting'])}")
    print(f"    Contradict: {len(classified['contradicting'])}")
    print(f"    Neutral:    {len(classified.get('neutral', []))}")