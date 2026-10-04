<div align="center">

# 🔍 TruthLens

### ⚡ *Don't just get answers. Get truth.*

**AI Document Investigator**

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
| [Testing](#-testing) | [Comparison](#-comparison) | [Contributing](#-contributing) | [Roadmap](#-roadmap) |
| | | | [License](#-license) |

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
┌─────────────────────────────────────────────────────────────┐
│ │
│ RETRIEVE → COMPARE → DETECT → DECIDE → ANSWER │
│ │
│ Supporting Evidence + Contradicting Evidence │
│ ↓ │
│ EVIDENCE COMPARISON │
│ ↓ │
│ ✅ AGREE | ⚠️ CONFLICT | 🟡 INSUFFICIENT │
│ │
└─────────────────────────────────────────────────────────────┘

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
| 4 | **Evidence Gap Detector** | Tells what's missing |
| 5 | **Multi-Bhasha** | 11 languages supported |
| 6 | **Evidence Confidence** | Score based on the evidence, not a guessed percentage |
| 7 | **Evidence Chain** | Full proof, traceable |
| 8 | **Hallucination Firewall** | No evidence = No answer |
| 9 | **Cross-Lingual Retrieval** | Hindi question + English docs |
| 10 | **Temporal Truth Engine** | Distinguishes time-based changes from real conflicts |
| 11 | **Source Drift Detection** | Detects changes across document versions |
| 12 | **Claim Dependency Graph** | Visual graph of claims and their evidence |

</div>

> **"Baaki AI answers dete hain. TruthLens batata hai ki answer bharosemand hai ya nahi."**

---

## 🔥 Features

TruthLens has **38 features** in total: 7 core, 12 advanced, 8 technical, and 11 supported languages.

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
| 11 | Evidence Confidence Score | `conflict.py` | ✅ |
| 12 | Evidence Chain | `app.py` | ✅ |
| 13 | Conflict Graph (Plotly) | `graph.py` | ✅ |
| 14 | Hallucination Firewall | `app.py` | ✅ |
| 15 | Empty-State Protection | `app.py` | ✅ |
| 16 | Cross-Lingual Retrieval | `app.py` | ✅ |
| 17 | Auto-Process | `app.py` | ✅ |
| 18 | Claim Extraction | `conflict.py` | ✅ |
| 19 | Answerability Check | `conflict.py` | ✅ |
| 20 | Temporal Truth Engine | `conflict.py` | ✅ |
| 21 | Source Drift Detection | `conflict.py` | ✅ |
| 22 | Claim Dependency Graph | `conflict.py` + `graph.py` | ✅ |

### 🟡 Technical Features

<img src="docs/features-technical.svg" alt="Technical features" width="100%">

| # | Feature | File | Status |
|:---:|:---|:---|:---:|
| 23 | Groq API (fast and free) | `llm.py` | ✅ |
| 24 | openai/gpt-oss-120b model | `llm.py` | ✅ |
| 25 | Strong multilingual embedding model | `embeddings.py` | ✅ |
| 26 | Top-30 retrieval | `app.py` | ✅ |
| 27 | Query translation | `app.py` | ✅ |
| 28 | OCR support (scanned PDFs and images) | `parser.py` | ✅ |
| 29 | Page number preservation | `embeddings.py` | ✅ |
| 30 | Caching | `translator.py` | ✅ |

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
▼ ▼
SUPPORTING COUNTER
EVIDENCE EVIDENCE
│ │
└──────────┬──────────┘
▼
CLAIM EXTRACTION
│
▼
CONFLICT DETECTION
│
┌──────────┴──────────┐
▼ ▼
EVIDENCE GAP EVIDENCE OK
│ │
▼ ▼
WHAT EVIDENCE IS ANSWER + SOURCES
NEEDED? │
│ ▼
│ CONFIDENCE SCORE
│ │
└──────────┬──────────┘
▼
INVESTIGATION
REPORT

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
Access
Open browser: http://localhost:8501

🆓 How to use
Once the app is running, you only need three steps:

Upload one or more documents (PDF, DOCX, TXT, or images).

Ask any question, in any of the 11 supported languages.

Read the answer with its citations, conflicts, and confidence score.

🧪 Testing
Run Automated Tests
bash
python backend/test_truthlens.py
Test Results
#	Test	Status
1	Parser	✅ PASSED
2	Language Detection	✅ PASSED
3	Language Names	✅ PASSED
4	No Evidence	✅ PASSED
5	Strong Evidence	✅ PASSED
6	Conflict Detection	✅ PASSED
7	Confidence Calculation	✅ PASSED
8	Conflict Penalty	✅ PASSED
All 8 tests passing ✅

🎬 Demo
Example outputs (sample documents, numbers are illustrative).

Scenario 1: Normal Question
text
Question: "What is the refund policy?"

Answer: The refund policy allows returns within 30 days of purchase.
[policy.pdf, Page 4]

Evidence Confidence: 92%
Scenario 2: Conflicting Documents
text
Question: "When did employee join?"

⚠️ CONFLICT DETECTED
- contract.txt: January 15, 2024
- hr.txt: January 20, 2024

Answer: Cannot determine reliably.

Evidence Confidence: 31%
🆚 Comparison
<div align="center">
Feature	Basic RAG chatbot	TruthLens
Multi-format	⚠️ Often PDF only	✅ PDF, DOCX, TXT, images
Multi-language	⚠️ Often English-only	✅ 11 languages
Conflict detection	❌	✅ Claim-level
"I don't know"	❌	✅ Honest
Counter-evidence	❌	✅ Active
Evidence confidence	⚠️ Single guessed %	✅ Evidence-based
Evidence chain	❌	✅ Full proof
Hallucination firewall	❌	✅ No evidence = No answer
Temporal analysis	❌	✅ Time-aware
Source drift	❌	✅ Version detection
Claim graph	❌	✅ Visual dependency
</div>
📈 Roadmap
Version	Feature	Status
v1.0	Core Q&A + Citations	✅
v1.1	Conflict Detection	✅
v1.2	Multi-Bhasha	✅
v1.3	Counter-Evidence 2.0	✅
v1.4	Evidence Gap + Resolution	✅
v2.0	Temporal Conflict Detection	✅
v2.1	Claim Dependency Graph	✅
v2.2	Source Drift Detection	✅
👥 Team
<div align="center">
Member	Role
Niranjan vishe	Developer
</div>
🤝 Contributing
Contributions are welcome!

Fork the repository

Create your feature branch (git checkout -b feat/amazing-feature)

Commit your changes (git commit -m 'feat: add amazing feature')

Push to the branch (git push origin feat/amazing-feature)

Open a Pull Request
📄 License
MIT License. See LICENSE for details.

<div align="center">
