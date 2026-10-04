# conflict.py
# Kaam: Claim extraction + conflict detection + answerability check

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


CLAIM_PROMPT = """Extract factual claims from this text.

Return ONLY valid JSON:
{
  "claims": [
    {"claim": "exact claim text", "type": "date/number/name/status"}
  ]
}

If no claims, return: {"claims": []}
"""


CONFLICT_PROMPT = """You are a STRICT conflict detector.

Compare these claims and find contradictions.

CONFLICT means:
- Different dates for same event
- Different numbers for same fact
- Different names for same entity
- Contradictory statements

Return ONLY valid JSON:
{
  "conflict": true/false,
  "pairs": [
    {
      "source_a": "file name",
      "claim_a": "claim from doc A",
      "source_b": "file name",
      "claim_b": "claim from doc B",
      "explanation": "why they conflict"
    }
  ]
}

If NO conflict: {"conflict": false, "pairs": []}
"""


def extract_claims(chunk_text):
    # Ek chunk se claims nikalta hai
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": CLAIM_PROMPT},
                {"role": "user", "content": chunk_text}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"claims": []}


def detect_conflict(chunks):
    # Chunks se claims nikalo
    all_claims = []
    for c in chunks:
        claims_data = extract_claims(c["text"])
        for claim in claims_data.get("claims", []):
            all_claims.append({
                "claim": claim.get("claim", ""),
                "type": claim.get("type", "unknown"),
                "source": c["file"],
                "page": c.get("page", "?")
            })

    if len(all_claims) < 2:
        return {"conflict": False, "pairs": [], "claims": all_claims}

    # Claims compare karo
    claims_json = json.dumps(all_claims, indent=2)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": CONFLICT_PROMPT},
                {"role": "user", "content": claims_json}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        result["claims"] = all_claims
        return result
    except Exception:
        return {"conflict": False, "pairs": [], "claims": all_claims}


def check_answerability(chunks, conflict_data, query):
    # Answerability check karta hai — honest labels
    if not chunks:
        return {
            "level": "no_evidence",
            "label": "No evidence found",
            "reason": "No relevant documents found for this question"
        }

    if conflict_data.get("conflict"):
        return {
            "level": "cannot_determine",
            "label": "Cannot determine reliably",
            "reason": "Conflicting evidence found across documents"
        }

    avg_score = sum(c["score"] for c in chunks) / len(chunks)
    if avg_score > 1.5:
        return {
            "level": "low_relevance",
            "label": "Low relevance",
            "reason": "Found documents but they may not directly answer this"
        }

    sources = set(c["file"] for c in chunks)
    if len(sources) >= 2:
        return {
            "level": "strong",
            "label": "Strong evidence",
            "reason": f"{len(sources)} sources agree"
        }
    else:
        return {
            "level": "moderate",
            "label": "Moderate evidence",
            "reason": f"Only {len(sources)} source found"
        }


def calculate_evidence_confidence(chunks, conflict_data):
    # Scientific evidence confidence score
    if chunks:
        avg_dist = sum(c["score"] for c in chunks) / len(chunks)
        relevance = max(0, 100 - (avg_dist * 30))
    else:
        relevance = 0

    sources = set(c["file"] for c in chunks)
    if conflict_data.get("conflict"):
        agreement = 0
    elif len(sources) >= 3:
        agreement = 100
    elif len(sources) == 2:
        agreement = 80
    elif len(sources) == 1:
        agreement = 60
    else:
        agreement = 0

    penalty = -55 if conflict_data.get("conflict") else 0

    score = (relevance * 0.4) + (agreement * 0.4) + penalty
    score = max(0, min(100, score))

    return {
        "score": round(score),
        "relevance": round(relevance),
        "agreement": agreement,
        "penalty": penalty,
        "label": "Evidence Confidence"
    }