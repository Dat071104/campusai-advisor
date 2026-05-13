"""Index local academic PDFs into the local vector store."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from campusai.config import Settings, get_settings
from campusai.ingestion.chunker import TextChunk, chunk_pages
from campusai.ingestion.pdf_loader import DocumentPage, find_pdf_files, load_pdf_pages
from campusai.rag.embeddings import EmbeddingModel, FastEmbedEmbeddingModel
from campusai.rag.vector_store import ChromaVectorStore, VectorStore


PageLoader = Callable[[Path], list[DocumentPage]]


@dataclass(frozen=True)
class IndexingResult:
    raw_data_dir: str
    pdf_files_found: int
    pages_loaded: int
    chunks_created: int
    chunks_indexed: int
    skipped_files: tuple[str, ...]

    @property
    def message(self) -> str:
        if self.pdf_files_found == 0:
            return f"No PDF files found in {self.raw_data_dir}."
        return (
            f"Indexed {self.chunks_indexed} chunks from {self.pages_loaded} pages "
            f"across {self.pdf_files_found} PDF file(s)."
        )


def index_local_documents(
    settings: Settings | None = None,
    *,
    page_loader: PageLoader = load_pdf_pages,
    embedding_model: EmbeddingModel | None = None,
    vector_store: VectorStore | None = None,
) -> IndexingResult:
    settings = settings or get_settings()
    raw_data_dir = Path(settings.raw_data_path)
    pdf_files = find_pdf_files(raw_data_dir)
    skipped_files: list[str] = []
    pages: list[DocumentPage] = []

    for pdf_file in pdf_files:
        try:
            loaded_pages = page_loader(pdf_file)
        except Exception:
            skipped_files.append(str(pdf_file))
            continue
        if loaded_pages:
            pages.extend(loaded_pages)
        else:
            skipped_files.append(str(pdf_file))

    chunks = chunk_pages(
        pages,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    if not chunks:
        return IndexingResult(
            raw_data_dir=str(raw_data_dir),
            pdf_files_found=len(pdf_files),
            pages_loaded=len(pages),
            chunks_created=0,
            chunks_indexed=0,
            skipped_files=tuple(skipped_files),
        )

    embedding_model = embedding_model or FastEmbedEmbeddingModel(settings.embedding_model)
    vector_store = vector_store or ChromaVectorStore(
        persist_path=settings.vector_store_path,
        collection_name=settings.chroma_collection,
    )

    embeddings = embedding_model.embed([chunk.text for chunk in chunks])
    indexed_count = vector_store.upsert_chunks(chunks, embeddings)

    return IndexingResult(
        raw_data_dir=str(raw_data_dir),
        pdf_files_found=len(pdf_files),
        pages_loaded=len(pages),
        chunks_created=len(chunks),
        chunks_indexed=indexed_count,
        skipped_files=tuple(skipped_files),
    )
