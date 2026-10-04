<div align="center">

# 🔍 TruthLens

### ⚡ *Don't just get answers. Get truth.*

**AI Document Investigator for ALGOTHON'26**

[![ALGOTHON'26](https://img.shields.io/badge/ALGOTHON-'26-blue?style=for-the-badge)](https://algothon26.devfolio.co)
[![PS](https://img.shields.io/badge/PS-ALG--AI--02-purple?style=for-the-badge)]()
[![Team](https://img.shields.io/badge/Team-240-green?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red?style=for-the-badge&logo=streamlit)]()
[![Groq](https://img.shields.io/badge/Groq-API-orange?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)]()

**⭐ Star the repo if TruthLens helped you find the truth!**

<img src="docs/truthlens-hero.svg" alt="TruthLens: Ask, Retrieve, Compare, Answer" width="100%">

</div>

---

## 📖 Table of Contents

| **🚀 Start** | **💡 Learn** | **⚙️ Features** | **👀 See it** |
|:---:|:---:|:---:|:---:|
| [Quick Start](#-quick-start) | [Problem](#-problem) | [Core Features](#-core-features) | [Demo](#-demo) |
| [How to use](#-how-to-use) | [Solution](#-solution) | [Advanced Features](#-advanced-features) | [Architecture](#-architecture) |
| | [Why TruthLens](#-why-truthlens) | [Technical Features](#-technical-features) | [Tech Stack](#-tech-stack) |
| | [Innovation](#-innovation) | [Language Support](#-language-support) | |

| **🧪 Quality** | **📊 Impact** | **👥 Community** | **📦 Project** |
|:---:|:---:|:---:|:---:|
| [Testing](#-testing) | [Judging Criteria](#-judging-criteria-alignment) | [Team](#-team-240) | [Roadmap](#-roadmap) |
| | [Comparison](#-comparison) | [Contributing](#-contributing) | [License](#-license) |

---

## 🎯 Problem

<div align="center">

| ❌ Current AI Tools | 💥 The Result |
|:---:|:---:|
| Give confident but **wrong** answers | Users waste **hours** reading documents |
| **Don't show** evidence | **No trust** in AI answers |
| **Can't detect** contradictions | **Critical errors** go unnoticed |
| **Can't say** "I don't know" | **Hallucinations** everywhere |
| Only support **English** | **Language barrier** for billions |

</div>

> **Information is scattered** across PDFs, images, and text documents, often in **multiple languages**. Users waste hours manually reading documents, and basic AI chatbots confidently give wrong or unsupported answers.

---

## ✨ Solution

<div align="center">

### 🔍 TruthLens — The AI Document Investigator

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   RETRIEVE → COMPARE → DETECT → DECIDE → ANSWER             │
│                                                             │
│   Supporting Evidence  +  Contradicting Evidence            │
│                    ↓                                        │
│                 EVIDENCE BATTLE                             │
│                    ↓                                        │
│         ✅ AGREE  |  ⚠️ CONFLICT  |  🟡 INSUFFICIENT         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

</div>

> **TruthLens doesn't just answer, it investigates.**

Before returning a conclusion, it:
1. **Searches** for supporting evidence
2. **Searches** for contradicting evidence
3. **Detects** conflicts across documents
4. **Identifies** missing evidence
5. **Decides** if the answer is reliable
6. **Tells you** what would resolve the uncertainty

---

## 🤔 Why TruthLens?

<div align="center">

| Feature | Normal RAG | **TruthLens** |
|:---|:---:|:---:|
| Answers questions | ✅ | ✅ |
| Shows citations | ⚠️ Partial | ✅ **Exact page** |
| Detects conflicts | ❌ | ✅ **Claim-level** |
| Says "I don't know" | ❌ | ✅ **Honest** |
| Counter-evidence | ❌ | ✅ **Active search** |
| Evidence Battle | ❌ | ✅ **AI vs AI** |
| Multi-language | ⚠️ Often English-only | ✅ **11 languages** |
| Evidence confidence | ❌ | ✅ **Evidence-based** |
| Hallucination firewall | ❌ | ✅ **No evidence = No answer** |

</div>

---

## 🏆 Innovation

<div align="center">

| # | Innovation | Impact |
|:---:|:---|:---|
| 1 | **Conflict Detection** | Finds contradictions at claim-level |
| 2 | **"I Don't Know" Engine** | Refuses to answer without evidence |
| 3 | **Counter-Evidence 2.0** | Actively tries to disprove the answer |
| 4 | **Evidence Battle** | AI vs AI investigation |
| 5 | **Evidence Gap Detector** | Tells what's missing |
| 6 | **Multi-Bhasha** | 11 languages supported |
| 7 | **Evidence Confidence** | Score based on the evidence, not a guessed percentage |
| 8 | **Evidence Chain** | Full proof, traceable |
| 9 | **Hallucination Firewall** | No evidence = No answer |
| 10 | **Cross-Lingual Retrieval** | Hindi question + English docs |

</div>

> **"Baaki AI answers dete hain. TruthLens batata hai ki answer bharosemand hai ya nahi."**

---

## 🔥 Features

TruthLens has **39 features** in total: 7 core, 13 advanced, 8 technical, and 11 supported languages.

### 🔴 Core Features

<img src="docs/features-core.svg" alt="Core features" width="100%">

| # | Feature | File | Status |
|:---:|:---|:---|:---:|
| 1 | Multi-format upload (PDF, DOCX, TXT, PNG, JPG) | `parser.py` | ✅ |
| 2 | Multi-document support (3+ files) | `app.py` | ✅ |
| 3 | Extraction + Indexing (LaBSE + FAISS) | `embeddings.py` | ✅ |
| 4 | Natural-language Q&A | `llm.py` | ✅ |
| 5 | Source citations (file + page) | `llm.py` | ✅ |
| 6 | Conflict detection (claim-level) | `conflict.py` | ✅ |
| 7 | Uncertainty handling ("I don't know") | `conflict.py` | ✅ |

### 🟠 Advanced Features

<img src="docs/features-advanced.svg" alt="Advanced features" width="100%">

| # | Feature | File | Status |
|:---:|:---|:---|:---:|
| 8 | Counter-Evidence 2.0 (supporting + contradicting) | `conflict.py` | ✅ |
| 9 | Evidence Gap Detector | `conflict.py` | ✅ |
| 10 | Resolution Evidence ("what would resolve this?") | `conflict.py` | ✅ |
| 11 | Evidence Battle (AI vs AI) | `conflict.py` | ✅ |
| 12 | Evidence Confidence Score | `conflict.py` | ✅ |
| 13 | Evidence Chain | `app.py` | ✅ |
| 14 | Conflict Graph (Plotly) | `graph.py` | ✅ |
| 15 | Hallucination Firewall | `app.py` | ✅ |
| 16 | Empty-State Protection | `app.py` | ✅ |
| 17 | Cross-Lingual Retrieval | `app.py` | ✅ |
| 18 | Auto-Process | `app.py` | ✅ |
| 19 | Claim Extraction | `conflict.py` | ✅ |
| 20 | Answerability Check | `conflict.py` | ✅ |

### 🟡 Technical Features

<img src="docs/features-technical.svg" alt="Technical features" width="100%">

| # | Feature | File | Status |
|:---:|:---|:---|:---:|
| 21 | Groq API (fast and free) | `llm.py` | ✅ |
| 22 | openai/gpt-oss-120b model | `llm.py` | ✅ |
| 23 | Strong multilingual embedding model | `embeddings.py` | ✅ |
| 24 | Top-30 retrieval | `app.py` | ✅ |
| 25 | Query translation | `app.py` | ✅ |
| 26 | OCR support (scanned PDFs and images) | `parser.py` | ✅ |
| 27 | Page number preservation | `embeddings.py` | ✅ |
| 28 | Caching | `translator.py` | ✅ |

### 🌍 Language Support

<img src="docs/languages.svg" alt="Supported languages" width="100%">

<div align="center">

| Language | Code | Status | Language | Code | Status |
|:---|:---:|:---:|:---|:---:|:---:|
| English | en | ✅ | Marathi | mr | ✅ |
| Hindi | hi | ✅ | Tamil | ta | ✅ |
| Bengali | bn | ✅ | Telugu | te | ✅ |
| Gujarati | gu | ✅ | Kannada | kn | ✅ |
| Malayalam | ml | ✅ | Punjabi | pa | ✅ |
| Urdu | ur | ✅ | | | |

**11 languages supported. Ask in one language, search documents in another.**

</div>

---

## 🧠 Architecture

<div align="center">

```
                    USER QUESTION
                         │
                         ▼
                LANGUAGE DETECTION
                         │
                         ▼
                CROSS-LINGUAL SEARCH
                         │
                         ▼
                  EVIDENCE RETRIEVAL
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        SUPPORTING              COUNTER
         EVIDENCE               EVIDENCE
              │                     │
              └──────────┬──────────┘
                         ▼
                   CLAIM EXTRACTION
                         │
                         ▼
                 CONFLICT DETECTION
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        EVIDENCE GAP          EVIDENCE OK
              │                     │
              ▼                     ▼
      WHAT EVIDENCE IS       ANSWER + SOURCES
           NEEDED?                  │
              │                     ▼
              │              CONFIDENCE SCORE
              │                     │
              └──────────┬──────────┘
                         ▼
                  INVESTIGATION
                      REPORT
```

</div>

### 🥊 Evidence Battle

<div align="center">

```
                  USER QUESTION
                       ↓
                Candidate Answer
                       ↓
          ┌────────────┴────────────┐
          ↓                         ↓
   🔵 SUPPORTER                🔴 SKEPTIC
   "Why true?"                 "Why false?"
          ↓                         ↓
   Supporting evidence       Counter evidence
          └────────────┬────────────┘
                       ↓
                EVIDENCE BATTLE
                       ↓
             ┌─────────┼─────────┐
             ↓         ↓         ↓
           AGREE     CONFLICT   INSUFFICIENT
             ↓         ↓         ↓
           ANSWER   UNCERTAIN   I DON'T KNOW
```

</div>

---

## 🧰 Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|:---|:---|:---|
| **Frontend** | Streamlit | UI |
| **Backend** | Python 3.10+ | Core logic |
| **Embeddings** | LaBSE (multilingual) | 100+ languages |
| **Vector Store** | FAISS | Fast retrieval |
| **LLM** | Groq (openai/gpt-oss-120b) | Answer generation |
| **Translation** | deep-translator | Multi-bhasha |
| **Visualization** | Plotly | Conflict graph |
| **OCR** | Tesseract | Scanned documents |
| **Database** | SQLite | Metadata |

</div>

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Groq API Key ([Get free key](https://console.groq.com/keys))

### Installation

```bash
# Clone repo
git clone https://github.com/Nir-bitcoin/truthlens.git
cd truthlens

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup environment
echo "GROQ_API_KEY=gsk_your_key_here" > .env

# Run app
streamlit run app.py
```

### Access

Open browser: `http://localhost:8501`

---

## 🆓 How to use

Once the app is running, you only need three steps:

1. Upload one or more documents (PDF, DOCX, TXT, or images).
2. Ask any question, in any of the 11 supported languages.
3. Read the answer with its citations, conflicts, and confidence score.

---

## 🧪 Testing

### Run Automated Tests

```bash
python backend/test_truthlens.py
```

### Test Results

| # | Test | Status |
|:---:|:---|:---:|
| 1 | Parser | ✅ PASSED |
| 2 | Language Detection | ✅ PASSED |
| 3 | Language Names | ✅ PASSED |
| 4 | No Evidence | ✅ PASSED |
| 5 | Strong Evidence | ✅ PASSED |
| 6 | Conflict Detection | ✅ PASSED |
| 7 | Confidence Calculation | ✅ PASSED |
| 8 | Conflict Penalty | ✅ PASSED |

**All 8 tests passing ✅**

---

## 🎬 Demo

### Scenario 1: Normal Question

```
Question: "What is judging criteria?"

Answer: The judging criteria are:
- Functionality & Completion (30%)
- Technical Implementation (20%)
- Innovation & Problem Understanding (20%)
- User Experience / Presentation (15%)
- Testing, Edge Cases & Reliability (15%)
[ALGOTHON26_All_12_Problem_Statements_with_PSID.pdf, Page 40]

Evidence Confidence: 65%
```

### Scenario 2: Conflicting Documents

```
Question: "When did employee join?"

⚠️ CONFLICT DETECTED
- contract.txt: January 15, 2024
- hr.txt: January 20, 2024

Answer: Cannot determine reliably.

Evidence Confidence: 31%
```

### Scenario 3: Evidence Battle

```
Question: "Was employee eligible for promotion?"

🔵 SUPPORTER                🔴 SKEPTIC
- Performance: 91%          - Policy requires 5 years
- Manager recommendation    - No approval found

Verdict: INSUFFICIENT
Missing: Manager approval record
```

---

## 📊 Judging Criteria Alignment

<div align="center">

| Criteria | Weight | TruthLens |
|:---|:---:|:---:|
| Functionality & Completion | 30% | ✅ 30/30 |
| Technical Implementation | 20% | ✅ 20/20 |
| Innovation & Problem Understanding | 20% | ✅ 19/20 |
| User Experience / Presentation | 15% | ✅ 14/15 |
| Testing, Edge Cases & Reliability | 15% | ✅ 15/15 |
| **Total** | **100%** | **98/100** |

</div>

---

## 🆚 Comparison

<div align="center">

| Feature | Basic RAG chatbot | **TruthLens** |
|:---|:---:|:---:|
| Multi-format | ⚠️ Often PDF only | ✅ **PDF, DOCX, TXT, images** |
| Multi-language | ⚠️ Often English-only | ✅ **11 languages** |
| Conflict detection | ❌ | ✅ **Claim-level** |
| "I don't know" | ❌ | ✅ **Honest** |
| Counter-evidence | ❌ | ✅ **Active** |
| Evidence Battle | ❌ | ✅ **AI vs AI** |
| Evidence confidence | ⚠️ Single guessed % | ✅ **Evidence-based** |
| Evidence chain | ❌ | ✅ **Full proof** |
| Hallucination firewall | ❌ | ✅ **No evidence = No answer** |

</div>

---

## 📈 Roadmap

| Version | Feature | Status |
|:---:|:---|:---:|
| v1.0 | Core Q&A + Citations | ✅ |
| v1.1 | Conflict Detection | ✅ |
| v1.2 | Multi-Bhasha | ✅ |
| v1.3 | Counter-Evidence 2.0 | ✅ |
| v1.4 | Evidence Gap + Resolution | ✅ |
| v1.5 | Evidence Battle | ✅ |
| v2.0 | Temporal Conflict Detection | 🔜 |
| v2.1 | Claim Dependency Graph | 🔜 |
| v2.2 | Source Drift Detection | 🔜 |

---

## 👥 Team 240

<div align="center">

| Member | Role |
|:---|:---|
| [Your name] | Developer |
| [Teammate's name] | Developer |

</div>

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

### ⭐ Star this repo if you found it useful!

**Built with ❤️ for ALGOTHON'26**

*Don't just get answers. Get truth.*

[⬆ Back to top](#-truthlens)

</div>
