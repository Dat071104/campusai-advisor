from dataclasses import replace
from pathlib import Path

from campusai.config import get_settings
from campusai.ingestion.indexer import index_local_documents
from campusai.ingestion.pdf_loader import DocumentPage


class FakeEmbeddingModel:
    def embed(self, texts):
        return [[float(index), 0.0, 1.0] for index, _ in enumerate(texts)]


class FakeVectorStore:
    def __init__(self):
        self.written = []
        self.embeddings = []

    def upsert_chunks(self, chunks, embeddings):
        self.written.extend(chunks)
        self.embeddings.extend(embeddings)
        return len(chunks)


def test_index_local_documents_handles_empty_raw_dir(tmp_path):
    settings = replace(get_settings(), raw_data_path=str(tmp_path))

    result = index_local_documents(settings)

    assert result.pdf_files_found == 0
    assert result.chunks_indexed == 0
    assert "No PDF files found" in result.message


def test_index_local_documents_with_fakes_preserves_metadata(tmp_path):
    pdf_path = tmp_path / "policy.pdf"
    pdf_path.write_bytes(b"%PDF placeholder")
    settings = replace(
        get_settings(),
        raw_data_path=str(tmp_path),
        chunk_size=40,
        chunk_overlap=10,
    )
    vector_store = FakeVectorStore()

    def fake_loader(path: Path):
        return [
            DocumentPage(
                text="Prerequisites require data structures before machine learning.",
                source=path.name,
                page_number=2,
                source_path=str(path),
            )
        ]

    result = index_local_documents(
        settings,
        page_loader=fake_loader,
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
    )

    assert result.pdf_files_found == 1
    assert result.pages_loaded == 1
    assert result.chunks_indexed == len(vector_store.written)
    assert vector_store.written[0].metadata["source"] == "policy.pdf"
    assert vector_store.written[0].metadata["page_number"] == 2
