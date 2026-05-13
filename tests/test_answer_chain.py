from campusai.config import Settings
from campusai.rag.answer_chain import RAGAnswerChain
from campusai.rag.retriever import RetrievedChunk
from campusai.services.groq_client import LLMResponse, redact_secret


class EmptyRetriever:
    def retrieve(self, question, top_k=None):
        return []


class OneChunkRetriever:
    def retrieve(self, question, top_k=None):
        return [
            RetrievedChunk(
                id="chunk-1",
                content="Students should learn data structures before machine learning.",
                source="campusai_local_advisor_rules.md",
                page_number=1,
                chunk_index=0,
            )
        ]


class FakeClient:
    def __init__(self, response=None):
        self.prompt = None
        self.system_prompt = None
        self.response = response or LLMResponse(content="Mock answer [1]", used_live_api=False)

    def generate(self, prompt, *, system_prompt=None):
        self.prompt = prompt
        self.system_prompt = system_prompt
        return self.response


def make_settings(api_key=None, retries=2):
    return Settings(
        groq_api_key=api_key,
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
        groq_max_retries=retries,
        groq_max_tokens=900,
        rag_top_k=5,
    )


def test_no_context_fallback_does_not_call_llm():
    client = FakeClient()
    chain = RAGAnswerChain(make_settings(), retriever=EmptyRetriever(), chat_client=client)

    result = chain.answer_question("Unknown policy?", {})

    assert result.no_context is True
    assert "chưa có đủ thông tin" in result.answer
    assert client.prompt is None


def test_missing_api_key_behavior_from_mocked_client():
    client = FakeClient(LLMResponse(content="Missing key", used_live_api=False, error="missing_api_key"))
    chain = RAGAnswerChain(make_settings(), retriever=OneChunkRetriever(), chat_client=client)

    result = chain.answer_question("Before ML?", {"major": "CS"})

    assert result.missing_api_key is True
    assert result.used_live_api is False
    assert result.citations


def test_prompt_includes_authority_instructions():
    client = FakeClient()
    chain = RAGAnswerChain(make_settings(), retriever=OneChunkRetriever(), chat_client=client)

    result = chain.answer_question("Local rules official?", {"career_goal": "AI Engineer"})

    assert result.no_context is False
    assert "Không bao giờ biến local advisor heuristic" in client.prompt
    assert "Heuristic local advisor source" in client.prompt
    assert "career_goal" in client.prompt


def test_secret_redaction_does_not_reveal_full_key():
    redacted = redact_secret("gsk_abcdefghijklmnopqrstuvwxyz")

    assert "abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "REDACTED" in redacted
