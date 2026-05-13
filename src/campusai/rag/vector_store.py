"""ChromaDB vector store wrapper."""

from __future__ import annotations

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
