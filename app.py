# app.py
# TruthLens — AI Document Investigator
# Professional dashboard UI for Streamlit

import html
import os
import sys
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv

sys.path.append("backend")
sys.path.append("utils")

# ============================================
# BACKEND IMPORTS
# ============================================
from parser import parse_document
from embeddings import process_documents
from retrieval import retrieve
from llm import get_answer
from conflict import (
    detect_conflict,
    check_answerability,
    calculate_evidence_confidence,
    find_counter_evidence,
    detect_evidence_gaps,
    run_evidence_battle,
    analyze_temporal_conflicts,
    detect_source_drift,
    build_claim_dependency_graph,
)
from translator import detect_lang, get_lang_name, translate
from graph import build_conflict_graph, build_dependency_graph_figure

# Investigation pipeline
from investigation_pipeline import run_full_investigation
from verdict_engine import get_kpi_cards
from eeg_engine import get_eeg_kpis
from independence_engine import get_independence_kpis
from cee_engine import get_cee_kpis
from serpapi_evidence import get_serpapi_kpis

load_dotenv()

st.set_page_config(
    page_title="TruthLens — AI Document Investigator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================
# STYLES
# ============================================
STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap');

:root {
    --ink: #0d131d;
    --surface: #141c2a;
    --surface-2: #1a2436;
    --surface-3: #212d44;
    --line: #2a3850;
    --text: #e6ebf3;
    --muted: #8b98ad;
    --faint: #66738a;
    --accent: #5aaee6;
    --accent-dim: #2c5f8a;
    --ok: #3fb68b;
    --warn: #e2a63c;
    --bad: #e5675f;
    --serif: 'Source Serif 4', Georgia, serif;
    --sans: 'IBM Plex Sans', -apple-system, 'Segoe UI', sans-serif;
}

/* ---------- App shell ---------- */
.stApp {
    background:
        radial-gradient(1200px 500px at 15% -10%, rgba(90, 174, 230, 0.07), transparent 60%),
        var(--ink);
    font-family: var(--sans);
    color: var(--text);
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; max-width: 1280px; }

html, body, [class*="st-"], .stMarkdown, p, li, label {
    font-family: var(--sans);
}
h1, h2, h3, h4 { font-family: var(--serif); color: var(--text); letter-spacing: -0.01em; }
h3 { font-size: 1.35rem; }
h4 { font-size: 1.1rem; }

:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

/* ---------- Header ---------- */
.tl-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    padding: 1.15rem 1.5rem;
    border-radius: 14px;
    background: var(--surface);
    border: 1px solid var(--line);
    box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset, 0 8px 24px rgba(0,0,0,0.25);
    margin-bottom: 1.5rem;
}
.tl-brand { display: flex; align-items: center; gap: 0.9rem; }
.tl-mark { width: 40px; height: 40px; flex: none; }
.tl-title {
    font-family: var(--serif);
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1.1;
    margin: 0;
}
.tl-sub { color: var(--muted); font-size: 0.92rem; margin-top: 0.25rem; }
.tl-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 500;
    background: var(--surface-2);
    color: var(--muted);
    border: 1px solid var(--line);
}
.tl-chip .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--faint); }
.tl-chip.ok { color: #9fe0c6; border-color: rgba(63, 182, 139, 0.45); }
.tl-chip.ok .dot { background: var(--ok); }

/* ---------- Verdict: stacked sheets (the one 3D moment) ---------- */
.verdict-wrap {
    position: relative;
    margin: 1.5rem 14px 2.4rem 0;
    perspective: 1400px;
}
.verdict-wrap::before,
.verdict-wrap::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 16px;
    background: var(--surface-2);
    border: 1px solid var(--line);
}
.verdict-wrap::before { transform: translate(14px, 14px); opacity: 0.45; z-index: 0; }
.verdict-wrap::after  { transform: translate(7px, 7px);  opacity: 0.75; z-index: 1; }

.verdict-card {
    --tone: var(--accent);
    position: relative;
    z-index: 2;
    padding: 1.6rem 2rem 1.6rem 2.2rem;
    border-radius: 16px;
    background: linear-gradient(160deg, var(--surface-3), var(--surface));
    border: 1px solid var(--line);
    box-shadow:
        0 1px 0 rgba(255,255,255,0.06) inset,
        0 18px 40px rgba(0,0,0,0.45);
    transform-origin: 50% 0;
    transform: rotateX(1.5deg);
    animation: settle 0.7s ease-out both;
    overflow: hidden;
}
.verdict-card::before {
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 6px;
    background: var(--tone);
}
.verdict-card.supported    { --tone: var(--ok); }
.verdict-card.conflicted   { --tone: var(--warn); }
.verdict-card.insufficient { --tone: var(--bad); }
.verdict-card.unknown      { --tone: var(--faint); }

.verdict-label { color: var(--muted); font-size: 0.85rem; margin: 0 0 0.3rem 0; }
.verdict-title {
    font-family: var(--serif);
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--tone);
    margin: 0;
    line-height: 1.15;
}
.verdict-subtitle {
    font-size: 1rem;
    color: #c4cddb;
    margin: 0.7rem 0 0 0;
    line-height: 1.55;
    max-width: 78ch;
}

@keyframes settle {
    from { opacity: 0; transform: rotateX(9deg) translateY(10px); }
    to   { opacity: 1; transform: rotateX(1.5deg) translateY(0); }
}

/* ---------- KPI cards ---------- */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 0.9rem;
    margin: 1.2rem 0 1.6rem;
}
.kpi-card {
    --tone: var(--accent);
    position: relative;
    padding: 1rem 1.1rem 1rem 1.25rem;
    border-radius: 12px;
    background: linear-gradient(170deg, var(--surface-2), var(--surface));
    border: 1px solid var(--line);
    box-shadow:
        0 1px 0 rgba(255,255,255,0.05) inset,
        0 2px 0 rgba(0,0,0,0.25),
        0 10px 22px rgba(0,0,0,0.28);
    transition: border-color 0.2s ease;
}
.kpi-card:hover { border-color: var(--accent-dim); }
.kpi-card::before {
    content: "";
    position: absolute;
    left: 0; top: 12px; bottom: 12px;
    width: 3px;
    border-radius: 0 3px 3px 0;
    background: var(--tone);
}
.kpi-card.success { --tone: var(--ok); }
.kpi-card.warning { --tone: var(--warn); }
.kpi-card.danger  { --tone: var(--bad); }
.kpi-label { color: var(--muted); font-size: 0.82rem; font-weight: 500; margin-bottom: 0.45rem; }
.kpi-value {
    color: var(--text);
    font-family: var(--serif);
    font-size: 1.75rem;
    font-weight: 700;
    line-height: 1.1;
}
.kpi-sub { color: var(--faint); font-size: 0.78rem; margin-top: 0.35rem; }

/* ---------- Content cards ---------- */
.tl-card {
    --tone: var(--accent);
    background: var(--surface);
    border: 1px solid var(--line);
    border-left: 3px solid var(--tone);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin: 0.55rem 0;
    color: var(--text);
    font-size: 0.93rem;
    line-height: 1.55;
}
.tl-card.support    { --tone: var(--ok); }
.tl-card.contradict { --tone: var(--bad); }
.tl-card.info       { --tone: var(--accent); }
.tl-card.warning    { --tone: var(--warn); }
.tl-card .meta { color: var(--muted); font-size: 0.85rem; }

.tl-source {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    color: #c4cddb;
    line-height: 1.55;
}
.tl-source b { color: var(--text); }

/* ---------- Web source cards ---------- */
.source-card {
    --tone: var(--warn);
    background: var(--surface);
    border: 1px solid var(--line);
    border-left: 3px solid var(--tone);
    border-radius: 10px;
    padding: 0.95rem 1.1rem;
    margin: 0.6rem 0;
}
.source-card.support    { --tone: var(--ok); }
.source-card.contradict { --tone: var(--bad); }
.source-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.45rem;
}
.source-badge {
    font-size: 0.78rem;
    font-weight: 600;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    color: var(--tone);
    border: 1px solid var(--tone);
}
.source-domain { color: var(--faint); font-size: 0.82rem; }
.source-title { color: var(--text); font-weight: 600; font-size: 0.97rem; line-height: 1.4; margin-bottom: 0.35rem; }
.source-snippet { color: var(--muted); font-size: 0.87rem; line-height: 1.55; margin-bottom: 0.5rem; }
.source-link { color: var(--accent); font-size: 0.85rem; text-decoration: none; font-weight: 500; }
.source-link:hover { text-decoration: underline; }

/* ---------- Coverage bar ---------- */
.coverage-bar {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin: 1rem 0;
}
.coverage-label {
    display: flex;
    justify-content: space-between;
    color: var(--text);
    font-weight: 500;
    margin-bottom: 0.6rem;
}
.coverage-track {
    height: 10px;
    background: var(--ink);
    border: 1px solid var(--line);
    border-radius: 999px;
    overflow: hidden;
}
.coverage-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-dim), var(--accent));
    border-radius: 999px;
}

/* ---------- Empty state ---------- */
.empty-state {
    border: 1px dashed var(--line);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    color: var(--muted);
    background: rgba(20, 28, 42, 0.5);
    line-height: 1.6;
}
.empty-state b { color: var(--text); }

/* ---------- Streamlit widgets ---------- */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    font-family: var(--sans);
    background: linear-gradient(180deg, #3b7db5, #2c6694);
    border: 1px solid #4b8fc6;
    color: #fff;
    box-shadow: 0 1px 0 rgba(255,255,255,0.15) inset, 0 4px 10px rgba(0,0,0,0.3);
    transition: background 0.2s ease, transform 0.15s ease;
}
.stButton > button:hover {
    background: linear-gradient(180deg, #4a8cc4, #3573a4);
    border-color: #6aa6d6;
    color: #fff;
}
.stButton > button:active { transform: translateY(1px); }

[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] * { color: #cfd7e4; }
[data-testid="stSidebar"] h3 { font-size: 1.05rem; color: var(--text); }

.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 4px;
    overflow-x: auto;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    color: var(--muted);
}
.stTabs [aria-selected="true"] {
    background: var(--surface-3) !important;
    color: var(--text) !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: var(--accent) !important; }

.stTextInput > div > div > input {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    padding: 0.7rem 0.9rem !important;
}
.stTextInput > div > div > input:focus { border-color: var(--accent) !important; }

[data-testid="stExpander"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
}

@media (max-width: 720px) {
    .tl-header { flex-direction: column; align-items: flex-start; }
    .verdict-title { font-size: 1.6rem; }
}
@media (prefers-reduced-motion: reduce) {
    .verdict-card { animation: none; transform: none; }
    * { transition: none !important; }
}
</style>
"""
st.markdown(STYLES, unsafe_allow_html=True)


# ============================================
# HELPERS
# ============================================
def esc(value) -> str:
    """Escape any text that ends up inside raw HTML (web results are untrusted)."""
    return html.escape(str(value if value is not None else ""))


def block(markup: str) -> str:
    """Strip indentation so Markdown never treats HTML as a code block."""
    return "".join(line.strip() for line in markup.strip().splitlines())


def render_kpi_card(label: str, value: str, sub: str = "", variant: str = "accent") -> str:
    sub_html = f'<div class="kpi-sub">{esc(sub)}</div>' if sub else ""
    return (
        f'<div class="kpi-card {esc(variant)}">'
        f'<div class="kpi-label">{esc(label)}</div>'
        f'<div class="kpi-value">{esc(value)}</div>'
        f"{sub_html}</div>"
    )


def render_kpi_grid(cards: list) -> str:
    inner = "".join(
        render_kpi_card(c["label"], c["value"], c.get("sub", ""), c.get("variant", "accent"))
        for c in cards
    )
    return f'<div class="kpi-grid">{inner}</div>'


def card(variant: str, body: str) -> str:
    """Content card. `body` must already be escaped / safe HTML."""
    return f'<div class="tl-card {variant}">{body}</div>'


def empty_state(message: str):
    st.markdown(f'<div class="empty-state">{message}</div>', unsafe_allow_html=True)


# ============================================
# HEADER
# ============================================
docs_count = len(st.session_state.get("documents", []))
if docs_count > 0:
    status_html = f'<span class="tl-chip ok"><span class="dot"></span>{docs_count} document(s) indexed</span>'
else:
    status_html = '<span class="tl-chip"><span class="dot"></span>No documents indexed</span>'

LOGO_SVG = (
    '<svg class="tl-mark" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<rect x="3" y="3" width="34" height="34" rx="9" fill="#1a2436" stroke="#2a3850"/>'
    '<circle cx="18" cy="18" r="7" stroke="#5aaee6" stroke-width="2.4"/>'
    '<path d="M23.5 23.5L30 30" stroke="#5aaee6" stroke-width="2.4" stroke-linecap="round"/>'
    '<path d="M14.8 18.2l2.3 2.3 4.2-4.6" stroke="#3fb68b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)

st.markdown(
    block(
        f"""
<div class="tl-header">
  <div class="tl-brand">
    {LOGO_SVG}
    <div>
      <div class="tl-title">TruthLens</div>
      <div class="tl-sub">Check any claim against your documents and the live web.</div>
    </div>
  </div>
  <div>{status_html}</div>
</div>
"""
    ),
    unsafe_allow_html=True,
)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("### Documents")
    st.caption("PDF, DOCX, TXT, PNG, JPG")

    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg", "tiff", "bmp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    auto_process = st.checkbox("Process files on upload", value=True)

    st.markdown("---")
    st.markdown("### Answer language")

    answer_lang = st.selectbox(
        "Answer language",
        ["Auto (same as question)", "English", "Hindi", "Marathi", "Tamil",
         "Bengali", "Telugu", "Gujarati", "Kannada", "Malayalam", "Punjabi", "Urdu"],
        label_visibility="collapsed",
    )

    lang_map = {
        "Auto (same as question)": None,
        "English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta",
        "Bengali": "bn", "Telugu": "te", "Gujarati": "gu", "Kannada": "kn",
        "Malayalam": "ml", "Punjabi": "pa", "Urdu": "ur",
    }

    st.markdown("---")
    st.markdown("### Investigation settings")

    enable_cee = st.checkbox(
        "Counterfactual check", value=True,
        help="Runs a targeted search after the first verdict to see what could change it.",
    )
    enable_serpapi = st.checkbox(
        "Live web evidence", value=True,
        help="Pulls web, news and fact-check results through SerpApi.",
    )

# ============================================
# PROCESS DOCUMENTS
# ============================================
upload_dir = "data/uploads"
os.makedirs(upload_dir, exist_ok=True)

if uploaded_files:
    current_files = [uf.name for uf in uploaded_files]
    processed_files = st.session_state.get("processed_files", [])
    new_files = [f for f in current_files if f not in processed_files]

    trigger = (auto_process and new_files) or st.sidebar.button(
        "Process documents", use_container_width=True
    )

    if trigger:
        with st.spinner("Processing documents..."):
            documents = []
            progress = st.progress(0)
            failed = []

            for i, uf in enumerate(uploaded_files):
                try:
                    file_path = os.path.join(upload_dir, uf.name)
                    with open(file_path, "wb") as f:
                        f.write(uf.getbuffer())
                    doc = parse_document(file_path)
                    if doc["full_text"].strip():
                        documents.append(doc)
                    else:
                        failed.append(f"{uf.name}: no readable text found")
                    progress.progress((i + 1) / len(uploaded_files))
                except Exception as e:
                    failed.append(f"{uf.name}: {e}")

            st.session_state["failed_files"] = failed

            if documents:
                process_documents(documents)
                st.session_state["documents"] = documents
                st.session_state["processed_files"] = current_files
                st.toast(f"{len(documents)} file(s) indexed", icon="✅")
                st.rerun()
            else:
                st.error("None of the uploaded files could be read.")

if st.session_state.get("failed_files"):
    with st.expander(f"{len(st.session_state['failed_files'])} file(s) could not be processed"):
        for item in st.session_state["failed_files"]:
            st.write(f"- {item}")

# ============================================
# INDEXED DOCUMENTS
# ============================================
if st.session_state.get("documents"):
    with st.expander(f"Indexed documents ({len(st.session_state['documents'])})"):
        for doc in st.session_state["documents"]:
            lang_name = get_lang_name(doc["language"])
            st.markdown(f"- **{doc['file']}** — {lang_name}, {len(doc['pages'])} pages")

# ============================================
# QUESTION INPUT
# ============================================
st.markdown("### Ask a question or check a claim")

query = st.text_input(
    "Question or claim",
    placeholder="Example: Elon Musk acquired Twitter in 2022",
    label_visibility="collapsed",
)

run_clicked = st.button("Investigate", type="primary", use_container_width=True)


# ============================================
# PIPELINE
# ============================================
def run_investigation(query: str) -> dict:
    has_docs = bool(st.session_state.get("documents"))

    q_lang = detect_lang(query)
    query_en = translate(query, "en") if q_lang != "en" else query

    chunks = []
    conflict_data = {}
    answerability = {"level": "no_evidence", "label": "No evidence", "reason": ""}
    confidence = {"score": 0, "relevance": 0, "agreement": 0, "penalty": 0}
    counter_evidence = {}
    gap_data = {}
    evidence_battle = {}
    temporal_analysis = {}
    source_drift = {}
    dependency_graph = {}

    if has_docs:
        chunks = retrieve(query_en, top_k=5)
        if chunks:
            conflict_data = detect_conflict(chunks)
            answerability = check_answerability(chunks, conflict_data, query)
            confidence = calculate_evidence_confidence(chunks, conflict_data)
            counter_evidence = find_counter_evidence(query, chunks)
            gap_data = detect_evidence_gaps(query, chunks, conflict_data)
            evidence_battle = run_evidence_battle(query, chunks)
            temporal_analysis = analyze_temporal_conflicts(chunks)
            source_drift = detect_source_drift(chunks)
            dependency_graph = build_claim_dependency_graph(query, chunks)

    investigation = {}
    if enable_serpapi:
        investigation = run_full_investigation(
            claim=query_en,
            document_chunks=chunks,
            answerability=answerability,
            enable_cee=enable_cee,
        )

    target = lang_map[answer_lang]
    if answerability["level"] in ["strong", "moderate"] and chunks:
        answer = get_answer(query, chunks, target)
    elif investigation and investigation.get("final_verdict"):
        answer = investigation["final_verdict"].get("summary", "Cannot determine reliably.")
    else:
        answer = "Cannot determine reliably. " + answerability["reason"]

    return {
        "query": query,
        "answer": answer,
        "chunks": chunks,
        "conflict_data": conflict_data,
        "answerability": answerability,
        "confidence": confidence,
        "counter_evidence": counter_evidence,
        "gap_data": gap_data,
        "evidence_battle": evidence_battle,
        "temporal_analysis": temporal_analysis,
        "source_drift": source_drift,
        "dependency_graph": dependency_graph,
        "investigation": investigation,
    }


if run_clicked:
    if not query.strip():
        st.warning("Enter a question or claim to investigate.")
    else:
        if not st.session_state.get("documents"):
            st.info("No documents are indexed, so this investigation will use live web evidence only.")
        with st.spinner("Investigating..."):
            st.session_state["result"] = run_investigation(query.strip())


# ============================================
# RESULTS
# ============================================
def render_verdict(r: dict):
    investigation = r["investigation"]
    conflict_data = r["conflict_data"]
    answerability = r["answerability"]

    final_verdict = investigation.get("final_verdict", {}) if investigation else {}
    verdict_label = final_verdict.get("verdict", "UNKNOWN")

    if verdict_label == "SUPPORTED":
        v_class, v_text = "supported", "Supported"
    elif verdict_label == "CONFLICTED":
        v_class, v_text = "conflicted", "Conflicted"
    elif verdict_label == "INSUFFICIENT":
        v_class, v_text = "insufficient", "Insufficient evidence"
    elif conflict_data.get("conflict"):
        v_class, v_text = "conflicted", "Conflict found in documents"
    else:
        v_class, v_text = "unknown", "Unknown"

    v_sub = final_verdict.get("summary", answerability.get("reason", ""))

    st.markdown(
        block(
            f"""
<div class="verdict-wrap">
  <div class="verdict-card {v_class}">
    <p class="verdict-label">Verdict</p>
    <p class="verdict-title">{esc(v_text)}</p>
    <p class="verdict-subtitle">{esc(v_sub)}</p>
  </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )

    if final_verdict:
        kpi = get_kpi_cards(final_verdict)

        verdict_variant = {
            "SUPPORTED": "success",
            "CONFLICTED": "warning",
            "INSUFFICIENT": "warning",
            "UNKNOWN": "danger",
        }.get(verdict_label, "accent")

        try:
            conf_num = float(str(kpi.get("Confidence", "0%")).rstrip("%"))
        except Exception:
            conf_num = 0
        conf_variant = "success" if conf_num > 60 else "warning" if conf_num > 30 else "danger"

        cards = [
            {"label": "Verdict", "value": kpi.get("Verdict", "—"),
             "sub": "Final conclusion", "variant": verdict_variant},
            {"label": "Confidence", "value": kpi.get("Confidence", "—"),
             "sub": "Evidence strength", "variant": conf_variant},
            {"label": "Support", "value": kpi.get("Support", "—"),
             "sub": "Supporting weight", "variant": "success"},
            {"label": "Contradiction", "value": kpi.get("Contradict", "—"),
             "sub": "Opposing weight", "variant": "danger"},
            {"label": "Evidence items", "value": kpi.get("Evidence", "—"),
             "sub": "Total reviewed", "variant": "accent"},
            {"label": "Independent sources", "value": kpi.get("Independent", "—"),
             "sub": "Unique clusters", "variant": "accent"},
        ]
        st.markdown(render_kpi_grid(cards), unsafe_allow_html=True)

    return final_verdict


def render_answer_tab(r: dict):
    st.markdown("### Answer")
    st.info(r["answer"])

    if r["chunks"]:
        st.markdown("#### Document citations")
        for i, c in enumerate(r["chunks"][:5], 1):
            st.markdown(
                block(
                    f'<div class="tl-source"><b>{i}. {esc(c["file"])}</b> — page {esc(c.get("page", "?"))}<br>'
                    f'{esc(c["text"][:250])}…</div>'
                ),
                unsafe_allow_html=True,
            )


def render_evidence_tab(r: dict):
    battle = r["evidence_battle"]
    st.markdown("### Supporting and contradicting evidence")

    if battle.get("candidate_answer"):
        st.markdown(f"**Candidate answer:** {battle.get('candidate_answer', '')}")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Supporting")
            for claim in battle.get("supporter", {}).get("claims", []):
                st.markdown(
                    card("support", f'<b>{esc(claim.get("source", "Document"))}</b><br>{esc(claim.get("claim", ""))}'),
                    unsafe_allow_html=True,
                )

        with col2:
            st.markdown("#### Contradicting")
            for claim in battle.get("skeptic", {}).get("claims", []):
                st.markdown(
                    card("contradict", f'<b>{esc(claim.get("source", "Document"))}</b><br>{esc(claim.get("claim", ""))}'),
                    unsafe_allow_html=True,
                )
    else:
        empty_state("<b>No document evidence yet.</b><br>Upload documents in the sidebar to compare supporting and opposing claims.")


def render_investigation_tab(r: dict):
    st.markdown("### Investigation details")
    shown = False

    if r["counter_evidence"].get("candidate_answer"):
        shown = True
        st.markdown("#### Counter-evidence")
        st.write(r["counter_evidence"].get("candidate_answer", ""))

    if r["gap_data"].get("evidence_gaps"):
        shown = True
        st.markdown("#### Evidence gaps")
        for gap in r["gap_data"].get("evidence_gaps", []):
            st.markdown(
                card("warning", f'<b>{esc(gap.get("missing", ""))}</b><br><span class="meta">{esc(gap.get("why_needed", ""))}</span>'),
                unsafe_allow_html=True,
            )

    if not shown:
        empty_state("<b>Nothing to report.</b><br>No counter-evidence or gaps were found in the indexed documents.")


def render_analysis_tab(r: dict):
    st.markdown("### Temporal and source analysis")
    shown = False

    if r["temporal_analysis"].get("temporal_analysis"):
        shown = True
        ta = r["temporal_analysis"]["temporal_analysis"]
        st.markdown(f"**Temporal verdict:** {ta.get('verdict', 'no_conflict')}")
        for change in ta.get("temporal_changes", []):
            st.markdown(f"- {change.get('attribute', '')}: {change.get('from', '')} → {change.get('to', '')}")

    if r["source_drift"].get("source_drift"):
        sd = r["source_drift"]["source_drift"]
        if sd.get("drift_detected"):
            shown = True
            st.warning("Source drift detected between document versions.")
            for change in sd.get("changes", []):
                st.markdown(
                    f"- **{change.get('section', '')}**: "
                    f"{change.get('old_value', '')} → {change.get('new_value', '')}"
                )

    if not shown:
        empty_state("<b>No temporal conflicts or source drift detected.</b>")


def render_graphs_tab(r: dict):
    st.markdown("### Visual analysis")
    shown = False

    dg = r["dependency_graph"].get("dependency_graph") if r["dependency_graph"] else None
    if dg and dg.get("claims"):
        fig = build_dependency_graph_figure(dg)
        if fig:
            shown = True
            st.plotly_chart(fig, use_container_width=True)

    if r["conflict_data"].get("conflict"):
        fig = build_conflict_graph(r["conflict_data"])
        if fig:
            shown = True
            st.plotly_chart(fig, use_container_width=True)

    if not shown:
        empty_state("<b>No graphs for this query.</b><br>Graphs appear when documents contain linked claims or conflicts.")


def render_live_tab(r: dict):
    investigation = r["investigation"]
    st.markdown("### Live web evidence")

    live = investigation.get("live_evidence", {}) if investigation else {}
    if not live:
        empty_state("<b>Live web evidence was not run.</b><br>Turn it on under Investigation settings in the sidebar.")
        return

    kpi = get_serpapi_kpis(live)
    st.markdown(
        render_kpi_grid([
            {"label": "Total sources", "value": kpi.get("Total Sources", "0"), "variant": "accent"},
            {"label": "Supporting", "value": kpi.get("Supporting", "0"), "variant": "success"},
            {"label": "Contradicting", "value": kpi.get("Contradicting", "0"), "variant": "danger"},
            {"label": "News", "value": kpi.get("News", "0"), "variant": "accent"},
            {"label": "Fact checks", "value": kpi.get("Fact Checks", "0"), "variant": "warning"},
            {"label": "Scholar", "value": kpi.get("Scholar", "0"), "variant": "accent"},
        ]),
        unsafe_allow_html=True,
    )

    st.markdown("#### News and web results")
    all_live = live.get("supporting", [])[:5] + live.get("contradicting", [])[:5]

    badge_text = {"support": "Supports", "contradict": "Contradicts", "neutral": "Neutral"}
    for item in all_live:
        stance = item.get("stance", "neutral")
        if stance not in badge_text:
            stance = "neutral"

        link = item.get("link", "") or ""
        domain = ""
        if link:
            try:
                domain = urlparse(link).netloc.replace("www.", "")
            except Exception:
                pass
        safe_link = link if link.startswith(("http://", "https://")) else ""
        link_html = (
            f'<a href="{esc(safe_link)}" target="_blank" rel="noopener noreferrer" class="source-link">Open source</a>'
            if safe_link else ""
        )

        st.markdown(
            block(
                f"""
<div class="source-card {stance}">
  <div class="source-header">
    <span class="source-badge">{badge_text[stance]}</span>
    <span class="source-domain">{esc(domain)}</span>
  </div>
  <div class="source-title">{esc(item.get("title", "")[:120])}</div>
  <div class="source-snippet">{esc(item.get("snippet", "")[:250])}…</div>
  {link_html}
</div>
"""
            ),
            unsafe_allow_html=True,
        )


def render_eeg_tab(r: dict):
    investigation = r["investigation"]
    st.markdown("### Expected evidence gap")
    st.caption("What evidence should exist for this claim, and what was actually found.")

    eeg = investigation.get("eeg_result", {}) if investigation else {}
    if not eeg:
        empty_state("<b>Expected evidence analysis was not run.</b>")
        return

    kpi = get_eeg_kpis(eeg)
    st.markdown(
        render_kpi_grid([
            {"label": "Coverage", "value": kpi.get("Coverage", "—"), "variant": "success"},
            {"label": "Search coverage", "value": kpi.get("Search Coverage", "—"), "variant": "accent"},
            {"label": "Missing", "value": kpi.get("Missing", "—"), "variant": "warning"},
            {"label": "High-priority missing", "value": kpi.get("High-Priority Missing", "—"), "variant": "danger"},
            {"label": "Gap severity", "value": kpi.get("Gap Severity", "—"), "variant": "warning"},
        ]),
        unsafe_allow_html=True,
    )

    try:
        coverage = max(0.0, min(100.0, float(eeg.get("coverage", 0))))
    except (TypeError, ValueError):
        coverage = 0.0

    st.markdown(
        block(
            f"""
<div class="coverage-bar">
  <div class="coverage-label"><span>Evidence coverage</span><span>{coverage:.1f}%</span></div>
  <div class="coverage-track"><div class="coverage-fill" style="width: {coverage}%;"></div></div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )

    st.markdown(f"**Summary:** {eeg.get('summary', '')}")

    st.markdown("#### Expected signals found")
    for f in eeg.get("found", []):
        st.markdown(
            card(
                "support",
                f'<b>[{esc(f.get("priority", ""))}]</b> {esc(f.get("signal", ""))}<br>'
                f'<span class="meta">Matched: {esc(f.get("evidence_title", "")[:100])}</span>',
            ),
            unsafe_allow_html=True,
        )

    st.markdown("#### Expected signals missing")
    for m in eeg.get("missing", []):
        st.markdown(
            card(
                "warning",
                f'<b>[{esc(m.get("priority", ""))}]</b> {esc(m.get("signal", ""))}<br>'
                f'<span class="meta">{esc(m.get("why", ""))}</span>',
            ),
            unsafe_allow_html=True,
        )


def render_independence_tab(r: dict):
    investigation = r["investigation"]
    st.markdown("### Source independence")
    st.caption("Many sources can trace back to one origin. This shows how many are truly independent.")

    cluster_data = investigation.get("cluster_data", {}) if investigation else {}
    if not cluster_data:
        empty_state("<b>Independence analysis was not run.</b>")
        return

    kpi = get_independence_kpis(cluster_data)
    st.markdown(
        render_kpi_grid([
            {"label": "Total sources", "value": kpi.get("Total Sources", "0"), "variant": "accent"},
            {"label": "Independent", "value": kpi.get("Independent Clusters", "0"), "variant": "success"},
            {"label": "Concentration", "value": kpi.get("Concentration", "—"), "variant": "warning"},
            {"label": "Independence score", "value": kpi.get("Independence Score", "—"), "variant": "accent"},
        ]),
        unsafe_allow_html=True,
    )

    st.markdown("#### Clusters")
    for c in cluster_data.get("clusters", [])[:10]:
        st.markdown(
            card(
                "info",
                f'<b>{esc(c.get("cluster_id", ""))}</b> — {esc(c.get("size", 0))} source(s), '
                f'{esc(c.get("domain", ""))}<br>'
                f'<span class="meta">{esc(c.get("representative_title", "")[:100])}</span>',
            ),
            unsafe_allow_html=True,
        )


def render_cee_tab(r: dict):
    investigation = r["investigation"]
    st.markdown("### What would change this verdict?")
    st.caption("Counterfactual evidence check")

    cee = investigation.get("cee_result", {}) if investigation else {}
    if not cee:
        empty_state("<b>Counterfactual check was not run.</b><br>Turn it on under Investigation settings in the sidebar.")
        return

    kpi = get_cee_kpis(cee)
    st.markdown(
        render_kpi_grid([
            {"label": "Previous verdict", "value": kpi.get("Old Verdict", "—"), "variant": "accent"},
            {"label": "New verdict", "value": kpi.get("New Verdict", "—"), "variant": "accent"},
            {"label": "Changed", "value": kpi.get("Changed", "—"),
             "variant": "success" if kpi.get("Changed") == "YES" else "warning"},
            {"label": "Confidence before", "value": kpi.get("Confidence Before", "—"), "variant": "accent"},
            {"label": "Confidence after", "value": kpi.get("Confidence After", "—"), "variant": "accent"},
        ]),
        unsafe_allow_html=True,
    )

    st.markdown(f"**Reason:** {cee.get('reason', '')}")

    st.markdown("#### Decisive evidence targets")
    for t in cee.get("targets", []):
        variant = "support" if t.get("direction") == "upgrade" else "contradict"
        st.markdown(
            card(
                variant,
                f'<b>{esc(t.get("direction", "")).capitalize()} · {esc(t.get("impact", ""))} impact</b><br>'
                f'{esc(t.get("evidence", ""))}',
            ),
            unsafe_allow_html=True,
        )


def render_chain(r: dict, final_verdict: dict):
    investigation = r["investigation"]
    chunks = r["chunks"]
    sources = {c["file"] for c in chunks} if chunks else set()
    live_count = len(investigation.get("all_evidence", [])) if investigation else 0
    eeg = investigation.get("eeg_result", {}) if investigation else {}
    cluster_data = investigation.get("cluster_data", {}) if investigation else {}

    with st.expander("Evidence chain"):
        st.markdown(
            f"""
**Question:** {r['query']}

↓

**Document chunks:** {len(chunks)} from {len(sources)} document(s)

↓

**Live web evidence:** {live_count} item(s)

↓

**Expected-evidence coverage:** {eeg.get('coverage', 0)}% · gap severity {eeg.get('gap_severity', '—')}

↓

**Independent clusters:** {cluster_data.get('independent_clusters', 0)} of {cluster_data.get('total_sources', 0)}

↓

**Final verdict:** {final_verdict.get('verdict', 'UNKNOWN')} ({final_verdict.get('confidence', 0)}%)
            """
        )


result = st.session_state.get("result")

if result:
    st.markdown("---")
    st.caption(f"Results for: {result['query']}")

    final_verdict = render_verdict(result)

    tabs = st.tabs([
        "Answer", "Evidence", "Investigation", "Analysis", "Graphs",
        "Live web", "Expected gaps", "Independence", "Counterfactual",
    ])
    renderers = [
        render_answer_tab, render_evidence_tab, render_investigation_tab,
        render_analysis_tab, render_graphs_tab, render_live_tab,
        render_eeg_tab, render_independence_tab, render_cee_tab,
    ]
    for tab, render in zip(tabs, renderers):
        with tab:
            render(result)

    render_chain(result, final_verdict)
else:
    empty_state(
        "<b>Ready when you are.</b><br>"
        "Upload documents in the sidebar, then enter a claim above. "
        "TruthLens checks it against your files and live web sources, and shows how strong the evidence is."
    )

st.markdown("---")
st.caption("TruthLens — Don't just get answers. Get truth.")