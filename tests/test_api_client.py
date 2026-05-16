from campusai.services.api_client import CampusAIBackendClient


def test_backend_client_decodes_ask_response(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return (
                b'{"answer":"Mock answer","citations":[{"source":"doc.md","chunk_id":"c1",'
                b'"authority_level":"official","authority_label":"Official"}],'
                b'"retrieved_chunks":[{"id":"c1","content":"Text","source":"doc.md"}],'
                b'"used_live_api":false,"missing_api_key":true,"no_context":false,"error":"missing_api_key"}'
            )

    def fake_urlopen(request, timeout):
        return FakeResponse()

    monkeypatch.setattr("campusai.services.api_client.urlopen", fake_urlopen)

    result = CampusAIBackendClient("http://backend:8000").ask_question("Question?", {"major": "CS"})

    assert result.answer == "Mock answer"
    assert result.missing_api_key is True
    assert result.citations[0].source == "doc.md"
    assert result.retrieved_chunks[0].id == "c1"
