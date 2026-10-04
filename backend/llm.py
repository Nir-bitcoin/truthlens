# llm.py
# Kaam: LLM se answer generate karna — exact citations ke saath

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """You are TruthLens, a document investigator.

STRICT RULES:
1. Answer ONLY from the provided context.
2. Every answer MUST cite: [Document Name, Page X]
3. If context doesn't have the answer, say: "Cannot determine reliably."
4. NEVER make up information.
5. If you find conflicting info, list BOTH versions.
6. Answer in the same language as the question.
7. Be concise — max 3 sentences.
"""


def build_prompt(query, chunks):
    # Retrieved chunks ke saath prompt banata hai
    context_parts = []
    for i, c in enumerate(chunks, 1):
        page = c.get("page", "?")
        context_parts.append(
            f"[Source {i}: {c['file']}, Page {page}, Lang: {c['language']}]\n{c['text']}"
        )
    context = "\n\n".join(context_parts)

    return f"""Context:
{context}

Question: {query}

Answer with exact citations [Document, Page X]:"""


def get_answer(query, chunks):
    # LLM se answer leta hai
    if not chunks:
        return "Cannot determine reliably. No relevant documents found."

    prompt = build_prompt(query, chunks)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content