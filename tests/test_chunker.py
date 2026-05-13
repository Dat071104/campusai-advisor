import pytest

from campusai.ingestion.chunker import chunk_pages
from campusai.ingestion.pdf_loader import DocumentPage


def test_chunk_pages_preserves_metadata():
    page = DocumentPage(
        text="A" * 60,
        source="catalog.pdf",
        page_number=3,
        source_path="data/raw/catalog.pdf",
    )

    chunks = chunk_pages([page], chunk_size=25, chunk_overlap=5)

    assert len(chunks) == 3
    assert chunks[0].source == "catalog.pdf"
    assert chunks[0].page_number == 3
    assert chunks[0].chunk_index == 0
    assert chunks[0].metadata["source_path"] == "data/raw/catalog.pdf"
    assert chunks[0].id.startswith("catalog.pdf:p3:c0:")


def test_chunk_pages_rejects_invalid_overlap():
    page = DocumentPage(text="Text", source="a.pdf", page_number=1, source_path="a.pdf")

    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_pages([page], chunk_size=100, chunk_overlap=100)
