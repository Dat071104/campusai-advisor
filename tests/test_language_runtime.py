"""English defaults and absence of Vietnamese runtime strings in RAG + Groq client."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from campusai.config import Settings
from campusai.rag.prompts import SYSTEM_PROMPT
from campusai.services.groq_client import GroqChatClient

# Vietnamese Latin extended range used by prior UI/prompt strings (not typical English UI copy).
_VIETNAMESE_DIACRITICS_RE = re.compile(r"[\u0102-\u0111\u0128-\u024f\u1e00-\u1ef9]")


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _iter_rag_and_groq_py_files() -> list[Path]:
    root = _project_root()
    rag = root / "src" / "campusai" / "rag"
    svc = root / "src" / "campusai" / "services" / "groq_client.py"
    return sorted(rag.glob("*.py")) + [svc]


@pytest.mark.parametrize("path", _iter_rag_and_groq_py_files(), ids=lambda p: p.name)
def test_no_vietnamese_diacritics_in_rag_and_groq_services(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    match = _VIETNAMESE_DIACRITICS_RE.search(text)
    assert match is None, f"Unexpected non-ASCII/Vietnamese-range character in {path}"


def test_system_prompt_defaults_to_english() -> None:
    assert "Answer in English" in SYSTEM_PROMPT
    assert "Vietnamese" in SYSTEM_PROMPT  # explicit opt-in for other languages


def test_groq_missing_key_message_is_english() -> None:
    settings = Settings(
        groq_api_key=None,
        groq_base_url="https://api.groq.com/openai/v1",
        groq_model="llama-3.3-70b-versatile",
        embedding_provider="fastembed",
        embedding_model="test-model",
        embedding_dim=3,
        vector_store_provider="local",
        vector_store_path="data/vector_db",
        chroma_collection="test",
        raw_data_path="data/raw",
        chunk_size=800,
        chunk_overlap=150,
        groq_timeout_seconds=30,
        groq_min_seconds_between_requests=3,
        groq_max_retries=2,
        groq_max_tokens=900,
        rag_top_k=5,
        campusai_api_base_url=None,
    )
    client = GroqChatClient(settings)
    response = client.generate("test prompt", system_prompt="You are a test assistant.")
    assert response.error == "missing_api_key"
    assert "GROQ_API_KEY" in response.content
    assert _VIETNAMESE_DIACRITICS_RE.search(response.content) is None
