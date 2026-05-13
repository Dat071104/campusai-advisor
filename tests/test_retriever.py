from campusai.config import Settings
from campusai.rag.retriever import Retriever, RetrievedChunk


class FakeEmbeddings:
    def embed(self, texts):
        return [[1.0, 2.0, 3.0] for _ in texts]


class FakeStore:
    def __init__(self, count=1):
        self._count = count
        self.last_top_k = None

    def count(self):
        return self._count

    def query(self, query_embedding, top_k):
        self.last_top_k = top_k
        return [
            RetrievedChunk(
                id="chunk-1",
                content="Machine Learning needs linear algebra.",
                source="local_rules.md",
                page_number=1,
                chunk_index=0,
                distance=0.12,
            )
        ]


def make_settings():
    return Settings(
        groq_api_key=None,
        groq_base_url="https://api.groq.com/openai/v1",
        groq_model="llama-3.3-70b-versatile",
        embedding_provider="fastembed",
        embedding_model="test-model",
        embedding_dim=3,
        vector_store_provider="local",
        vector_store_path="data/vector_db",
        chroma_collection="test",
        raw_data_path="data/raw",
        chunk_size=800,
        chunk_overlap=150,
        groq_timeout_seconds=30,
        groq_min_seconds_between_requests=3,
        groq_max_retries=2,
        groq_max_tokens=900,
        rag_top_k=5,
    )


def test_retriever_returns_chunks_without_groq():
    store = FakeStore()
    retriever = Retriever(make_settings(), embedding_model=FakeEmbeddings(), vector_store=store)

    chunks = retriever.retrieve("What before ML?")

    assert len(chunks) == 1
    assert chunks[0].id == "chunk-1"
    assert chunks[0].source == "local_rules.md"
    assert store.last_top_k == 5


def test_retriever_handles_empty_index():
    retriever = Retriever(make_settings(), embedding_model=FakeEmbeddings(), vector_store=FakeStore(count=0))

    assert retriever.retrieve("Anything?") == []
