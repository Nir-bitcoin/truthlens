# app.py
# TruthLens — AI Document Investigator
# ALGOTHON'26 | Team 240 | PS: ALG-AI-02
# Multi-format support + Auto-process + Citations + Confidence + Evidence Chain

import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Backend imports
sys.path.append("backend")
sys.path.append("utils")

from parser import parse_document
from embeddings import process_documents
from retrieval import retrieve
from llm import get_answer
from conflict import (
    detect_conflict,
    check_answerability,
    calculate_evidence_confidence
)
from translator import detect_lang, get_lang_name, translate
from graph import build_conflict_graph

load_dotenv()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TruthLens — AI Document Investigator",
    page_icon="🔍",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1f77b4;
        text-align: center;
    }
    .tagline {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .conflict-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .answer-box {
        background-color: #f0f8ff;
        border-left: 5px solid #1f77b4;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .source-box {
        background-color: #f9f9f9;
        border-left: 3px solid #999;
        padding: 0.6rem;
        border-radius: 6px;
        margin: 0.4rem 0;
        font-size: 0.9rem;
    }
    .strong { color: #28a745; font-weight: bold; }
    .moderate { color: #ffc107; font-weight: bold; }
    .weak { color: #dc3545; font-weight: bold; }
    .cannot { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">🔍 TruthLens</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Don\'t just get answers. Get truth.</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("📂 Upload Documents")
    st.caption("PDF, DOCX, TXT, PNG, JPG — koi bhi format")

    uploaded_files = st.file_uploader(
        "Files upload karo (multiple)",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg", "tiff", "bmp"],
        accept_multiple_files=True
    )

    auto_process = st.checkbox("⚡ Auto-process on upload", value=True)

    st.header("🌍 Answer Language")
    answer_lang = st.selectbox(
        "Answer kis bhasha mein chahiye?",
        ["Auto (same as question)", "English", "Hindi", "Tamil", "Bengali", "Marathi"]
    )

    lang_map = {
        "Auto (same as question)": None,
        "English": "en",
        "Hindi": "hi",
        "Tamil": "ta",
        "Bengali": "bn",
        "Marathi": "mr"
    }

    st.markdown("---")
    st.caption("ALGOTHON'26 • Team 240 • PS: ALG-AI-02")

# ---------------- PROCESS DOCUMENTS ----------------
upload_dir = "data/uploads"
os.makedirs(upload_dir, exist_ok=True)

if uploaded_files:
    current_files = [uf.name for uf in uploaded_files]
    processed_files = st.session_state.get("processed_files", [])
    new_files = [f for f in current_files if f not in processed_files]

    trigger = False
    if auto_process and new_files:
        trigger = True
    if st.sidebar.button("🔄 Process Documents"):
        trigger = True

    if trigger:
        with st.spinner(f"Processing {len(uploaded_files)} files..."):
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
                        failed.append(uf.name)

                    progress.progress((i + 1) / len(uploaded_files))
                except Exception as e:
                    failed.append(f"{uf.name}: {str(e)}")

            if documents:
                process_documents(documents)
                st.session_state["documents"] = documents
                st.session_state["processed_files"] = current_files
                st.success(f"✅ {len(documents)} files indexed!")
            else:
                st.error("❌ Koi file parse nahi hui.")

            if failed:
                with st.expander(f"⚠️ {len(failed)} files failed"):
                    for f in failed:
                        st.write(f"- {f}")

# ---------------- SHOW DOCUMENTS ----------------
if "documents" in st.session_state:
    with st.expander(f"📚 Indexed Documents ({len(st.session_state['documents'])})"):
        for doc in st.session_state["documents"]:
            lang_name = get_lang_name(doc["language"])
            st.markdown(f"- **{doc['file']}** — {lang_name} — {len(doc['pages'])} pages")

# ---------------- QUESTION INPUT ----------------
st.markdown("---")
st.header("💬 Ask a Question")

query = st.text_input(
    "Apna sawaal likho (kisi bhi bhasha mein):",
    placeholder="Example: When did the employee join?"
)

if st.button("🔍 Investigate") and query:
    if "documents" not in st.session_state:
        st.warning("⚠️ Pehle documents upload + process karo.")
    else:
        with st.spinner("Investigating..."):
            q_lang = detect_lang(query)
            chunks = retrieve(query, top_k=5)
            conflict_data = detect_conflict(chunks)
            answerability = check_answerability(chunks, conflict_data, query)
            confidence = calculate_evidence_confidence(chunks, conflict_data)

            if answerability["level"] in ["strong", "moderate"]:
                answer = get_answer(query, chunks)
            else:
                answer = "🤷 Cannot determine reliably. " + answerability["reason"]

            target = lang_map[answer_lang]
            if target and target != q_lang:
                answer = translate(answer, target)

        # ---------------- CONFLICT WARNING ----------------
        if conflict_data.get("conflict"):
            st.markdown('<div class="conflict-box">', unsafe_allow_html=True)
            st.markdown("### ⚠️ CONFLICT DETECTED")
            for pair in conflict_data.get("pairs", []):
                st.markdown(f"""
- **{pair.get('source_a', 'Doc A')}**: {pair.get('claim_a', '')}
- **{pair.get('source_b', 'Doc B')}**: {pair.get('claim_b', '')}
- *Reason*: {pair.get('explanation', '')}
                """)
            st.markdown('</div>', unsafe_allow_html=True)

        # ---------------- ANSWER ----------------
        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        st.markdown("### 📝 Answer")
        st.write(answer)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---------------- ANSWERABILITY ----------------
        level = answerability["level"]
        css_class = level if level in ["strong", "moderate", "weak"] else "cannot"
        st.markdown(
            f"**Evidence Strength:** <span class='{css_class}'>{answerability['label']}</span>",
            unsafe_allow_html=True
        )
        st.caption(answerability["reason"])

        # ---------------- EVIDENCE CONFIDENCE ----------------
        st.markdown("### 📊 Evidence Confidence")
        st.progress(confidence["score"] / 100)
        st.markdown(f"**{confidence['score']}%**")

        col1, col2, col3 = st.columns(3)
        col1.metric("Relevance", f"{confidence['relevance']}%")
        col2.metric("Agreement", f"{confidence['agreement']}%")
        col3.metric("Conflict Penalty", confidence["penalty"])

        # ---------------- EVIDENCE CHAIN ----------------
        with st.expander("🔗 Evidence Chain", expanded=True):
            sources = set(c["file"] for c in chunks)
            st.markdown(f"""
**Question:** {query}

↓

**Retrieved:** {len(chunks)} chunks from {len(sources)} documents

↓

**Claims Extracted:** {len(conflict_data.get('claims', []))}

↓

**Conflict:** {'⚠️ YES' if conflict_data.get('conflict') else '✓ NO'}

↓

**Answerability:** {answerability['label']}
            """)

        # ---------------- CITATIONS ----------------
        st.markdown("### 📌 Citations")
        for i, c in enumerate(chunks, 1):
            st.markdown(
                f'<div class="source-box">'
                f'<b>{i}. {c["file"]}</b> — Page {c.get("page", "?")} '
                f'(Lang: {get_lang_name(c["language"])})<br>'
                f'{c["text"][:300]}...'
                f'</div>',
                unsafe_allow_html=True
            )

        # ---------------- CONFLICT GRAPH ----------------
        if conflict_data.get("conflict"):
            with st.expander("🕸️ Conflict Graph"):
                fig = build_conflict_graph(conflict_data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built with ❤️ for ALGOTHON'26 | TruthLens — Don't just get answers. Get truth.")