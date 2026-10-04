<h1 align="center">🔍 TruthLens</h1>



<p align="center">

&#x20; <b>A document Q\&A tool that shows its evidence, flags conflicts, and says "I don't know" when it should.</b><br>

&#x20; Built for ALGOTHON'26 \&nbsp;|\&nbsp; PS ALG-AI-02 \&nbsp;|\&nbsp; Team 240

</p>



<p align="center">

&#x20; <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=flat-square\&logo=python" alt="Python">

&#x20; <img src="https://img.shields.io/badge/Streamlit-red?style=flat-square\&logo=streamlit" alt="Streamlit">

&#x20; <img src="https://img.shields.io/badge/License-MIT-orange?style=flat-square" alt="MIT">

</p>



```

&#x20;     \_\_\_\_\_\_              \_\_\_\_\_\_              \_\_\_\_\_\_              \_\_\_\_\_\_

&#x20;    /      /|           /      /|           /      /|           /      /|

&#x20;   /\_\_\_\_\_\_/ |          /\_\_\_\_\_\_/ |          /\_\_\_\_\_\_/ |          /\_\_\_\_\_\_/ |

&#x20;   |  ?   | /          |  +-  | /          |  !=  | /          |  ok  | /

&#x20;   |\_\_\_\_\_\_|/           |\_\_\_\_\_\_|/           |\_\_\_\_\_\_|/           |\_\_\_\_\_\_|/

&#x20;       Ask               Retrieve            Compare              Answer

```



\---



\## The problem



Important information usually sits in many files: PDFs, scanned images, text documents, often in different languages. Normal AI chatbots can read them, but they have a few habits that make them hard to trust:



\- They answer confidently even when the documents don't say that.

\- They don't show where the answer came from.

\- They don't notice when two documents disagree.

\- They almost never say "I don't know".

\- Most of them work well only in English.



So people end up reading everything by hand anyway.



\## What TruthLens does



You upload your documents and ask a question. Before answering, TruthLens:



1\. Looks for evidence that supports an answer.

2\. Looks for evidence that goes against it.

3\. Checks whether different documents contradict each other.

4\. Checks whether the evidence is actually enough to answer.

5\. If it isn't, tells you what is missing and what would settle the question.



If the evidence is solid, you get the answer with the file name and page number. If documents conflict, it shows you both sides instead of picking one. If there is no evidence, it says so.



\---



\## Features



TruthLens has 39 features in total: 7 core, 13 advanced, 8 technical, and 11 supported languages.



\### Core features



```

&#x20;     \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_

&#x20;    /      /|         /      /|         /      /|         /      /|

&#x20;   /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |

&#x20;   |  01  | /        |  02  | /        |  03  | /        |  04  | /

&#x20;   |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/

&#x20;  Multi-format     Multi-document   Extract + index   Natural-lang Q\&A



&#x20;     \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_

&#x20;    /      /|         /      /|         /      /|

&#x20;   /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |

&#x20;   |  05  | /        |  06  | /        |  07  | /

&#x20;   |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/

&#x20;Source citations  Conflict detect     Uncertainty

```



| # | Feature | Where |

|---|---------|-------|

| 1 | Multi-format upload (PDF, DOCX, TXT, PNG, JPG) | `parser.py` |

| 2 | Multi-document support (3+ files) | `app.py` |

| 3 | Extraction + indexing (embeddings + FAISS) | `embeddings.py` |

| 4 | Natural-language Q\&A | `llm.py` |

| 5 | Source citations (file + page) | `llm.py` |

| 6 | Conflict detection (claim-level) | `conflict.py` |

| 7 | Uncertainty handling ("I don't know") | `conflict.py` |



\### Advanced features



```

&#x20;     \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_

&#x20;    /      /|         /      /|         /      /|         /      /|

&#x20;   /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |

&#x20;   |  08  | /        |  09  | /        |  10  | /        |  11  | /

&#x20;   |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/

&#x20;Counter-Evidence    Evidence Gap    Resolution Evid.  Evidence Battle



&#x20;     \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_

&#x20;    /      /|         /      /|         /      /|         /      /|

&#x20;   /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |

&#x20;   |  12  | /        |  13  | /        |  14  | /        |  15  | /

&#x20;   |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/

&#x20;Confidence Score   Evidence Chain    Conflict Graph   Halluc. Firewall



&#x20;     \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_

&#x20;    /      /|         /      /|         /      /|         /      /|

&#x20;   /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |

&#x20;   |  16  | /        |  17  | /        |  18  | /        |  19  | /

&#x20;   |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/

Empty-State Guard   Cross-Lingual      Auto-Process    Claim Extraction



&#x20;     \_\_\_\_\_\_

&#x20;    /      /|

&#x20;   /\_\_\_\_\_\_/ |

&#x20;   |  20  | /

&#x20;   |\_\_\_\_\_\_|/

&#x20; Answerability

```



| # | Feature | Where |

|---|---------|-------|

| 8 | Counter-Evidence 2.0 (supporting + contradicting) | `conflict.py` |

| 9 | Evidence Gap Detector | `conflict.py` |

| 10 | Resolution Evidence ("what would resolve this?") | `conflict.py` |

| 11 | Evidence Battle (AI vs AI) | `conflict.py` |

| 12 | Evidence Confidence Score | `conflict.py` |

| 13 | Evidence Chain | `app.py` |

| 14 | Conflict Graph (Plotly) | `graph.py` |

| 15 | Hallucination Firewall (no evidence, no answer) | `app.py` |

| 16 | Empty-State Protection | `app.py` |

| 17 | Cross-Lingual Retrieval | `app.py` |

| 18 | Auto-Process | `app.py` |

| 19 | Claim Extraction | `conflict.py` |

| 20 | Answerability Check | `conflict.py` |



\### Technical features



```

&#x20;     \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_

&#x20;    /      /|         /      /|         /      /|         /      /|

&#x20;   /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |

&#x20;   |  21  | /        |  22  | /        |  23  | /        |  24  | /

&#x20;   |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/

&#x20;    Groq API        gpt-oss-120b   Strong embeddings  Top-30 retrieval



&#x20;     \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_

&#x20;    /      /|         /      /|         /      /|         /      /|

&#x20;   /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |

&#x20;   |  25  | /        |  26  | /        |  27  | /        |  28  | /

&#x20;   |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/

&#x20;Query translate     OCR support       Page numbers        Caching

```



| # | Feature | Where |

|---|---------|-------|

| 21 | Groq API (fast and free) | `llm.py` |

| 22 | openai/gpt-oss-120b model | `llm.py` |

| 23 | Strong multilingual embedding model | `embeddings.py` |

| 24 | Top-30 retrieval | `app.py` |

| 25 | Query translation | `app.py` |

| 26 | OCR support (scanned PDFs and images) | `parser.py` |

| 27 | Page number preservation | `embeddings.py` |

| 28 | Caching | `translator.py` |



\---



\## Languages



You can ask in one language and search documents written in another. For example, a Hindi question can find its answer in an English document.



```

&#x20;     \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_

&#x20;    /      /|         /      /|         /      /|         /      /|

&#x20;   /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |

&#x20;   |  en  | /        |  hi  | /        |  mr  | /        |  ta  | /

&#x20;   |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/

&#x20;    English            Hindi            Marathi            Tamil



&#x20;     \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_

&#x20;    /      /|         /      /|         /      /|         /      /|

&#x20;   /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |

&#x20;   |  bn  | /        |  te  | /        |  gu  | /        |  kn  | /

&#x20;   |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/

&#x20;    Bengali            Telugu           Gujarati          Kannada



&#x20;     \_\_\_\_\_\_            \_\_\_\_\_\_            \_\_\_\_\_\_

&#x20;    /      /|         /      /|         /      /|

&#x20;   /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |        /\_\_\_\_\_\_/ |

&#x20;   |  ml  | /        |  pa  | /        |  ur  | /

&#x20;   |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/         |\_\_\_\_\_\_|/

&#x20;   Malayalam          Punjabi             Urdu

```



\---



\## How it works



```

Question

&#x20;  ↓

Detect language

&#x20;  ↓

Search documents (multilingual embeddings)

&#x20;  ↓

Collect supporting evidence + counter evidence

&#x20;  ↓

Extract claims → check for conflicts

&#x20;  ↓

Enough evidence?

&#x20;  ├── Yes → Answer + sources + confidence score

&#x20;  └── No  → "Can't answer" + what's missing

```



\*\*Evidence Battle\*\*



```

Candidate answer

&#x20;  ├── Supporter: "why this could be true"

&#x20;  └── Skeptic:   "why this could be false"

&#x20;             ↓

&#x20;  Verdict: Agree / Conflict / Insufficient

```



The confidence score depends on how much evidence there is, how well it matches the question, and whether any documents disagree. A conflict lowers the score.



\---



\## Tech stack



| Part | What we used |

|------|--------------|

| Frontend | Streamlit |

| Backend | Python |

| Embeddings | LaBSE (multilingual) |

| Vector search | FAISS |

| LLM | Groq (openai/gpt-oss-120b) |

| Translation | deep-translator |

| Charts | Plotly |

| OCR | Tesseract |

| Database | SQLite |



\---



\## Running it



You need Python 3.10+ and a Groq API key (free at https://console.groq.com/keys).



```bash

git clone https://github.com/Nir-bitcoin/truthlens.git

cd truthlens



python -m venv venv

venv\\Scripts\\activate        # Windows

source venv/bin/activate     # Mac/Linux



pip install -r requirements.txt



echo "GROQ\_API\_KEY=your\_key\_here" > .env



streamlit run app.py

```



Then open http://localhost:8501



\---



\## Tests



```bash

python backend/test\_truthlens.py

```



The test file has 8 checks, and all of them pass right now: parser, language detection, language names, no-evidence case, strong-evidence case, conflict detection, confidence calculation, and conflict penalty.



\---



\## Examples



\*\*1. Normal question\*\*



```

Q: What is the judging criteria?



A: Functionality \& Completion (30%), Technical Implementation (20%),

&#x20;  Innovation \& Problem Understanding (20%), User Experience /

&#x20;  Presentation (15%), Testing, Edge Cases \& Reliability (15%).

&#x20;  \[ALGOTHON26\_All\_12\_Problem\_Statements\_with\_PSID.pdf, Page 40]



Confidence: 65%

```



\*\*2. Documents disagree\*\*



```

Q: When did the employee join?



⚠️ Conflict found

\- contract.txt: January 15, 2024

\- hr.txt: January 20, 2024



A: Can't say for sure, the two documents give different dates.

Confidence: 31%

```



\*\*3. Evidence Battle\*\*



```

Q: Was the employee eligible for promotion?



For:                          Against:

\- Performance score 91%       - Policy asks for 5 years

\- Manager recommended         - No approval found



Verdict: Insufficient

Missing: manager approval record

```



\---



\## Team 240



| Name | Role |

|------|------|

| \[Your name] | Developer |

| \[Teammate's name] | Developer |



\## License



MIT, see \[LICENSE](LICENSE).

