# llm.py
# Groq version — Direct target language

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


LANG_MAP = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "bn": "Bengali",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu"
}


def get_answer(query, chunks, target_lang=None):
    if not chunks:
        return "Cannot determine reliably. No relevant documents found."

    lang_name = LANG_MAP.get(target_lang, "English") if target_lang else "English"

    context_parts = []
    for i, c in enumerate(chunks[:5], 1):
        page = c.get("page", "?")
        context_parts.append(
            f"[Source {i}: {c['file']}, Page {page}]\n{c['text'][:1000]}"
        )
    context = "\n\n".join(context_parts)

    system_prompt = f"""You are TruthLens, a document investigator.

CRITICAL LANGUAGE RULE:
- You MUST answer in {lang_name}.
- Do NOT answer in any other language.

OTHER RULES:
1. Answer ONLY from the provided context.
2. Every answer MUST cite: [Document Name, Page X]
3. If context doesn't have the answer, say: "Cannot determine reliably."
4. NEVER make up information.
5. Be specific — give exact facts.
"""

    prompt = f"""Context:
{context}

Question: {query}

Answer in {lang_name} with citations:"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-oss-20b",
        temperature=0.5,
        max_tokens=1000,
    )

    return chat_completion.choices[0].message.content