"""Runtime settings for CampusAI Advisor."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value else default


@dataclass(frozen=True)
class Settings:
    """Environment-backed settings with safe MVP defaults."""

    groq_api_key: str | None
    groq_api_key_2: str | None
    groq_api_key_3: str | None
    groq_base_url: str
    groq_model: str
    embedding_provider: str
    embedding_model: str
    vector_store_provider: str
    vector_store_path: str
    raw_data_path: str

    @property
    def has_groq_key(self) -> bool:
        return bool(self.groq_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from environment variables and optional local .env."""

    load_dotenv()

    return Settings(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        groq_api_key_2=os.getenv("GROQ_API_KEY_2"),
        groq_api_key_3=os.getenv("GROQ_API_KEY_3"),
        groq_base_url=_env("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        groq_model=_env("GROQ_MODEL", "llama-3.3-70b-versatile"),
        embedding_provider=_env("EMBEDDING_PROVIDER", "fastembed"),
        embedding_model=_env("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
        vector_store_provider=_env("VECTOR_STORE_PROVIDER", "local"),
        vector_store_path=_env("VECTOR_STORE_PATH", "data/vector_db"),
        raw_data_path=_env("RAW_DATA_PATH", "data/raw"),
    )
