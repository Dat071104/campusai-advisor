"""Streamlit entrypoint for the CampusAI Advisor MVP."""

from __future__ import annotations

import json
import time
from pathlib import Path

import streamlit as st

from campusai.config import Settings, get_settings
from campusai.rag.answer_chain import RAGAnswerChain
from campusai.rag.retriever import index_exists

MANIFEST_PATH = Path("data/processed/source_manifest.json")


def _manifest_entry_count() -> tuple[bool, int]:
    """Return (exists, entry_count) for the public dataset manifest."""
    if not MANIFEST_PATH.is_file():
        return False, 0
    try:
        payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True, 0
    if isinstance(payload, list):
        return True, len(payload)
    if isinstance(payload, dict):
        for key in ("sources", "entries", "files"):
            value = payload.get(key)
            if isinstance(value, list):
                return True, len(value)
        return True, len(payload)
    return True, 0


def render_profile_sidebar() -> dict[str, str]:
    st.sidebar.header("Student profile")
    st.sidebar.caption(
        "Used to personalize tone and study-path suggestions. "
        "Document-backed claims still require matching indexed sources."
    )
    profile = {
        "major": st.sidebar.text_input("Major", value="Computer Science"),
        "academic_year": st.sidebar.selectbox(
            "Academic year",
            ["Year 1", "Year 2", "Year 3", "Year 4"],
            index=1,
        ),
        "career_goal": st.sidebar.text_input("Career goal", value="Backend + AI Engineer"),
        "completed_courses": st.sidebar.text_area("Completed courses", placeholder="Data Structures, Databases, ..."),
        "interests": st.sidebar.text_area("Interests", placeholder="AI, backend systems, data, security, ..."),
        "learning_goals": st.sidebar.text_area(
            "Weak areas or learning goals",
            placeholder="Math, English, algorithms, ...",
        ),
    }
    st.sidebar.divider()
    st.sidebar.info(
        "**Local advisor rules** (if present in your index) are **heuristic study guidance**, "
        "not official university policy."
    )
    return profile


def render_document_sidebar() -> None:
    st.sidebar.header("Documents & indexing")
    settings = get_settings()
    uploaded_files = st.sidebar.file_uploader(
        "Upload academic documents (staged)",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )
    st.sidebar.button(
        "Index uploaded documents",
        disabled=True,
        help="MVP indexes PDF, Markdown, and .txt files from disk under data/raw. Run: python -m campusai.index_documents",
    )
    st.sidebar.caption(f"CLI reads PDFs from: `{settings.raw_data_path}`")
    if uploaded_files:
        st.sidebar.warning(
            "Upload UI is staged only. For this MVP, copy files into `data/raw` and run the index CLI."
        )
    else:
        st.sidebar.caption("No files selected.")


def render_status(settings: Settings, has_index: bool, manifest_exists: bool, manifest_count: int) -> None:
    st.sidebar.header("System status")
    if has_index:
        st.sidebar.success("Vector index: embedded chunks detected.")
    else:
        st.sidebar.warning(
            "No vector index detected. Run `python -m campusai.index_documents` after adding PDFs, Markdown, or .txt files under data/raw."
        )
    if manifest_exists:
        st.sidebar.info(f"Dataset manifest on disk: {manifest_count} source record(s).")
    else:
        st.sidebar.caption(
            "No `data/processed/source_manifest.json` yet. Optional: `python -m campusai.fetch_public_dataset`."
        )
    st.sidebar.caption(f"Groq model: `{settings.groq_model}`")
    st.sidebar.caption(f"Embeddings: {settings.embedding_provider} / {settings.embedding_model}")
    st.sidebar.caption(f"Vector store path: `{settings.vector_store_path}`")
    st.sidebar.caption(f"Retrieval top_k: {settings.rag_top_k}")
    if settings.has_groq_key:
        st.sidebar.success("Groq API key: configured (local or environment).")
    else:
        st.sidebar.warning("Groq API key: not configured — answers stay local/heuristic without LLM.")
    st.sidebar.caption(
        f"Live request spacing: ≥ {settings.groq_min_seconds_between_requests:g}s between Groq calls "
        "(anti-spam / free-tier safety)."
    )


def render_dataset_index_panel(
    settings: Settings,
    has_index: bool,
    manifest_exists: bool,
    manifest_count: int,
) -> None:
    st.subheader("Dataset & index status")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(
            "Source manifest",
            f"{manifest_count} entries" if manifest_exists else "Not found",
            help="Produced by `python -m campusai.fetch_public_dataset` (public sources + local heuristics).",
        )
    with m2:
        st.metric(
            "Vector index",
            "Ready" if has_index else "Not indexed",
            help=f"Chroma collection `{settings.chroma_collection}` under `{settings.vector_store_path}`.",
        )
    with m3:
        st.metric(
            "Groq LLM",
            "Key present" if settings.has_groq_key else "Missing key",
            help="Set `GROQ_API_KEY` in local `.env` or Streamlit Cloud Secrets. Never commit keys.",
        )


def render_help_safety_expander() -> None:
    with st.expander("Help, safety & limitations", expanded=False):
        st.markdown(
            """
- **Heuristic sources:** text labeled as local advisor heuristics is **not** official policy.
- **Groq:** the app **does not** call Groq on startup — only after you submit **Ask CampusAI**.
- **Empty retrieval:** if no chunks match, the assistant refuses to invent prerequisites or policies.
- **Rate limits / timeouts:** wait and retry; avoid rapid repeated submits.
- **Manual live smoke test:** configure `.env`, then ask exactly one safe question first — see `README.md`.
            """.strip()
        )


def render_citations(result) -> None:
    if not result.citations:
        st.caption("No citation rows for this answer (common when retrieval is empty).")
        return
    st.markdown("##### Citations")
    for idx, citation in enumerate(result.citations, start=1):
        page = f"p. {citation.page_number}" if citation.page_number is not None else "page n/a"
        title = f"[{idx}] {citation.source} — {page}"
        with st.expander(title, expanded=(idx == 1)):
            st.markdown(f"**Authority:** {citation.authority_label}")
            if citation.excerpt:
                st.markdown("**Excerpt:**")
                st.write(citation.excerpt)
            with st.expander("Technical details (chunk id, path, score)", expanded=False):
                st.code(citation.chunk_id, language=None)
                if citation.source_path:
                    st.caption(f"Path: `{citation.source_path}`")
                if citation.distance is not None:
                    st.caption(f"Distance: {citation.distance:.4f}")


def render_chat(student_profile: dict[str, str], has_index: bool) -> None:
    settings = get_settings()
    st.subheader("Question & answer")
    st.caption(
        "Submit a single question. The app retrieves top chunks, builds citations, then calls Groq only for that request."
    )

    if not has_index:
        st.error(
            "**No index found.** Add PDFs, Markdown, or .txt files to `data/raw`, run `python -m campusai.index_documents`, then refresh this page."
        )
    if not settings.has_groq_key:
        st.warning(
            "**No Groq key configured.** Retrieval can still run, but full LLM answers need `GROQ_API_KEY` "
            "(local `.env` or deployment secrets)."
        )

    if "last_groq_submit_at" not in st.session_state:
        st.session_state.last_groq_submit_at = 0.0
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_question" not in st.session_state:
        st.session_state.last_question = ""

    with st.form("rag_question_form", clear_on_submit=False):
        question = st.text_area(
            "Your question",
            placeholder="What should I learn before Machine Learning?",
            height=110,
            label_visibility="visible",
        )
        submitted = st.form_submit_button(
            "Ask CampusAI",
            type="primary",
            disabled=st.session_state.get("request_running", False),
            help="Respects a minimum delay between live Groq calls to reduce accidental spam.",
        )

    if submitted:
        now = time.monotonic()
        wait_remaining = settings.groq_min_seconds_between_requests - (now - st.session_state.last_groq_submit_at)
        if wait_remaining > 0:
            st.info(
                f"**Please wait {wait_remaining:.1f}s** before another live Groq request "
                "(rate-limit / free-tier safeguard)."
            )
        else:
            cleaned = question.strip()
            if not cleaned:
                st.warning("Enter a non-empty question before submitting.")
            else:
                st.session_state.request_running = True
                with st.spinner("Retrieving chunks and generating an answer…"):
                    chain = RAGAnswerChain(settings=settings)
                    result = chain.answer_question(question, student_profile)
                    st.session_state.last_result = result
                    st.session_state.last_question = question
                    if result.used_live_api:
                        st.session_state.last_groq_submit_at = time.monotonic()
                st.session_state.request_running = False

    result = st.session_state.last_result
    if not result:
        st.info("Ask a question above to see the answer and citations here.")
        return

    st.divider()
    st.markdown("### Last answer")
    with st.chat_message("user"):
        st.write(st.session_state.last_question)
    with st.chat_message("assistant"):
        st.write(result.answer)

        if result.no_context:
            st.warning(
                "**No relevant chunks found** for this question (or empty question). "
                "The assistant should not invent policy or prerequisites beyond indexed evidence."
            )
        if result.missing_api_key:
            st.info(
                "**Groq API key missing** — configure `GROQ_API_KEY` to enable live LLM completions."
            )
        if result.error in {"rate_limited", "timeout"}:
            st.warning(
                f"**Groq request issue ({result.error})** — wait and retry later. Message: {result.answer}"
            )
        elif result.error and result.error not in {"missing_api_key"}:
            st.warning(f"**Request issue:** {result.answer}")

        render_citations(result)


def main() -> None:
    st.set_page_config(page_title="CampusAI Advisor", layout="wide", initial_sidebar_state="expanded")
    settings = get_settings()
    has_index = index_exists(settings)
    manifest_exists, manifest_count = _manifest_entry_count()

    st.title("CampusAI Advisor")
    st.caption(
        "Portfolio MVP: ask study-path and catalog-style questions against **your indexed documents**, "
        "with **authority-labeled citations** and optional **Groq** generation."
    )
    render_dataset_index_panel(settings, has_index, manifest_exists, manifest_count)
    st.divider()
    render_help_safety_expander()
    st.divider()

    student_profile = render_profile_sidebar()
    render_document_sidebar()
    render_status(settings, has_index, manifest_exists, manifest_count)

    render_chat(student_profile=student_profile, has_index=has_index)


if __name__ == "__main__":
    main()
