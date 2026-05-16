from dataclasses import replace
from pathlib import Path

from campusai.app import _build_demo_index
from campusai.config import get_settings
from campusai.ingestion.indexer import index_local_documents
from campusai.ingestion.pdf_loader import DocumentPage
from campusai.rag.vector_store import ChromaVectorStore, wait_for_chroma_index_ready


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
    assert result.text_files_found == 0
    assert result.chunks_indexed == 0
    assert "No PDF, Markdown, or text files found" in result.message


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
                document_type="pdf",
            )
        ]

    result = index_local_documents(
        settings,
        page_loader=fake_loader,
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
    )

    assert result.pdf_files_found == 1
    assert result.text_files_found == 0
    assert result.pages_loaded == 1
    assert result.chunks_indexed == len(vector_store.written)
    assert vector_store.written[0].metadata["source"] == "policy.pdf"
    assert vector_store.written[0].metadata["page_number"] == 2
    assert vector_store.written[0].metadata["document_type"] == "pdf"


def test_index_local_documents_indexes_markdown_without_pdf(tmp_path):
    md = tmp_path / "campusai_local_advisor_rules.md"
    md.write_text(
        "Data Structures and Algorithms before Machine Learning. " * 5 + "\n",
        encoding="utf-8",
    )
    settings = replace(
        get_settings(),
        raw_data_path=str(tmp_path),
        chunk_size=40,
        chunk_overlap=10,
    )
    vector_store = FakeVectorStore()

    result = index_local_documents(
        settings,
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
    )

    assert result.pdf_files_found == 0
    assert result.text_files_found == 1
    assert result.chunks_indexed > 0
    assert any("campusai_local_advisor_rules.md" in c.metadata["source"] for c in vector_store.written)
    meta0 = vector_store.written[0].metadata
    assert meta0.get("authority") == "heuristic"
    assert meta0.get("source_type") == "local_advisor_rules"
    assert meta0.get("is_official_policy") is False


def test_index_local_documents_preserves_markdown_metadata_fields(tmp_path):
    md = tmp_path / "tdtu_program.md"
    md.write_text(
        "\n".join(
            [
                "# TDTU Program",
                "",
                "## Metadata",
                "",
                "```yaml",
                "source_authority: official_curriculum",
                "source_type: official_faculty_info",
                "official_policy: true",
                "university: Ton Duc Thang University",
                "country: Vietnam",
                "language: Vietnamese",
                "```",
                "",
                "The program has 136 credits and a major code.",
            ]
        ),
        encoding="utf-8",
    )
    settings = replace(
        get_settings(),
        raw_data_path=str(tmp_path),
        chunk_size=200,
        chunk_overlap=20,
    )
    vector_store = FakeVectorStore()

    result = index_local_documents(
        settings,
        embedding_model=FakeEmbeddingModel(),
        vector_store=vector_store,
    )

    assert result.text_files_found == 1
    assert result.chunks_indexed > 0
    meta0 = vector_store.written[0].metadata
    assert meta0.get("authority") == "official_curriculum"
    assert meta0.get("source_type") == "official_faculty_info"
    assert meta0.get("is_official_policy") is True
    assert meta0.get("university") == "Ton Duc Thang University"
    assert meta0.get("country") == "Vietnam"
    assert meta0.get("language") == "Vietnamese"


def test_index_local_documents_reset_clears_chroma_before_reupsert(tmp_path):
    md = tmp_path / "note.md"
    md.write_text("Probability before Machine Learning. " * 8, encoding="utf-8")
    vdir = tmp_path / "vdb"
    settings = replace(
        get_settings(),
        raw_data_path=str(tmp_path),
        vector_store_path=str(vdir),
        chroma_collection="idx_reset_test",
        chunk_size=80,
        chunk_overlap=10,
    )
    store = ChromaVectorStore(str(vdir), settings.chroma_collection)
    em = FakeEmbeddingModel()

    r1 = index_local_documents(settings, reset=False, embedding_model=em, vector_store=store)
    assert r1.chunks_indexed > 0
    n1 = store._collection.count()

    md.write_text("Unrelated dining hall hours and campus bus schedule. " * 15, encoding="utf-8")
    r2 = index_local_documents(settings, reset=True, embedding_model=em, vector_store=store)

    n2 = store._collection.count()
    assert n1 == r1.chunks_indexed
    assert n2 == r2.chunks_indexed
    assert n1 > 0
    assert n2 < n1 + r2.chunks_indexed


def test_wait_for_chroma_index_ready_detects_fresh_collection(tmp_path):
    md = tmp_path / "note.md"
    md.write_text("Statistics before Machine Learning. " * 8, encoding="utf-8")
    vdir = tmp_path / "vdb"
    settings = replace(
        get_settings(),
        raw_data_path=str(tmp_path),
        vector_store_path=str(vdir),
        chroma_collection="ready_check_test",
        chunk_size=80,
        chunk_overlap=10,
    )
    store = ChromaVectorStore(str(vdir), settings.chroma_collection)

    result = index_local_documents(settings, reset=True, embedding_model=FakeEmbeddingModel(), vector_store=store)

    assert result.chunks_indexed > 0
    assert wait_for_chroma_index_ready(
        settings.vector_store_path,
        settings.chroma_collection,
        expected_min_chunks=result.chunks_indexed,
    ) is True


def test_build_demo_index_returns_success_message_for_indexable_files(tmp_path):
    md = tmp_path / "campusai_local_advisor_rules.md"
    md.write_text("Calculus and Python before Machine Learning. " * 6, encoding="utf-8")
    settings = replace(
        get_settings(),
        raw_data_path=str(tmp_path),
        vector_store_path=str(tmp_path / "vector_db"),
        chroma_collection="demo_index_success",
        chunk_size=80,
        chunk_overlap=10,
    )

    ok, message = _build_demo_index(settings)

    assert ok is True
    assert message == "Demo index built successfully."


def test_build_demo_index_returns_safe_failure_message_when_nothing_is_indexed(tmp_path):
    settings = replace(
        get_settings(),
        raw_data_path=str(tmp_path),
        vector_store_path=str(tmp_path / "vector_db"),
        chroma_collection="demo_index_failure",
    )

    ok, message = _build_demo_index(settings)

    assert ok is False
    assert message.startswith("Failed to build index: ")
    assert str(tmp_path) in message
