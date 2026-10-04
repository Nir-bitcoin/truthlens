# conflict.py
# Kaam: Claim extraction + conflict detection + answerability + confidence
# + Counter-Evidence 2.0 + Evidence Gap Detector + Resolution Evidence

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


CLAIM_PROMPT = """Extract factual claims from this text.

Return ONLY valid JSON:
{
  "claims": [
    {"claim": "exact claim text", "type": "date/number/name/status"}
  ]
}
"""


CONFLICT_PROMPT = """You are a STRICT conflict detector.

Compare these claims and find contradictions.

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
"""


COUNTER_EVIDENCE_2_PROMPT = """You are a rigorous investigation assistant.

CRITICAL RULES:
1. Extract EXACT numbers, dates, and facts from the evidence.
2. Do NOT change or swap values.
3. Candidate answer must be COPY-PASTED from evidence, not paraphrased.
4. If evidence says 30%, write 30% — not 20% or 15%.

Given a question and evidence chunks:

STEP 1: Generate a candidate answer by EXACTLY quoting the evidence.
STEP 2: Find evidence that SUPPORTS this candidate answer.
STEP 3: Find evidence that CONTRADICTS or WEAKENS this candidate answer.
STEP 4: Compare and decide.

Return ONLY valid JSON:
{
  "candidate_answer": "EXACT answer from evidence with numbers unchanged",
  "supporting_evidence": [
    {
      "source": "file name",
      "page": "page number",
      "claim": "supporting claim",
      "strength": "strong/medium/weak"
    }
  ],
  "contradicting_evidence": [
    {
      "source": "file name",
      "page": "page number",
      "claim": "contradicting claim",
      "impact": "why it weakens the answer"
    }
  ],
  "final_decision": "supported/contradicted/uncertain",
  "reasoning": "why this decision"
}
"""


GAP_DETECTOR_PROMPT = """You are an evidence gap detector.

Given a question, retrieved evidence, and conflict analysis, identify:

1. EVIDENCE GAPS — What evidence is MISSING to fully answer the question?
2. RESOLUTION EVIDENCE — What specific document/record would resolve the uncertainty?

CRITICAL RULES:
- Do NOT invent arbitrary documents.
- Derive gaps from: retrieved evidence + question + claim requirements.
- Be specific: "Latest signed amendment" not just "more documents".
- If answer is complete, return empty lists.

Return ONLY valid JSON:
{
  "evidence_gaps": [
    {
      "missing": "what evidence is missing",
      "why_needed": "why it is needed to answer"
    }
  ],
  "resolution_evidence": [
    {
      "document": "specific document needed",
      "reason": "how it would resolve the uncertainty"
    }
  ]
}
"""


def extract_claims(chunk_text):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
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
    all_claims = []
    for c in chunks[:2]:
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

    claims_json = json.dumps(all_claims, indent=2)

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
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
    if avg_score > 25.0:
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
    if chunks:
        avg_dist = sum(c["score"] for c in chunks) / len(chunks)
        relevance = max(0, 100 - (avg_dist * 3))
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


def find_counter_evidence(query, chunks):
    # Counter-Evidence 2.0 — Supporting + Contradicting compare
    if not chunks:
        return {
            "candidate_answer": "",
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "final_decision": "uncertain",
            "reasoning": "No evidence available"
        }

    context = "\n\n".join([
        f"[Source: {c['file']}, Page {c.get('page', '?')}]\n{c['text'][:600]}"
        for c in chunks[:6]
    ])

    prompt = f"""Question: {query}

Evidence:
{context}

Investigate thoroughly:
1. What does the evidence suggest as a candidate answer?
2. What evidence SUPPORTS it?
3. What evidence CONTRADICTS it?
4. Final decision."""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": COUNTER_EVIDENCE_2_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {
            "candidate_answer": "",
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "final_decision": "uncertain",
            "reasoning": "Analysis failed"
        }


def detect_evidence_gaps(query, chunks, conflict_data=None):
    # Evidence Gap + Resolution Evidence
    if not chunks:
        return {"evidence_gaps": [], "resolution_evidence": []}

    context = "\n\n".join([
        f"[Source: {c['file']}, Page {c.get('page', '?')}]\n{c['text'][:500]}"
        for c in chunks[:6]
    ])

    conflict_info = ""
    if conflict_data and conflict_data.get("conflict"):
        conflict_info = f"\n\nConflict detected: {json.dumps(conflict_data.get('pairs', []), indent=2)}"

    prompt = f"""Question: {query}

Available Evidence:
{context}
{conflict_info}

Identify:
1. What evidence is MISSING to fully answer this question?
2. What SPECIFIC document/record would resolve the uncertainty?

If answer is complete, return empty lists."""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": GAP_DETECTOR_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"evidence_gaps": [], "resolution_evidence": []}
EVIDENCE_BATTLE_PROMPT = """You are an evidence investigator team.

Given a question and evidence chunks, perform TWO independent investigations:

🔵 INVESTIGATOR A (SUPPORTER):
- Generate a candidate answer
- Find ALL evidence that SUPPORTS this answer
- Build the strongest possible case FOR the answer

🔴 INVESTIGATOR B (SKEPTIC):
- Challenge the candidate answer
- Find ALL evidence that CONTRADICTS or WEAKENS it
- Find what evidence is MISSING to verify the answer

⚖️ RECONCILIATION:
- Compare supporting vs contradicting evidence
- Determine final verdict based on evidence weight
- Do NOT let one LLM overpower the other

Return ONLY valid JSON:
{
  "candidate_answer": "the proposed answer",
  "supporter": {
    "claims": [
      {
        "claim": "supporting claim",
        "source": "file name",
        "page": "page number",
        "strength": "strong/medium/weak"
      }
    ],
    "total_claims": 0
  },
  "skeptic": {
    "claims": [
      {
        "claim": "contradicting or challenging claim",
        "source": "file name",
        "page": "page number",
        "impact": "high/medium/low",
        "type": "contradiction/missing_evidence/weak_support"
      }
    ],
    "total_claims": 0,
    "missing_evidence": [
      "critical evidence that is missing"
    ]
  },
  "verdict": {
    "decision": "agree/conflict/insufficient",
    "reasoning": "evidence-based reasoning",
    "supporting_count": 0,
    "counter_count": 0,
    "critical_missing": "most important missing evidence"
  }
}
"""


def run_evidence_battle(query, chunks):
    # Evidence Battle — AI vs AI Investigation
    if not chunks:
        return {
            "candidate_answer": "",
            "supporter": {"claims": [], "total_claims": 0},
            "skeptic": {"claims": [], "total_claims": 0, "missing_evidence": []},
            "verdict": {
                "decision": "insufficient",
                "reasoning": "No evidence available",
                "supporting_count": 0,
                "counter_count": 0,
                "critical_missing": "All evidence"
            }
        }

    context = "\n\n".join([
        f"[Source: {c['file']}, Page {c.get('page', '?')}]\n{c['text'][:700]}"
        for c in chunks[:8]
    ])

    prompt = f"""Question: {query}

Evidence Pool:
{context}

Perform Evidence Battle:
1. Generate candidate answer
2. Supporter: find supporting evidence
3. Skeptic: find contradicting + missing evidence
4. Reconcile: final verdict"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": EVIDENCE_BATTLE_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {
            "candidate_answer": "",
            "supporter": {"claims": [], "total_claims": 0},
            "skeptic": {"claims": [], "total_claims": 0, "missing_evidence": []},
            "verdict": {
                "decision": "insufficient",
                "reasoning": "Analysis failed",
                "supporting_count": 0,
                "counter_count": 0,
                "critical_missing": "Unknown"
            }
        }