# app.py
# TruthLens — AI Document Investigator
# ALGOTHON'26 | Team 240 | PS: ALG-AI-02

import streamlit as st
import os
import sys
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
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
    .main-title { font-size: 2.5rem; font-weight: 800; color: #1f77b4; text-align: center; }
    .tagline { text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem; }
    .conflict-box { background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .answer-box { background-color: #f0f8ff; border-left: 5px solid #1f77b4; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .source-box { background-color: #f9f9f9; border-left: 3px solid #999; padding: 0.6rem; border-radius: 6px; margin: 0.4rem 0; font-size: 0.9rem; }
    .counter-box { background-color: #f8d7da; border-left: 5px solid #dc3545; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .gap-box { background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .supporter-box { background-color: #d4edda; border-left: 5px solid #28a745; padding: 1rem; border-radius: 8px; }
    .skeptic-box { background-color: #f8d7da; border-left: 5px solid #dc3545; padding: 1rem; border-radius: 8px; }
    .temporal-box { background-color: #d1ecf1; border-left: 5px solid #17a2b8; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .drift-box { background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .strong { color: #28a745; font-weight: bold; }
    .moderate { color: #ffc107; font-weight: bold; }
    .weak { color: #dc3545; font-weight: bold; }
    .cannot { color: #dc3545; font-weight: bold; }
    .empty-state { background-color: #f8d7da; border-left: 5px solid #dc3545; padding: 1.5rem; border-radius: 8px; text-align: center; }
</style>
""", unsafe_allow_html=True)

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

    auto_process = st.checkbox("⚡ Auto-process", value=True)

    st.header("🌍 Answer Language")
    answer_lang = st.selectbox(
        "Answer kis bhasha mein?",
        [
            "Auto (same as question)",
            "English",
            "Hindi",
            "Marathi",
            "Tamil",
            "Bengali",
            "Telugu",
            "Gujarati",
            "Kannada",
            "Malayalam",
            "Punjabi",
            "Urdu"
        ]
    )

    lang_map = {
        "Auto (same as question)": None,
        "English": "en",
        "Hindi": "hi",
        "Marathi": "mr",
        "Tamil": "ta",
        "Bengali": "bn",
        "Telugu": "te",
        "Gujarati": "gu",
        "Kannada": "kn",
        "Malayalam": "ml",
        "Punjabi": "pa",
        "Urdu": "ur"
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
if "documents" in st.session_state and st.session_state["documents"]:
    with st.expander(f"📚 Indexed Documents ({len(st.session_state['documents'])})"):
        for doc in st.session_state["documents"]:
            lang_name = get_lang_name(doc["language"])
            st.markdown(f"- **{doc['file']}** — {lang_name} — {len(doc['pages'])} pages")

# ---------------- QUESTION INPUT ----------------
st.markdown("---")
st.header("💬 Ask a Question")

query = st.text_input(
    "Apna sawaal likho (kisi bhi bhasha mein):",
    placeholder="Example: Was the employee eligible for promotion?"
)

if st.button("🔍 Investigate") and query:
    if "documents" not in st.session_state or not st.session_state["documents"]:
        st.markdown('<div class="empty-state">', unsafe_allow_html=True)
        st.markdown("### 📭 No documents available")
        st.markdown("Upload and process at least one document before asking a question.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    with st.spinner("Investigating..."):
        q_lang = detect_lang(query)

        if q_lang != "en":
            query_en = translate(query, "en")
        else:
            query_en = query

        chunks = retrieve(query_en, top_k=30)

        if not chunks:
            st.error("📭 **No evidence found**")
            st.info("No relevant documents found for this question.")
            st.stop()

        conflict_data = {"conflict": False, "pairs": [], "claims": []}

        answerability = check_answerability(chunks, conflict_data, query)
        confidence = calculate_evidence_confidence(chunks, conflict_data)

        # All investigation features
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
            answer = "🤷 Cannot determine reliably. " + answerability["reason"]

    # ---------------- CONFLICT DISPLAY ----------------
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

    level = answerability["level"]
    css_class = level if level in ["strong", "moderate", "weak"] else "cannot"
    st.markdown(
        f"**Evidence Strength:** <span class='{css_class}'>{answerability['label']}</span>",
        unsafe_allow_html=True
    )
    st.caption(answerability["reason"])

    st.markdown("### 📊 Evidence Confidence")
    st.progress(confidence["score"] / 100)
    st.markdown(f"**{confidence['score']}%**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Relevance", f"{confidence['relevance']}%")
    col2.metric("Agreement", f"{confidence['agreement']}%")
    col3.metric("Conflict Penalty", confidence["penalty"])

    # ---------------- TEMPORAL TRUTH ENGINE ----------------
    if temporal_analysis.get("temporal_analysis"):
        ta = temporal_analysis["temporal_analysis"]
        verdict = ta.get("verdict", "no_conflict")

        if verdict == "temporal_progression":
            st.markdown('<div class="temporal-box">', unsafe_allow_html=True)
            st.markdown("### ⏳ Temporal Progression Detected")
            st.info("The apparent conflict is a **time-based change**, not a contradiction.")

            changes = ta.get("temporal_changes", [])
            if changes:
                st.markdown("**What changed over time:**")
                for change in changes:
                    st.markdown(f"""
- **{change.get('attribute', '')}**
  - From: `{change.get('from', '')}`
  - To: `{change.get('to', '')}`
  - Reason: *{change.get('reason', '')}*
                    """)
            st.markdown('</div>', unsafe_allow_html=True)

        elif verdict == "conflict":
            st.markdown('<div class="temporal-box">', unsafe_allow_html=True)
            st.markdown("### ⚠️ Real Temporal Conflict")
            st.warning("Same-time contradiction detected.")
            conflicts = ta.get("real_conflicts", [])
            for c in conflicts:
                st.markdown(f"""
- **{c.get('claim_a', '')}** vs **{c.get('claim_b', '')}**
  - *{c.get('reason', '')}*
                """)
            st.markdown('</div>', unsafe_allow_html=True)

        timeline = ta.get("claims_timeline", [])
        if timeline:
            with st.expander("📅 Claims Timeline"):
                for item in timeline:
                    st.markdown(f"""
- **{item.get('temporal_context', '?')}**: {item.get('value', '')}
  - *{item.get('claim', '')}*
  - Source: {item.get('source', '')} (Page {item.get('page', '?')})
                    """)

    # ---------------- SOURCE DRIFT DETECTION ----------------
    if source_drift.get("source_drift"):
        sd = source_drift["source_drift"]
        if sd.get("drift_detected"):
            st.markdown('<div class="drift-box">', unsafe_allow_html=True)
            st.markdown("### 📑 Source Drift Detected")
            st.warning(f"Changes found across {len(sd.get('documents_compared', []))} documents")

            st.markdown(f"**Documents compared:** {', '.join(sd.get('documents_compared', []))}")

            changes = sd.get("changes", [])
            if changes:
                st.markdown("**Changes detected:**")
                for change in changes:
                    sig = change.get("significance", "medium")
                    emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(sig, "🟡")
                    st.markdown(f"""
{emoji} **{change.get('section', '')}** ({change.get('change_type', '')})
- Old: `{change.get('old_value', '')}` — *{change.get('old_source', '')}*
- New: `{change.get('new_value', '')}` — *{change.get('new_source', '')}*
                    """)

            st.caption(sd.get("summary", ""))
            st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- CLAIM DEPENDENCY GRAPH ----------------
    if dependency_graph.get("dependency_graph"):
        dg = dependency_graph["dependency_graph"]
        if dg.get("claims"):
            st.markdown("### 🔗 Claim Dependency Graph")

            fig = build_dependency_graph_figure(dg)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            final = dg.get("final_answer", {})
            decision = final.get("decision", "uncertain")
            emoji = {"supported": "✅", "contradicted": "⚠️", "uncertain": "🟡"}.get(decision, "🟡")

            st.markdown(f"### {emoji} Final Decision: **{decision.upper()}**")
            st.caption(final.get("reasoning", ""))

            with st.expander("📋 All Claims"):
                for claim in dg.get("claims", []):
                    st.markdown(f"""
**{claim.get('id', 'C')}: {claim.get('claim', '')}**
- Confidence: {claim.get('confidence', 'medium')}
- Supporting: {len(claim.get('supporting', []))} sources
- Contradicting: {len(claim.get('contradicting', []))} sources
                    """)

    # ---------------- EVIDENCE BATTLE ----------------
    if evidence_battle.get("candidate_answer"):
        st.markdown("---")
        st.markdown("### ⚖️ Evidence Battle")
        st.markdown(f"**Candidate Answer:** {evidence_battle.get('candidate_answer', '')}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="supporter-box">', unsafe_allow_html=True)
            st.markdown("#### 🔵 Supporter")
            st.caption("*Why the answer is TRUE*")
            supporter = evidence_battle.get("supporter", {})
            claims = supporter.get("claims", [])
            if claims:
                for claim in claims:
                    st.markdown(f"""
- **{claim.get('source', 'Doc')}** (Page {claim.get('page', '?')})
  - {claim.get('claim', '')}
  - *Strength: {claim.get('strength', 'unknown')}*
                    """)
                st.markdown(f"**Total: {supporter.get('total_claims', len(claims))} claims**")
            else:
                st.caption("No supporting evidence found")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="skeptic-box">', unsafe_allow_html=True)
            st.markdown("#### 🔴 Skeptic")
            st.caption("*Why the answer might be FALSE*")
            skeptic = evidence_battle.get("skeptic", {})
            claims = skeptic.get("claims", [])
            if claims:
                for claim in claims:
                    st.markdown(f"""
- **{claim.get('source', 'Doc')}** (Page {claim.get('page', '?')})
  - {claim.get('claim', '')}
  - *Impact: {claim.get('impact', 'unknown')}*
  - *Type: {claim.get('type', '')}*
                    """)
                st.markdown(f"**Total: {skeptic.get('total_claims', len(claims))} claims**")
            else:
                st.caption("No contradicting evidence found")

            missing = skeptic.get("missing_evidence", [])
            if missing:
                st.markdown("**Missing Evidence:**")
                for m in missing:
                    st.markdown(f"- ❌ {m}")
            st.markdown('</div>', unsafe_allow_html=True)

        verdict = evidence_battle.get("verdict", {})
        decision = verdict.get("decision", "insufficient")

        decision_display = {
            "agree": ("✅", "AGREE", "Evidence supports the answer"),
            "conflict": ("⚠️", "CONFLICT", "Evidence contradicts the answer"),
            "insufficient": ("🟡", "INSUFFICIENT", "Not enough evidence")
        }.get(decision, ("🟡", "UNCERTAIN", "Cannot determine"))

        emoji, label, desc = decision_display

        st.markdown("---")
        st.markdown(f"### {emoji} Verdict: **{label}**")
        st.markdown(f"*{desc}*")
        st.caption(verdict.get("reasoning", ""))

        col1, col2, col3 = st.columns(3)
        col1.metric("Supporting", verdict.get("supporting_count", 0))
        col2.metric("Counter", verdict.get("counter_count", 0))
        col3.metric("Critical Missing", verdict.get("critical_missing", "—"))
        st.markdown("---")

    # ---------------- EVIDENCE GAP ----------------
    if answerability["level"] in ["cannot_determine", "low_relevance", "no_evidence"]:
        gaps = gap_data.get("evidence_gaps", [])
        resolutions = gap_data.get("resolution_evidence", [])

        if gaps or resolutions:
            st.markdown('<div class="gap-box">', unsafe_allow_html=True)
            st.markdown("### 🟡 Missing Evidence")

            if gaps:
                st.markdown("**What is missing:**")
                for gap in gaps:
                    st.markdown(f"""
- ❌ **{gap.get('missing', '')}**
  - *{gap.get('why_needed', '')}*
                    """)

            if resolutions:
                st.markdown("**What would resolve this:**")
                for res in resolutions:
                    st.markdown(f"""
- 📄 **{res.get('document', '')}**
  - *{res.get('reason', '')}*
                    """)

            st.markdown('</div>', unsafe_allow_html=True)

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

st.markdown("---")
st.caption("Built with ❤️ for ALGOTHON'26 | TruthLens — Don't just get answers. Get truth.")