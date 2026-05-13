"""Streamlit entrypoint for the CampusAI Advisor MVP."""

from __future__ import annotations

import time

import streamlit as st

from campusai.config import get_settings
from campusai.rag.answer_chain import RAGAnswerChain
from campusai.rag.retriever import index_exists


def render_profile_sidebar() -> dict[str, str]:
    st.sidebar.header("Student Profile")
    return {
        "major": st.sidebar.text_input("Major", value="Computer Science"),
        "academic_year": st.sidebar.selectbox("Academic year", ["Year 1", "Year 2", "Year 3", "Year 4"], index=1),
        "career_goal": st.sidebar.text_input("Career goal", value="Backend + AI Engineer"),
        "completed_courses": st.sidebar.text_area("Completed courses", placeholder="Data Structures, Databases, ..."),
        "interests": st.sidebar.text_area("Interests", placeholder="AI, backend systems, data, security, ..."),
        "learning_goals": st.sidebar.text_area("Weak areas or learning goals", placeholder="Math, English, algorithms, ..."),
    }


def render_document_sidebar() -> None:
    st.sidebar.header("Documents")
    settings = get_settings()
    uploaded_files = st.sidebar.file_uploader(
        "Upload academic documents",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )
    st.sidebar.button("Index uploaded documents", disabled=True, help="Phase 3 indexes staged local files with the CLI command.")
    st.sidebar.caption(f"Local index command reads `{settings.raw_data_path}`.")
    if uploaded_files:
        st.sidebar.info("Upload UI is staged. For this MVP, place files in data/raw and run `python -m campusai.index_documents`.")
    else:
        st.sidebar.caption("No documents selected.")


def render_status(has_index: bool) -> None:
    settings = get_settings()
    st.sidebar.header("System Status")
    st.sidebar.success("Vector index ready" if has_index else "No indexed chunks detected")
    st.sidebar.caption(f"Groq model: {settings.groq_model}")
    st.sidebar.caption(f"Embeddings: {settings.embedding_provider} / {settings.embedding_model}")
    st.sidebar.caption(f"Vector store: {settings.vector_store_path}")
    st.sidebar.caption(f"Top K: {settings.rag_top_k}")
    st.sidebar.caption("Groq key detected" if settings.has_groq_key else "Groq key not configured")


def render_citations(result) -> None:
    if not result.citations:
        st.caption("No citations returned.")
        return
    for idx, citation in enumerate(result.citations, start=1):
        page = f"page {citation.page_number}" if citation.page_number is not None else "page unknown"
        with st.expander(f"[{idx}] {citation.source} — {citation.authority_label}"):
            st.write(f"Location: {page}, chunk `{citation.chunk_id}`")
            if citation.source_path:
                st.caption(f"Path: {citation.source_path}")
            if citation.distance is not None:
                st.caption(f"Distance: {citation.distance:.4f}")
            if citation.excerpt:
                st.write(citation.excerpt)


def render_chat(student_profile: dict[str, str], has_index: bool) -> None:
    settings = get_settings()
    st.subheader("Advisor Chat")
    if not has_index:
        st.warning("No vector DB/index found or no chunks are indexed. Run `python -m campusai.index_documents` after staging public/local documents.")
    if not settings.has_groq_key:
        st.warning("GROQ_API_KEY is not configured. Retrieval can run, but live LLM answers need a local .env key.")

    if "last_groq_submit_at" not in st.session_state:
        st.session_state.last_groq_submit_at = 0.0
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_question" not in st.session_state:
        st.session_state.last_question = ""

    with st.form("rag_question_form", clear_on_submit=False):
        question = st.text_area(
            "Question",
            placeholder="Trước khi học Machine Learning thì nên học gì?",
            height=100,
        )
        submitted = st.form_submit_button("Ask CampusAI", disabled=st.session_state.get("request_running", False))

    if submitted:
        now = time.monotonic()
        wait_remaining = settings.groq_min_seconds_between_requests - (now - st.session_state.last_groq_submit_at)
        if wait_remaining > 0:
            st.info(f"Please wait {wait_remaining:.1f}s before sending another live request.")
        else:
            st.session_state.request_running = True
            with st.spinner("Retrieving documents and preparing answer..."):
                chain = RAGAnswerChain(settings=settings)
                result = chain.answer_question(question, student_profile)
                st.session_state.last_result = result
                st.session_state.last_question = question
                if result.used_live_api:
                    st.session_state.last_groq_submit_at = time.monotonic()
            st.session_state.request_running = False

    result = st.session_state.last_result
    if result:
        with st.chat_message("user"):
            st.write(st.session_state.last_question)
        with st.chat_message("assistant"):
            st.write(result.answer)
            if result.no_context:
                st.warning("No relevant documents found for this question.")
            if result.missing_api_key:
                st.info("Configure GROQ_API_KEY in local .env to generate full answers.")
            if result.error in {"rate_limited", "timeout"}:
                st.warning(result.answer)
            st.markdown("#### Citations")
            render_citations(result)


def main() -> None:
    st.set_page_config(page_title="CampusAI Advisor", layout="wide")
    settings = get_settings()
    has_index = index_exists(settings)

    student_profile = render_profile_sidebar()
    render_document_sidebar()
    render_status(has_index)

    st.title("CampusAI Advisor")
    st.write("Ask academic advising questions grounded in indexed public/demo documents, with source authority clearly labeled.")
    render_chat(student_profile, has_index)


if __name__ == "__main__":
    main()
