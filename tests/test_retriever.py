import pytest

from campusai.config import Settings
from campusai.rag.retriever import (
    Retriever,
    RetrievedChunk,
    chunk_matches_local_advisor_source,
    is_graduation_policy_query,
    is_study_path_prerequisite_query,
    rerank_graduation_policy_chunks,
    rerank_study_path_chunks,
    study_path_fetch_size,
)


class FakeEmbeddings:
    def embed(self, texts):
        return [[1.0, 2.0, 3.0] for _ in texts]


class FakeStore:
    def __init__(self, count=1, chunks=None):
        self._count = count
        self.last_top_k = None
        self._chunks = chunks

    def count(self):
        return self._count

    def query(self, query_embedding, top_k):
        self.last_top_k = top_k
        if self._chunks is not None:
            return list(self._chunks[:top_k])
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


def test_study_path_query_widens_fetch_and_prefers_local_advisor_chunk():
    berkeley = RetrievedChunk(
        id="berkeley-1",
        content="Berkeley scheduling policy text unrelated to ML prep.",
        source="berkeley_cs_guide.pdf",
        source_path="data/raw/berkeley_cs_guide.pdf",
        distance=0.05,
    )
    local = RetrievedChunk(
        id="local-1",
        content="Linear algebra before machine learning.",
        source="campusai_local_advisor_rules.md",
        source_path="data/raw/documents/local/campusai_local_advisor_rules.md",
        distance=0.95,
    )
    store = FakeStore(count=1, chunks=[berkeley, local])
    retriever = Retriever(make_settings(), embedding_model=FakeEmbeddings(), vector_store=store)

    q = "What should I learn before Machine Learning?"
    chunks = retriever.retrieve(q, top_k=1)

    assert store.last_top_k == study_path_fetch_size(1)
    assert len(chunks) == 1
    assert chunks[0].id == "local-1"


def test_non_study_path_query_does_not_widen_fetch():
    berkeley = RetrievedChunk(
        id="berkeley-1",
        content="Policy text.",
        source="berkeley_cs_guide.pdf",
        source_path="data/raw/berkeley_cs_guide.pdf",
        distance=0.05,
    )
    local = RetrievedChunk(
        id="local-1",
        content="Heuristic advice.",
        source="campusai_local_advisor_rules.md",
        source_path="data/raw/documents/local/campusai_local_advisor_rules.md",
        distance=0.02,
    )
    store = FakeStore(count=1, chunks=[berkeley, local])
    retriever = Retriever(make_settings(), embedding_model=FakeEmbeddings(), vector_store=store)

    chunks = retriever.retrieve("Berkeley CS office mailing address and hours", top_k=5)

    assert store.last_top_k == 5
    assert [c.id for c in chunks] == ["berkeley-1", "local-1"]


@pytest.mark.parametrize(
    "question,expected",
    [
        ("before learning machine learning, which should we learn", True),
        ("What should I learn before Machine Learning?", True),
        ("What are the prerequisites for machine learning?", True),
        ("prepare for ML coursework", True),
        ("study path for AI engineer", True),
        ("What are the prerequisites for CS 61A?", False),
        ("Berkeley CS lower division requirements", False),
    ],
)
def test_is_study_path_prerequisite_query(question, expected):
    assert is_study_path_prerequisite_query(question) is expected


def test_chunk_matches_local_advisor_source_normalizes_windows_path():
    chunk = RetrievedChunk(
        id="x",
        content="x",
        source="campusai_local_advisor_rules.md",
        source_path=r"data\raw\documents\local\campusai_local_advisor_rules.md",
    )
    assert chunk_matches_local_advisor_source(chunk) is True


def test_rerank_orders_local_above_berkeley_when_distances_favor_berkeley():
    berkeley = RetrievedChunk(
        id="b",
        content="Scheduling.",
        source="berkeley.pdf",
        source_path="data/raw/berkeley.pdf",
        distance=0.1,
    )
    local = RetrievedChunk(
        id="l",
        content="Stats before ML.",
        source="campusai_local_advisor_rules.md",
        source_path="data/raw/documents/local/campusai_local_advisor_rules.md",
        distance=0.9,
    )
    out = rerank_study_path_chunks([berkeley, local], top_k=2)
    assert [c.id for c in out] == ["l", "b"]


def test_rerank_prefers_heuristic_authority_chunk_without_local_filename_markers():
    berkeley = RetrievedChunk(
        id="berkeley-1",
        content="Berkeley scheduling policy text unrelated to ML prep.",
        source="berkeley_cs_guide.pdf",
        source_path="data/raw/berkeley_cs_guide.pdf",
        distance=0.08,
    )
    local = RetrievedChunk(
        id="local-1",
        content="Probability and linear algebra before machine learning.",
        source="other_notes.md",
        source_path="data/raw/other_notes.md",
        distance=0.22,
        authority_level="heuristic",
        source_type="local_advisor_rules",
    )
    store = FakeStore(count=1, chunks=[berkeley, local])
    retriever = Retriever(make_settings(), embedding_model=FakeEmbeddings(), vector_store=store)

    chunks = retriever.retrieve("What should I learn before Machine Learning?", top_k=1)

    assert len(chunks) == 1
    assert chunks[0].id == "local-1"


def test_graduation_policy_query_detects_requirements_language():
    assert is_graduation_policy_query("What are TDTU graduation requirements?") is True
    assert is_graduation_policy_query("What is the academic regulation for graduation?") is True
    assert is_graduation_policy_query("What are graduation requirements for international students?") is False
    assert is_graduation_policy_query("What should a Backend + AI student learn?") is False


def test_rerank_prefers_tdtu_graduation_policy_over_curriculum_mentions():
    curriculum = RetrievedChunk(
        id="curriculum-1",
        content="TOEIC 600 is required for some advanced curriculum graduation tracks.",
        source="tdtu_computer_science_curriculum.md",
        source_path="data/raw/documents/tdtu/tdtu_computer_science_curriculum.md",
        distance=0.04,
        authority_level="official_curriculum",
        source_type="official_faculty",
    )
    policy = RetrievedChunk(
        id="policy-1",
        content="TDTU graduation requirements include mandatory courses and required credits.",
        source="tdtu_academic_regulations_graduation.md",
        source_path="data/raw/documents/tdtu/tdtu_academic_regulations_graduation.md",
        distance=0.18,
        authority_level="official_policy",
        source_type="official_regulation_pdf",
    )
    out = rerank_graduation_policy_chunks([curriculum, policy], top_k=1)
    assert [c.id for c in out] == ["policy-1"]


def test_rerank_graduation_policy_deprioritizes_curriculum_toeic_mentions():
    curriculum = RetrievedChunk(
        id="curriculum-1",
        content="Advanced program graduation requires TOEIC 600.",
        source="tdtu_computer_science_curriculum.md",
        source_path="data/raw/documents/tdtu/tdtu_computer_science_curriculum.md",
        distance=0.01,
        authority_level="official_curriculum",
        source_type="official_faculty",
    )
    policy = RetrievedChunk(
        id="policy-1",
        content="TDTU graduation requirements include required credits and mandatory courses.",
        source="tdtu_academic_regulations_graduation.md",
        source_path="data/raw/documents/tdtu/tdtu_academic_regulations_graduation.md",
        distance=0.03,
        authority_level="official_policy",
        source_type="official_regulation_pdf",
    )
    out = rerank_graduation_policy_chunks([curriculum, policy], top_k=1)
    assert [c.id for c in out] == ["policy-1"]


def test_rerank_graduation_policy_deprioritizes_international_handbook_policy_doc():
    handbook = RetrievedChunk(
        id="handbook-1",
        content="International student handbook guidance and support information.",
        source="tdtu_student_handbook_international.md",
        source_path="data/raw/documents/tdtu/tdtu_student_handbook_international.md",
        distance=0.06,
        authority_level="official_policy",
        source_type="official_handbook",
    )
    policy = RetrievedChunk(
        id="policy-1",
        content="TDTU graduation requirements include required credits and mandatory courses.",
        source="tdtu_academic_regulations_graduation.md",
        source_path="data/raw/documents/tdtu/tdtu_academic_regulations_graduation.md",
        distance=0.25,
        authority_level="official_policy",
        source_type="official_regulation_pdf",
    )

    out = rerank_graduation_policy_chunks([handbook, policy], top_k=1)

    assert [c.id for c in out] == ["policy-1"]


def test_retrieved_chunk_parses_authority_from_chroma_metadata():
    from campusai.rag.retriever import _parse_chroma_results

    results = {
        "ids": [["chunk-1"]],
        "documents": [["Curriculum details"]],
        "metadatas": [[{
            "source": "tdtu_software_engineering_curriculum.md",
            "source_path": "data/raw/documents/tdtu/tdtu_software_engineering_curriculum.md",
            "page_number": 1,
            "chunk_index": 0,
            "authority": "official_curriculum",
            "source_type": "official_faculty_info",
            "university": "Ton Duc Thang University",
            "country": "Vietnam",
            "language": "Vietnamese",
        }]],
        "distances": [[0.42]],
    }

    chunks = _parse_chroma_results(results)

    assert len(chunks) == 1
    assert chunks[0].authority_level == "official_curriculum"
    assert chunks[0].source_type == "official_faculty_info"
    assert chunks[0].university == "Ton Duc Thang University"
    assert chunks[0].country == "Vietnam"
    assert chunks[0].language == "Vietnamese"
