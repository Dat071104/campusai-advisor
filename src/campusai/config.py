"""Runtime settings for CampusAI Advisor."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value else default


def _dotenv_disabled() -> bool:
    value = os.getenv("PYTHON_DOTENV_DISABLED", "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Environment-backed settings with safe MVP defaults."""

    groq_api_key: str | None
    groq_base_url: str
    groq_model: str
    embedding_provider: str
    embedding_model: str
    embedding_dim: int
    vector_store_provider: str
    vector_store_path: str
    chroma_collection: str
    raw_data_path: str
    chunk_size: int
    chunk_overlap: int
    groq_timeout_seconds: int
    groq_min_seconds_between_requests: float
    groq_max_retries: int
    groq_max_tokens: int
    rag_top_k: int
    campusai_api_base_url: str | None

    @property
    def has_groq_key(self) -> bool:
        return bool(self.groq_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from environment variables and optional local .env."""

    if not _dotenv_disabled():
        load_dotenv()

    return Settings(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        groq_base_url=_env("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        groq_model=_env("GROQ_MODEL", "llama-3.3-70b-versatile"),
        embedding_provider=_env("EMBEDDING_PROVIDER", "fastembed"),
        embedding_model=_env("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
        embedding_dim=int(_env("EMBEDDING_DIM", "384")),
        vector_store_provider=_env("VECTOR_STORE_PROVIDER", "local"),
        vector_store_path=_env("VECTOR_STORE_PATH", "data/vector_db"),
        chroma_collection=_env("CHROMA_COLLECTION", "campusai_documents"),
        raw_data_path=_env("RAW_DATA_DIR", _env("RAW_DATA_PATH", "data/raw")),
        chunk_size=int(_env("CHUNK_SIZE", "800")),
        chunk_overlap=int(_env("CHUNK_OVERLAP", "150")),
        groq_timeout_seconds=int(_env("GROQ_TIMEOUT_SECONDS", "30")),
        groq_min_seconds_between_requests=float(_env("GROQ_MIN_SECONDS_BETWEEN_REQUESTS", "3")),
        groq_max_retries=int(_env("GROQ_MAX_RETRIES", "2")),
        groq_max_tokens=int(_env("GROQ_MAX_TOKENS", "900")),
        rag_top_k=int(_env("RAG_TOP_K", "5")),
        campusai_api_base_url=os.getenv("CAMPUSAI_API_BASE_URL") or None,
    )
