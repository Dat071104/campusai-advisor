from campusai.ingestion.chunker import TextChunk
from campusai.rag.vector_store import ChromaVectorStore


def test_reset_collection_clears_chroma(tmp_path):
    persist = tmp_path / "chroma"
    store = ChromaVectorStore(str(persist), "test_reset_coll")
    chunk = TextChunk(
        id="id-1",
        text="hello world",
        source="x.md",
        page_number=1,
        chunk_index=0,
        source_path=str(tmp_path / "x.md"),
        document_type="markdown",
    )
    emb = [0.0] * 384
    store.upsert_chunks([chunk], [emb])
    assert store._collection.count() == 1

    store.reset_collection()

    assert store._collection.count() == 0
