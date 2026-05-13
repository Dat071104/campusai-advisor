"""Local embedding providers for CampusAI."""

from __future__ import annotations

from typing import Protocol


class EmbeddingModel(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text."""


class FastEmbedEmbeddingModel:
    """FastEmbed-backed local embedding model.

    The model is imported and initialized lazily so tests can use fakes without
    downloading model files.
    """

    def __init__(self, model_name: str) -> None:
        try:
            from fastembed import TextEmbedding
        except ImportError as exc:
            raise RuntimeError("fastembed is required for local embeddings.") from exc

        self._model = TextEmbedding(model_name=model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [vector.tolist() for vector in self._model.embed(texts)]
