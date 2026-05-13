"""Document ingestion pipeline for CampusAI Advisor."""

from campusai.ingestion.chunker import TextChunk, chunk_pages
from campusai.ingestion.indexer import IndexingResult, index_local_documents
from campusai.ingestion.pdf_loader import DocumentPage, load_pdf_pages

__all__ = [
    "DocumentPage",
    "IndexingResult",
    "TextChunk",
    "chunk_pages",
    "index_local_documents",
    "load_pdf_pages",
]
