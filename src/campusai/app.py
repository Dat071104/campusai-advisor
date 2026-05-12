"""Streamlit entrypoint for the CampusAI Advisor MVP."""

from __future__ import annotations

import streamlit as st

from campusai.config import get_settings


def render_profile_sidebar() -> None:
    st.sidebar.header("Student Profile")
    st.sidebar.text_input("Major", value="Computer Science")
    st.sidebar.selectbox("Academic year", ["Year 1", "Year 2", "Year 3", "Year 4"], index=1)
    st.sidebar.text_input("Career goal", value="Backend + AI Engineer")
    st.sidebar.text_area("Completed courses", placeholder="Data Structures, Databases, ...")
    st.sidebar.text_area("Interests", placeholder="AI, backend systems, data, security, ...")
    st.sidebar.text_area("Weak areas or learning goals", placeholder="Math, English, algorithms, ...")


def render_document_sidebar() -> None:
    st.sidebar.header("Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Upload academic documents",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )
    st.sidebar.button("Index documents", disabled=True, help="Document indexing starts in a later phase.")
    if uploaded_files:
        st.sidebar.info("Upload UI is ready. Indexing is not implemented in Phase 1.")
    else:
        st.sidebar.caption("No documents selected.")


def render_status() -> None:
    settings = get_settings()
    st.sidebar.header("System Status")
    st.sidebar.success("App foundation loaded")
    st.sidebar.caption(f"Groq model: {settings.groq_model}")
    st.sidebar.caption(f"Embeddings: {settings.embedding_provider}")
    st.sidebar.caption("Groq key detected" if settings.has_groq_key else "Groq key not configured")


def render_chat_placeholder() -> None:
    st.subheader("Advisor Chat")
    st.info(
        "Phase 1 placeholder: chat, retrieval, citations, and Groq calls are intentionally not implemented yet."
    )

    question = st.chat_input("Ask about courses, prerequisites, policies, or study direction")
    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            st.write(
                "The system does not have enough source evidence yet because document ingestion and retrieval are not implemented in Phase 1."
            )
            with st.expander("Sources"):
                st.caption("No citations available until documents are indexed in a later phase.")


def main() -> None:
    st.set_page_config(page_title="CampusAI Advisor", layout="wide")

    render_profile_sidebar()
    render_document_sidebar()
    render_status()

    st.title("CampusAI Advisor")
    st.write(
        "A university-focused academic advising assistant that will answer from uploaded academic documents with visible citations."
    )
    render_chat_placeholder()


if __name__ == "__main__":
    main()
