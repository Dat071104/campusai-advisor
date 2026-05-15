"""ChromaDB vector store wrapper."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from campusai.ingestion.chunker import TextChunk


class VectorStore(Protocol):
    def upsert_chunks(self, chunks: list["TextChunk"], embeddings: list[list[float]]) -> int:
        """Persist chunks and return the number written."""


class ChromaVectorStore:
    def __init__(self, persist_path: str, collection_name: str) -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("chromadb is required for the local vector store.") from exc

        self._client = chromadb.PersistentClient(path=persist_path)
        self._collection_name = collection_name
        self._collection = self._client.get_or_create_collection(name=collection_name)

    @property
    def collection(self):
        """Expose the underlying Chroma collection for read-only query adapters."""

        return self._collection

    def reset_collection(self) -> None:
        """Delete the backing collection if it exists, then recreate it empty."""

        try:
            self._client.delete_collection(self._collection_name)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(name=self._collection_name)

    def upsert_chunks(self, chunks: list["TextChunk"], embeddings: list[list[float]]) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        if not chunks:
            return 0

        self._collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks],
            embeddings=embeddings,
        )
        return len(chunks)


def wait_for_chroma_index_ready(
    persist_path: str,
    collection_name: str,
    *,
    expected_min_chunks: int = 1,
    attempts: int = 5,
    sleep_seconds: float = 0.2,
) -> bool:
    """Confirm the collection is readable by a fresh Chroma client.

    Uses a short bounded retry because file persistence can be visible a moment
    after upsert returns, especially right after reset/recreate flows.
    """

    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError("chromadb is required for the local vector store.") from exc

    if expected_min_chunks <= 0:
        return True

    last_count = 0
    for attempt in range(attempts):
        try:
            client = chromadb.PersistentClient(path=persist_path)
            collection = client.get_or_create_collection(name=collection_name)
            last_count = int(collection.count())
            if last_count >= expected_min_chunks:
                return True
        except Exception:
            last_count = 0
        if attempt < attempts - 1:
            time.sleep(sleep_seconds)
    return False
