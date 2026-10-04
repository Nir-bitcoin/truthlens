# conflict.py
# for: Chunks ke beech contradiction detect karna + answerability check karna

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


CONFLICT_PROMPT = """You are a conflict detector.

Compare the given document chunks and find contradictions.

Return ONLY valid JSON in this format:
{
  "conflict": true/false,
  "pairs": [
    {
      "source_a": "file name",
      "claim_a": "what doc A says",
      "source_b": "file name",
      "claim_b": "what doc B says",
      "explanation": "why they conflict"
    }
  ]
}

If no conflict, return: {"conflict": false, "pairs": []}
"""


def detect_conflict(chunks):
    # Chunks ke beech conflict detect karta hai
    if len(chunks) < 2:
        return {"conflict": False, "pairs": []}

    context = "\n\n".join([
        f"[Source: {c['file']}]\n{c['text']}"
        for c in chunks
    ])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CONFLICT_PROMPT},
            {"role": "user", "content": context}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"conflict": False, "pairs": []}


def check_answerability(chunks, conflict_data):
    # Answerability check karta hai — honest labels
    if conflict_data.get("conflict"):
        return {
            "level": "cannot_determine",
            "label": "Cannot determine reliably",
            "reason": "Conflicting evidence found"
        }

    if len(chunks) >= 3:
        return {
            "level": "strong",
            "label": "Strong evidence",
            "reason": f"{len(chunks)} sources agree"
        }
    elif len(chunks) >= 2:
        return {
            "level": "moderate",
            "label": "Moderate evidence",
            "reason": f"{len(chunks)} sources found"
        }
    else:
        return {
            "level": "weak",
            "label": "Weak evidence",
            "reason": "Only 1 source found"
        }


# Test karne ke liye
if __name__ == "__main__":
    from retrieval import retrieve
    chunks = retrieve("When did employee join?")
    conflict = detect_conflict(chunks)
    answerability = check_answerability(chunks, conflict)
    print(json.dumps(conflict, indent=2))
    print(json.dumps(answerability, indent=2))