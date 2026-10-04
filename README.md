Absolutely. Below is the **complete, judge-focused `README.md`** for TruthLens, ready to copy-paste directly into GitHub.

````markdown
<div align="center">

# 🔍 TruthLens

### *Don't just get answers. Get truth.*

**AI Document Investigator**

Upload documents. Ask questions. Compare evidence. Detect conflicts. Know when the evidence is not enough.

<br>

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![FAISS](https://img.shields.io/badge/Search-FAISS-green)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)
![OCR](https://img.shields.io/badge/OCR-Tesseract-purple)
![License](https://img.shields.io/badge/License-MIT-black)

</div>

---

# 🧠 The Problem

Organizations rarely keep information in one clean document.

Important facts can be scattered across:

- 📄 PDFs
- 📝 DOCX files
- 📃 Text files
- 🖼️ Scanned documents
- 📧 Reports and emails
- 🌐 Documents written in different languages

Traditional document Q&A systems can retrieve relevant text and generate an answer.

But there is a bigger problem:

> **What happens when the documents disagree?**

For example:

**HR Document**

> Employee joining date: January 15, 2024

**Manager Email**

> Employee joined on January 20, 2024

A normal RAG system may simply select one piece of evidence and confidently answer.

That can be dangerous.

TruthLens approaches the problem differently.

---

# 🎯 Our Solution

## TruthLens — AI Document Investigator

TruthLens doesn't just search for evidence supporting an answer.

It investigates the available evidence.

### Investigation Pipeline

```text
                    USER QUESTION
                          │
                          ▼
                  LANGUAGE DETECTION
                          │
                          ▼
                 QUERY UNDERSTANDING
                          │
                          ▼
                 CROSS-LINGUAL SEARCH
                          │
                          ▼
                 EVIDENCE RETRIEVAL
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
        SUPPORTING EVIDENCE   COUNTER EVIDENCE
                │                   │
                └─────────┬─────────┘
                          ▼
                  CLAIM EXTRACTION
                          │
                          ▼
                  CONFLICT DETECTION
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
          EVIDENCE SUFFICIENT   EVIDENCE MISSING
                │                   │
                ▼                   ▼
             ANSWER          UNCERTAIN / I DON'T KNOW
                │
                ▼
          SOURCES + CITATIONS
                │
                ▼
        EVIDENCE CONFIDENCE
````

The goal is not to make the AI sound confident.

The goal is to make the answer **evidence-aware**.

---

# 🚀 What Makes TruthLens Different?

| Capability                | Traditional RAG | TruthLens |
| ------------------------- | --------------: | --------: |
| Multiple documents        |               ✅ |         ✅ |
| Natural-language Q&A      |               ✅ |         ✅ |
| Source citations          |       Sometimes |         ✅ |
| Page-level references     |       Sometimes |         ✅ |
| Multilingual queries      |         Limited |         ✅ |
| Cross-lingual retrieval   |         Limited |         ✅ |
| Conflict detection        |               ❌ |         ✅ |
| Counter-evidence search   |               ❌ |         ✅ |
| Evidence gap detection    |               ❌ |         ✅ |
| "I don't know" behavior   |         Limited |         ✅ |
| Evidence confidence       |         Limited |         ✅ |
| Evidence chain            |               ❌ |         ✅ |
| Conflict graph            |               ❌ |         ✅ |
| Temporal reasoning        |               ❌ |         ✅ |
| Source drift analysis     |               ❌ |         ✅ |
| Claim dependency analysis |               ❌ |         ✅ |
| Evidence-gated answering  |         Limited |         ✅ |

---

# ⭐ Key Innovation

## TruthLens does not only ask:

> "What evidence supports this answer?"

It also asks:

> "What evidence could contradict it?"

And when the evidence is insufficient:

> **"What evidence is missing?"**

This creates an investigation workflow instead of a simple question-answering workflow.

---

# 🔥 Core Features

## 1. 📂 Multi-Format Documents

TruthLens supports investigation across multiple document formats:

* PDF
* DOCX
* TXT
* PNG
* JPG

Scanned documents can be processed using OCR.

---

## 2. 📚 Multi-Document Investigation

Users can upload multiple documents into the same investigation session.

TruthLens searches across the entire document collection rather than treating each file independently.

---

## 3. 🔎 Semantic Evidence Retrieval

Documents are:

1. Extracted
2. Cleaned
3. Chunked
4. Embedded
5. Indexed
6. Retrieved using semantic similarity

The system uses multilingual embeddings with FAISS for efficient evidence retrieval.

---

## 4. 🌍 Cross-Lingual Retrieval

A user can ask a question in one language while relevant evidence exists in another.

For example:

```text
Question:
कर्मचारी की joining date क्या है?

Document:
Employee Start Date: January 15, 2024
```

TruthLens can retrieve relevant evidence across supported languages.

---

# 🌐 Supported Languages

TruthLens currently supports:

| Language  | Code |
| --------- | ---- |
| English   | `en` |
| Hindi     | `hi` |
| Marathi   | `mr` |
| Tamil     | `ta` |
| Bengali   | `bn` |
| Telugu    | `te` |
| Gujarati  | `gu` |
| Kannada   | `kn` |
| Malayalam | `ml` |
| Punjabi   | `pa` |
| Urdu      | `ur` |

---

# ⚔️ Claim-Level Conflict Detection

Not every difference between two documents is a contradiction.

TruthLens attempts to compare claims based on:

* Entity
* Attribute
* Value
* Context
* Time

For example:

```text
Employee salary in 2024 = ₹8 LPA
Employee salary in 2025 = ₹9 LPA
```

This is not automatically treated as a contradiction.

However:

```text
Joining Date = 15 January 2024

Joining Date = 20 January 2024
```

represents a potential conflict because the same attribute has incompatible values.

---

# 🛡️ Evidence-Gated Answering

TruthLens uses an evidence-first workflow.

```text
Question
   │
   ▼
Retrieve Evidence
   │
   ├── No useful evidence
   │          │
   │          ▼
   │      I DON'T KNOW
   │
   └── Evidence found
              │
              ▼
       Check sufficiency
              │
        ┌─────┴─────┐
        ▼           ▼
   Sufficient    Insufficient
        │           │
        ▼           ▼
      Answer     Uncertain /
                 I DON'T KNOW
```

The system is designed to avoid generating a confident answer when the available evidence is insufficient.

---

# 🔥 Counter-Evidence Search

Most retrieval systems focus primarily on finding evidence that supports a candidate answer.

TruthLens explicitly searches for evidence that may challenge the candidate answer.

### Example

Question:

> Was the employee eligible for promotion?

### Supporting evidence

```text
Performance Score: 91%

Manager Recommendation: Positive
```

### Counter evidence

```text
Promotion policy requires 5 years of service.
Employee service record shows 3 years.
```

TruthLens can surface both sides instead of presenting only the supporting evidence.

---

# 🕳️ Evidence Gap Detection

Sometimes the documents contain related information but still do not contain enough evidence to reach a reliable conclusion.

TruthLens identifies this situation as an **Evidence Gap**.

Example:

```text
Available:
✓ Performance score
✓ Service duration
✓ Manager recommendation

Missing:
? Required approval record
```

Instead of inventing the missing information, the system communicates that additional evidence is needed.

---

# 🧩 Resolution Evidence

When evidence conflicts or is insufficient, TruthLens can identify what type of additional evidence could help resolve the investigation.

Example:

```text
Conflict:
Joining date differs between two records.

Potential resolution evidence:
• Official HR joining record
• Signed employment agreement
• Payroll onboarding record
```

This turns the system from a simple answer generator into an investigation assistant.

---

# ⚔️ Evidence Battle

TruthLens can evaluate a claim from two perspectives.

### 🟢 Supporter

> Why is this claim true?

### 🔴 Skeptic

> Why might this claim be false?

The system compares:

```text
Supporting Evidence
        VS
Counter Evidence
        │
        ▼
   Final Assessment
```

Possible outcomes include:

* `AGREE`
* `CONFLICT`
* `INSUFFICIENT`

This helps reduce one-sided evidence selection.

---

# 📊 Evidence Confidence

TruthLens provides an **Evidence Confidence / Evidence Score** based on factors such as:

* Evidence relevance
* Evidence coverage
* Agreement between sources
* Contradicting evidence
* Missing evidence

The score is intended as an evidence-quality indicator.

It is **not presented as an objective probability that an answer is true**.

Example:

```text
Evidence Confidence
██████████████░░░░ 72%

Evidence Strength: MODERATE

Supporting Sources: 4
Counter Sources: 1
Conflicts: 1
```

---

# 🔗 Evidence Chain

TruthLens can show how the final answer was derived.

```text
Question
   ↓
Retrieved Evidence
   ↓
Claims
   ↓
Supporting / Counter Evidence
   ↓
Conflict Analysis
   ↓
Evidence Sufficiency
   ↓
Final Answer
```

This provides an investigation trail instead of only showing the final response.

---

# 🕸️ Conflict Graph

Conflicting claims can be visualized as a graph.

Example:

```text
          ┌───────────────────┐
          │ HR Document       │
          │ Jan 15, 2024      │
          └─────────┬─────────┘
                    │
                 CONFLICT
                    │
                    ▼
          ┌───────────────────┐
          │ Manager Email     │
          │ Jan 20, 2024      │
          └───────────────────┘
```

This helps investigators quickly understand relationships between documents and claims.

---

# ⏳ Temporal Truth Analysis

Information can change over time.

TruthLens considers temporal context when evaluating claims.

Example:

```text
Salary:
2024 → ₹8 LPA
2025 → ₹9 LPA
```

Rather than treating every changed value as a contradiction, the system can consider the time associated with the claim.

---

# 🔄 Source Drift Detection

Documents can become outdated as policies, values, or records change.

TruthLens includes source-drift analysis to help identify cases where information may have changed across documents or over time.

---

# 🧠 Claim Dependency Graph

Some claims depend on other claims.

Example:

```text
Promotion Eligibility
        │
        ├── Service Duration
        │
        ├── Performance Score
        │
        └── Required Approval
```

If an important dependency is missing, the final conclusion may remain uncertain.

---

# 🛠️ Technical Architecture

```text
                    ┌──────────────────┐
                    │   Streamlit UI   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Document Parser  │
                    │ PDF/DOCX/TXT/OCR │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Chunking +       │
                    │ Metadata         │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Multilingual     │
                    │ Embeddings       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ FAISS Vector     │
                    │ Index            │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Top-K Retrieval  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Supporting      Counter          Missing
         Evidence       Evidence         Evidence
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌──────────────────┐
                    │ Claim Extraction │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Conflict Engine  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Evidence /       │
                    │ Answerability    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Groq LLM         │
                    │ GPT-OSS-120B     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Answer + Sources │
                    │ + Confidence     │
                    └──────────────────┘
```

---

# 🧰 Technology Stack

## Frontend

* Streamlit

## Programming

* Python

## Document Processing

* PDF parsing
* DOCX parsing
* TXT processing
* OCR
* Tesseract

## Retrieval

* Multilingual embeddings
* FAISS
* Top-K semantic retrieval

## LLM

* Groq API
* `openai/gpt-oss-120b`

## Translation / Language

* Language detection
* Cross-lingual query processing
* Translation support

## Visualization

* Plotly
* NetworkX

## Storage / Utilities

* SQLite
* Local caching

---

# 📁 Project Structure

```text
truthlens/
│
├── app.py
│
├── backend/
│   ├── parser.py
│   ├── embeddings.py
│   ├── retrieval.py
│   ├── llm.py
│   ├── conflict.py
│   └── translator.py
│
├── utils/
│   └── graph.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/Nir-bitcoin/truthlens.git
cd truthlens
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 API Configuration

TruthLens uses the Groq API for LLM-based reasoning.

Create an environment variable:

```text
GROQ_API_KEY=your_api_key_here
```

Do not commit API keys to GitHub.

Recommended:

```text
.env
```

and add it to `.gitignore`.

---

# ▶️ Run TruthLens

Start the application:

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

---

# 🧪 How To Use

### Step 1 — Upload Documents

Upload one or more:

```text
PDF
DOCX
TXT
PNG
JPG
```

---

### Step 2 — Process Documents

TruthLens extracts the content, creates chunks, generates embeddings and builds the searchable evidence index.

---

### Step 3 — Ask a Question

Ask naturally.

Example:

```text
What is the employee's joining date?
```

Or:

```text
कर्मचारी ने कब जॉइन किया?
```

---

### Step 4 — Investigate

TruthLens retrieves relevant evidence and searches for:

* Supporting claims
* Contradicting claims
* Missing evidence
* Related claims
* Temporal context

---

### Step 5 — Review the Result

The investigation can show:

```text
Verdict
Answer
Evidence Confidence
Supporting Evidence
Counter Evidence
Conflicts
Evidence Chain
Citations
Missing Evidence
```

---

# 🎬 Example Investigation

Suppose three documents contain:

### `contract.txt`

```text
Employee joining date: January 15, 2024
```

### `hr.txt`

```text
Employee start date: January 20, 2024
```

### `email.txt`

```text
Employment begins January 15, 2024
```

Question:

```text
कर्मचारी ने कब जॉइन किया?
```

A simple RAG system might return:

> January 15, 2024

TruthLens instead identifies the disagreement.

```text
⚠ CONFLICT DETECTED

January 15, 2024
Sources:
• contract.txt
• email.txt

VS

January 20, 2024
Source:
• hr.txt
```

The system can therefore respond with an uncertainty-aware result rather than pretending that one document is automatically correct.

---

# 🧪 Testing

The project includes validation for important components.

Current test coverage includes:

```text
✓ Parser
✓ Language Detection
✓ Language Names
✓ No Evidence Handling
✓ Strong Evidence Handling
✓ Conflict Detection
✓ Confidence Calculation
✓ Conflict Penalty
```

Example expected behavior:

```text
No Evidence
      ↓
I DON'T KNOW / INSUFFICIENT EVIDENCE
```

rather than an unsupported generated answer.

---

# 🛡️ Reliability Principles

TruthLens follows several design principles.

### 1. Evidence Before Answer

The system retrieves evidence before generating an answer.

### 2. No Evidence → No Confident Answer

If useful evidence is unavailable, the system should communicate uncertainty.

### 3. Conflicts Are First-Class Signals

Contradictory evidence should not be silently ignored.

### 4. Citations Come From Document Metadata

Source references are associated with retrieved document chunks rather than being invented by the LLM.

Example metadata:

```python
{
    "file": "contract.pdf",
    "page": 3,
    "chunk_id": "contract_p3_c2",
    "text": "..."
}
```

The UI can then render the corresponding source and page.

### 5. Evidence Score ≠ Truth Probability

The confidence indicator summarizes evidence quality and agreement. It is not a guarantee of factual truth.

---

# 🏆 ALGOTHON'26 — Problem Alignment

TruthLens is built for:

## ALG-AI-02 — Intelligent Document Investigator

The problem statement requires a platform that can:

* Accept multiple documents
* Extract and index information
* Answer natural-language questions
* Provide source / section references
* Detect conflicts
* Handle uncertainty

TruthLens directly targets these requirements.

---

# 📊 Judging Criteria Alignment

| Criteria                   | TruthLens Implementation                                |
| -------------------------- | ------------------------------------------------------- |
| Functionality & Completion | Multi-document investigation pipeline                   |
| Technical Implementation   | Embeddings + FAISS + OCR + LLM + evidence engine        |
| Innovation                 | Counter-evidence, conflict detection, evidence gaps     |
| UX / Presentation          | Investigation dashboard with evidence visibility        |
| Testing / Reliability      | Evidence gating, uncertainty handling, validation tests |
| Problem Understanding      | Designed specifically around document investigation     |

---

# 💡 Real-World Applications

TruthLens can be useful in domains where documents need to be compared before making decisions.

### 🏢 HR

Compare:

* Employment contracts
* HR records
* Emails
* Policies

### ⚖️ Legal

Compare:

* Agreements
* Clauses
* Amendments
* Supporting documents

### 💰 Finance

Compare:

* Reports
* Statements
* Invoices
* Financial records

### 🏥 Healthcare

Compare:

* Reports
* Medical documents
* Records
* Instructions

### 🏛️ Compliance

Compare:

* Policies
* Regulations
* Internal documentation
* Audit records

---

# 🔐 Privacy

TruthLens is designed around user-provided investigation documents.

For production deployment, appropriate security controls should be added for:

* Authentication
* Authorization
* Encryption
* Secure document storage
* API-key management
* Data retention
* Audit logging

Do not upload confidential or sensitive documents to an untrusted deployment.

---

# 🔮 Future Improvements

Potential future work includes:

* Better calibrated evidence scoring
* More robust temporal reasoning
* Advanced document layout understanding
* Table-aware extraction
* Better OCR for complex documents
* Human-in-the-loop verification
* Enterprise authentication
* Secure document-level permissions
* More explainable conflict resolution
* Larger multilingual model support

---

# 🗺️ Development Roadmap

```text
v1.0  Core Q&A + Citations              ✅
v1.1  Conflict Detection                ✅
v1.2  Multi-Language Support            ✅
v1.3  Counter-Evidence                  ✅
v1.4  Evidence Gap + Resolution         ✅
v2.0  Temporal Analysis                 ✅
v2.1  Claim Dependency Graph            ✅
v2.2  Source Drift Detection            ✅
```

---

# 🤝 Contributing

Contributions are welcome.

Possible areas for improvement:

* Better retrieval
* More document formats
* Improved OCR
* Better multilingual support
* Evaluation datasets
* Conflict-resolution algorithms
* UI improvements
* Performance optimization

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Team

### Niranjan Vishe

Computer Engineering Student

**ALGOTHON'26**

Problem Statement:

**ALG-AI-02 — Intelligent Document Investigator**

---

# 🔗 Project

GitHub:

[https://github.com/Nir-bitcoin/truthlens](https://github.com/Nir-bitcoin/truthlens)

---

# 🎯 Final Idea

> **TruthLens doesn't just answer from documents.**
>
> **It investigates the evidence before answering.**

When the evidence agrees:

```text
✓ ANSWER
```

When the evidence conflicts:

```text
⚠ CONFLICT
```

When the evidence is insufficient:

```text
? INSUFFICIENT EVIDENCE
```

Because in document intelligence,

> **A confident answer is not always a reliable answer.**

### 🔍 TruthLens

**Don't just get answers. Get truth.**

```
```
