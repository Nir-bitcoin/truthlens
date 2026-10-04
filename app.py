# app.py
# TruthLens — AI Document Investigator
# Dark Theme + Fast Mode

import streamlit as st
import os
import sys
import time
from dotenv import load_dotenv

sys.path.append("backend")
sys.path.append("utils")

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
    build_claim_dependency_graph
)
from translator import detect_lang, get_lang_name, translate
from graph import build_conflict_graph, build_dependency_graph_figure

load_dotenv()

st.set_page_config(
    page_title="TruthLens — AI Document Investigator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# DARK THEME + ANIMATED CSS
# ============================================
st.markdown("""
<style>
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-40px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(107, 155, 209, 0.4); }
        50% { box-shadow: 0 0 0 15px rgba(107, 155, 209, 0); }
        100% { box-shadow: 0 0 0 0 rgba(107, 155, 209, 0); }
    }
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(3deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp {
        background: linear-gradient(-45deg, #0f141b, #131a24, #0f141b, #171e28);
        background-size: 400% 400%;
        animation: gradientShift 20s ease infinite;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    .tl-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.2rem 1.6rem;
        border-radius: 16px;
        background: rgba(23, 30, 40, 0.75);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(107, 155, 209, 0.15);
        margin-bottom: 1.5rem;
        animation: fadeInUp 0.6s ease-out;
    }
    .tl-title {
        font-size: 1.9rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6b9bd1, #8bb4de, #5a8ab8);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 5s ease infinite;
        display: inline-block;
        margin: 0;
    }
    .tl-logo {
        display: inline-block;
        animation: float 3s ease-in-out infinite;
        margin-right: 0.6rem;
        -webkit-text-fill-color: initial;
    }
    .tl-sub {
        color: #9ca3af;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }
    .tl-chip {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        background: rgba(107, 155, 209, 0.12);
        color: #8bb4de;
        border: 1px solid rgba(107, 155, 209, 0.3);
        animation: fadeIn 1s ease-in;
    }
    .tl-chip.ok {
        background: rgba(74, 222, 128, 0.12);
        color: #6ee7a7;
        border-color: rgba(74, 222, 128, 0.3);
    }

    .verdict-banner {
        padding: 1.6rem;
        border-radius: 16px;
        margin: 1rem 0;
        text-align: center;
        animation: fadeInUp 0.7s cubic-bezier(0.34, 1.56, 0.64, 1);
        transition: all 0.3s ease;
    }
    .verdict-banner:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
    }
    .verdict-supported {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(34, 197, 94, 0.08));
        border: 2px solid #4ade80;
        animation: pulseGlow 3s infinite, fadeInUp 0.7s;
    }
    .verdict-conflict {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.08));
        border: 2px solid #fbbf24;
        animation: pulseGlow 3s infinite, fadeInUp 0.7s;
    }
    .verdict-insufficient {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.08));
        border: 2px solid #f87171;
        animation: pulseGlow 3s infinite, fadeInUp 0.7s;
    }
    .verdict-title {
        font-size: 1.7rem;
        font-weight: 800;
        margin: 0;
        color: #f3f4f6;
    }
    .verdict-subtitle {
        font-size: 1rem;
        color: #9ca3af;
        margin-top: 0.5rem;
    }

    .tl-card {
        background: rgba(23, 30, 40, 0.7);
        backdrop-filter: blur(15px);
        border-radius: 14px;
        padding: 1.2rem;
        margin: 0.6rem 0;
        border-left: 4px solid #6b9bd1;
        animation: fadeInUp 0.5s ease-out;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        color: #e5e9f0;
    }
    .tl-card:hover {
        transform: translateY(-5px) translateX(3px);
        box-shadow: 0 12px 30px rgba(107, 155, 209, 0.15);
    }
    .tl-card-support {
        border-left-color: #4ade80;
        background: rgba(34, 197, 94, 0.1);
    }
    .tl-card-contradict {
        border-left-color: #f87171;
        background: rgba(239, 68, 68, 0.1);
    }
    .tl-card-info {
        border-left-color: #60a5fa;
        background: rgba(96, 165, 250, 0.1);
    }
    .tl-card-warning {
        border-left-color: #fbbf24;
        background: rgba(245, 158, 11, 0.1);
    }

    .tl-source {
        background: rgba(23, 30, 40, 0.8);
        border-left: 3px solid #4b5563;
        padding: 0.7rem 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #d1d5db;
        animation: fadeIn 0.5s ease-in;
        transition: all 0.25s ease;
    }
    .tl-source:hover {
        border-left-color: #6b9bd1;
        background: rgba(107, 155, 209, 0.1);
        transform: translateX(5px);
    }

    [data-testid="stMetric"] {
        background: rgba(23, 30, 40, 0.75);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(107, 155, 209, 0.15);
        border-radius: 14px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-in;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 30px rgba(107, 155, 209, 0.2);
    }

    .stButton > button {
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        border-radius: 12px;
        font-weight: 600;
        background: linear-gradient(135deg, #2f5d8a, #4a6fa5);
        border: none;
        color: white;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(107, 155, 209, 0.35);
        background: linear-gradient(135deg, #4a6fa5, #6b9bd1);
    }
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6b9bd1, #4a6fa5, #8bb4de);
        background-size: 200% 100%;
        animation: gradientShift 2s ease infinite;
        border-radius: 10px;
        transition: width 0.3s ease;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f141b, #171e28);
        animation: slideInLeft 0.5s ease-out;
        border-right: 1px solid rgba(107, 155, 209, 0.1);
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }
    [data-testid="stSidebar"] * {
        color: #d1d5db;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(23, 30, 40, 0.6);
        border-radius: 12px;
        padding: 4px;
        animation: fadeIn 0.5s ease-in;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        color: #9ca3af;
        transition: all 0.25s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(107, 155, 209, 0.12);
        transform: translateY(-2px);
        color: #e5e9f0;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(107, 155, 209, 0.2) !important;
        color: #8bb4de !important;
    }

    .streamlit-expanderHeader {
        background: rgba(23, 30, 40, 0.7) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: #e5e9f0 !important;
        transition: all 0.25s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(107, 155, 209, 0.12) !important;
        transform: translateX(3px);
    }

    .empty-state {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(239, 68, 68, 0.05));
        border-left: 5px solid #f87171;
        padding: 2rem;
        border-radius: 14px;
        text-align: center;
        animation: fadeInUp 0.7s ease-in;
        color: #e5e9f0;
    }

    .stTextInput > div > div > input {
        background: rgba(23, 30, 40, 0.8) !important;
        color: #e5e9f0 !important;
        border: 1px solid rgba(107, 155, 209, 0.2) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6b9bd1 !important;
        box-shadow: 0 0 0 3px rgba(107, 155, 209, 0.15) !important;
    }

    .stSelectbox > div > div {
        background: rgba(23, 30, 40, 0.8) !important;
        border: 1px solid rgba(107, 155, 209, 0.2) !important;
        border-radius: 12px !important;
    }

    .stAlert {
        background: rgba(23, 30, 40, 0.8) !important;
        color: #e5e9f0 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(107, 155, 209, 0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
docs_count = len(st.session_state.get("documents", []))
status_html = (
    f'<span class="tl-chip ok">✅ Indexed: {docs_count} document(s)</span>'
    if docs_count > 0
    else '<span class="tl-chip">📂 No documents indexed</span>'
)

st.markdown(f"""
<div class="tl-header">
    <div>
        <div class="tl-title"><span class="tl-logo">🔍</span>TruthLens</div>
        <div class="tl-sub">Don't just get answers. Get truth.</div>
    </div>
    <div>{status_html}</div>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("### 📂 Upload Documents")
    st.caption("PDF, DOCX, TXT, PNG, JPG")

    uploaded_files = st.file_uploader(
        "Files upload karo",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg", "tiff", "bmp"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    auto_process = st.checkbox("⚡ Auto-process", value=True)

    st.markdown("---")
    st.markdown("### 🌍 Answer Language")

    answer_lang = st.selectbox(
        "Answer kis bhasha mein?",
        ["Auto (same as question)", "English", "Hindi", "Marathi", "Tamil",
         "Bengali", "Telugu", "Gujarati", "Kannada", "Malayalam", "Punjabi", "Urdu"],
        label_visibility="collapsed"
    )

    lang_map = {
        "Auto (same as question)": None,
        "English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta",
        "Bengali": "bn", "Telugu": "te", "Gujarati": "gu", "Kannada": "kn",
        "Malayalam": "ml", "Punjabi": "pa", "Urdu": "ur"
    }

    st.markdown("---")
    st.caption("ALGOTHON'26 · Team 240 · PS: ALG-AI-02")

# ============================================
# PROCESS DOCUMENTS
# ============================================
upload_dir = "data/uploads"
os.makedirs(upload_dir, exist_ok=True)

if uploaded_files:
    current_files = [uf.name for uf in uploaded_files]
    processed_files = st.session_state.get("processed_files", [])
    new_files = [f for f in current_files if f not in processed_files]

    trigger = (auto_process and new_files) or st.sidebar.button("🔄 Process Documents", use_container_width=True)

    if trigger:
        with st.spinner("📂 Processing documents..."):
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
                st.toast(f"✅ {len(documents)} files indexed!", icon="🎉")
                st.success(f"✅ {len(documents)} files indexed!")
                st.rerun()
            else:
                st.toast("❌ Koi file parse nahi hui", icon="🚨")
                st.error("❌ Koi file parse nahi hui.")

            if failed:
                with st.expander(f"⚠️ {len(failed)} failed"):
                    for f in failed:
                        st.write(f"- {f}")

# ============================================
# DOCUMENTS DISPLAY
# ============================================
if "documents" in st.session_state and st.session_state["documents"]:
    with st.expander(f"📚 Indexed Documents ({len(st.session_state['documents'])})"):
        for doc in st.session_state["documents"]:
            lang_name = get_lang_name(doc["language"])
            st.markdown(f"- **{doc['file']}** — {lang_name} — {len(doc['pages'])} pages")

# ============================================
# QUESTION INPUT
# ============================================
st.markdown("---")
st.markdown("### 💬 Ask a Question")

query = st.text_input(
    "Apna sawaal likho:",
    placeholder="Example: When did employee join?",
    label_visibility="collapsed"
)

if st.button("🔍 Investigate", type="primary", use_container_width=True) and query:
    if "documents" not in st.session_state or not st.session_state["documents"]:
        st.toast("📭 No documents available", icon="⚠️")
        st.markdown("""
        <div class="empty-state">
            <h3>📭 No documents available</h3>
            <p>Upload and process at least one document first.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    with st.spinner("🔍 Investigating documents..."):
        q_lang = detect_lang(query)
        query_en = translate(query, "en") if q_lang != "en" else query
        chunks = retrieve(query_en, top_k=5)

        if not chunks:
            st.toast("📭 No evidence found", icon="⚠️")
            st.error("📭 **No evidence found**")
            st.stop()

        # Real conflict detection
        conflict_data = detect_conflict(chunks)

        answerability = check_answerability(chunks, conflict_data, query)
        confidence = calculate_evidence_confidence(chunks, conflict_data)
        counter_evidence = find_counter_evidence(query, chunks)
        gap_data = detect_evidence_gaps(query, chunks, conflict_data)
        evidence_battle = run_evidence_battle(query, chunks)
        temporal_analysis = analyze_temporal_conflicts(chunks)
        source_drift = detect_source_drift(chunks)
        dependency_graph = build_claim_dependency_graph(query, chunks)

        target = lang_map[answer_lang]
        if answerability["level"] in ["strong", "moderate"]:
            answer = get_answer(query, chunks, target)
        else:
            answer = "Cannot determine reliably. " + answerability["reason"]

    # ============================================
    # VERDICT BANNER
    # ============================================
    st.markdown("---")

    if conflict_data.get("conflict"):
        v_class, v_emoji, v_text = "verdict-conflict", "⚠️", "CONFLICT DETECTED"
        v_sub = "Documents contradict each other"
        st.toast("⚠️ Conflict detected!", icon="⚠️")
    elif answerability["level"] in ["cannot_determine", "no_evidence"]:
        v_class, v_emoji, v_text = "verdict-insufficient", "🟡", "INSUFFICIENT EVIDENCE"
        v_sub = answerability["reason"]
    else:
        v_class, v_emoji, v_text = "verdict-supported", "✅", "SUPPORTED"
        v_sub = answerability["reason"]
        st.balloons()

    st.markdown(f"""
    <div class="verdict-banner {v_class}">
        <p class="verdict-title">{v_emoji} {v_text}</p>
        <p class="verdict-subtitle">{v_sub}</p>
    </div>
    """, unsafe_allow_html=True)

    # Animated Confidence
    st.markdown("#### 📊 Evidence Confidence")
    progress_bar = st.progress(0)
    for i in range(confidence['score']):
        progress_bar.progress(i + 1)
        time.sleep(0.005)
    st.markdown(f"**{confidence['score']}%**")

    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Confidence", f"{confidence['score']}%")
    col2.metric("💪 Strength", answerability['label'])
    col3.metric("📚 Sources", len(set(c['file'] for c in chunks)))

    # ============================================
    # TABS
    # ============================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Answer", "⚖️ Evidence", "🔍 Investigation", "📈 Analysis", "🕸️ Graphs"
    ])

    with tab1:
        st.markdown("### 📝 Answer")
        st.info(answer)

        st.markdown("### 📌 Citations")
        for i, c in enumerate(chunks[:5], 1):
            st.markdown(
                f'<div class="tl-source">'
                f'<b>{i}. {c["file"]}</b> — Page {c.get("page", "?")}<br>'
                f'{c["text"][:250]}...'
                f'</div>',
                unsafe_allow_html=True
            )

        with st.expander("📐 How confidence is calculated"):
            st.markdown(f"""
**Formula:**
Confidence = (Relevance × 0.4) + (Agreement × 0.4) + Conflict Penalty

**Your values:**
- Relevance: {confidence['relevance']}%
- Agreement: {confidence['agreement']}%
- Conflict Penalty: {confidence['penalty']}
- **Final: {confidence['score']}%**
            """)

    with tab2:
        st.markdown("### ⚖️ Supporting vs Contradicting Evidence")

        if evidence_battle.get("candidate_answer"):
            st.markdown(f"**Candidate Answer:** {evidence_battle.get('candidate_answer', '')}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🔵 Supporting Evidence")
                supporter = evidence_battle.get("supporter", {})
                claims = supporter.get("claims", [])
                if claims:
                    for claim in claims:
                        st.markdown(f"""
<div class="tl-card tl-card-support">
<b>{claim.get('source', 'Doc')}</b> (Page {claim.get('page', '?')})<br>
{claim.get('claim', '')}<br>
<i>Strength: {claim.get('strength', 'unknown')}</i>
</div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No supporting evidence")

            with col2:
                st.markdown("#### 🔴 Contradicting Evidence")
                skeptic = evidence_battle.get("skeptic", {})
                claims = skeptic.get("claims", [])
                if claims:
                    for claim in claims:
                        st.markdown(f"""
<div class="tl-card tl-card-contradict">
<b>{claim.get('source', 'Doc')}</b> (Page {claim.get('page', '?')})<br>
{claim.get('claim', '')}<br>
<i>Impact: {claim.get('impact', 'unknown')}</i>
</div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No contradicting evidence")

            verdict = evidence_battle.get("verdict", {})
            decision = verdict.get("decision", "insufficient")
            emoji = {"agree": "✅", "conflict": "⚠️", "insufficient": "🟡"}.get(decision, "🟡")
            st.markdown(f"### {emoji} Verdict: **{decision.upper()}**")
            st.caption(verdict.get("reasoning", ""))

    with tab3:
        st.markdown("### 🔍 Investigation Details")

        st.markdown("#### 🛑 Counter-Evidence Search")
        if counter_evidence.get("candidate_answer"):
            st.write(counter_evidence.get("candidate_answer", ""))
            contradicting = counter_evidence.get("contradicting_evidence", [])
            if contradicting:
                for ce in contradicting:
                    st.markdown(f"""
<div class="tl-card tl-card-contradict">
<b>{ce.get('source', 'Doc')}</b> (Page {ce.get('page', '?')})<br>
{ce.get('claim', '')}<br>
<i>{ce.get('impact', '')}</i>
</div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No counter-evidence found")

        st.markdown("#### 🟡 Evidence Gaps")
        if answerability["level"] in ["cannot_determine", "low_relevance", "no_evidence"]:
            gaps = gap_data.get("evidence_gaps", [])
            resolutions = gap_data.get("resolution_evidence", [])
            if gaps:
                st.markdown("**Missing:**")
                for gap in gaps:
                    st.markdown(f"- ❌ **{gap.get('missing', '')}** — *{gap.get('why_needed', '')}*")
            if resolutions:
                st.markdown("**What would resolve this:**")
                for res in resolutions:
                    st.markdown(f"- 📄 **{res.get('document', '')}** — *{res.get('reason', '')}*")
        else:
            st.success("No evidence gaps identified")

    with tab4:
        st.markdown("### 📈 Temporal Truth Engine")
        if temporal_analysis.get("temporal_analysis"):
            ta = temporal_analysis["temporal_analysis"]
            verdict = ta.get("verdict", "no_conflict")
            if verdict == "temporal_progression":
                st.info("⏳ **Temporal progression detected** — not a conflict")
                for change in ta.get("temporal_changes", []):
                    st.markdown(f"""
<div class="tl-card tl-card-info">
<b>{change.get('attribute', '')}</b><br>
From: <code>{change.get('from', '')}</code><br>
To: <code>{change.get('to', '')}</code><br>
<i>{change.get('reason', '')}</i>
</div>
                    """, unsafe_allow_html=True)
            elif verdict == "conflict":
                st.warning("⚠️ **Real temporal conflict detected**")
                for c in ta.get("real_conflicts", []):
                    st.markdown(f"- **{c.get('claim_a', '')}** vs **{c.get('claim_b', '')}** — *{c.get('reason', '')}*")
            else:
                st.success("No temporal conflicts")

        st.markdown("---")
        st.markdown("### 📑 Source Drift Detection")
        if source_drift.get("source_drift"):
            sd = source_drift["source_drift"]
            if sd.get("drift_detected"):
                st.warning(f"Changes across {len(sd.get('documents_compared', []))} documents")
                for change in sd.get("changes", []):
                    sig = change.get("significance", "medium")
                    emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(sig, "🟡")
                    st.markdown(f"""
<div class="tl-card tl-card-warning">
{emoji} <b>{change.get('section', '')}</b> ({change.get('change_type', '')})<br>
Old: <code>{change.get('old_value', '')}</code> — <i>{change.get('old_source', '')}</i><br>
New: <code>{change.get('new_value', '')}</code> — <i>{change.get('new_source', '')}</i>
</div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No source drift detected")

    with tab5:
        st.markdown("### 🕸️ Visual Analysis")
        if dependency_graph.get("dependency_graph"):
            dg = dependency_graph["dependency_graph"]
            if dg.get("claims"):
                st.markdown("#### 🔗 Claim Dependency Graph")
                fig = build_dependency_graph_figure(dg)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                final = dg.get("final_answer", {})
                decision = final.get("decision", "uncertain")
                emoji = {"supported": "✅", "contradicted": "⚠️", "uncertain": "🟡"}.get(decision, "🟡")
                st.markdown(f"**Final Decision:** {emoji} {decision.upper()}")
                st.caption(final.get("reasoning", ""))

        if conflict_data.get("conflict"):
            st.markdown("#### ⚠️ Conflict Graph")
            fig = build_conflict_graph(conflict_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    with st.expander("🔗 Evidence Chain"):
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

↓

**Final Answer:** {'✅ Provided' if answerability['level'] in ['strong', 'moderate'] else '🤷 Cannot determine'}
        """)

st.markdown("---")
st.caption(" TruthLens — Don't just get answers. Get truth.")