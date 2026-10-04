# llm.py
# for: LLM se answer generate karna — citations ke saath

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """You are a document investigator.

RULES:
1. Answer ONLY from the provided context.
2. Always cite source document + page/section.
3. If context is insufficient, say: "Cannot determine reliably."
4. If context has conflicts, highlight them.
5. Never guess or hallucinate.
6. Answer in the same language as the question.
"""


def build_prompt(query, chunks):
    # Retrieved chunks ke saath prompt banata hai
    context = "\n\n".join([
        f"[Source: {c['file']} | Lang: {c['language']}]\n{c['text']}"
        for c in chunks
    ])

    return f"""Context:
{context}

Question: {query}

Answer with citations:"""


def get_answer(query, chunks):
    # LLM se answer leta hai
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


# Test karne ke liye
if __name__ == "__main__":
    from retrieval import retrieve
    chunks = retrieve("When did employee join?")
    answer = get_answer("When did employee join?", chunks)
    print(answer)