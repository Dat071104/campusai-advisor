from __future__ import annotations

from campusai.services.api_client import APIClientError, CampusAIAPIClient


class DummyResponse:
    def __init__(self, payload: dict[str, object], status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("bad status")

    def json(self):
        return self._payload


def test_client_builds_urls(monkeypatch):
    calls = {}

    def fake_get(url, params=None, timeout=None):
        calls["url"] = url
        calls["params"] = params
        calls["timeout"] = timeout
        return DummyResponse({"status": "ok"})

    monkeypatch.setattr("campusai.services.api_client.requests.get", fake_get)
    client = CampusAIAPIClient("http://127.0.0.1:8000", timeout_seconds=3)
    assert client.health() == {"status": "ok"}
    assert calls["url"] == "http://127.0.0.1:8000/health"
    assert calls["timeout"] == 3


def test_client_handles_errors(monkeypatch):
    def fake_post(*args, **kwargs):
        raise OSError("network down")

    monkeypatch.setattr("campusai.services.api_client.requests.post", fake_post)
    client = CampusAIAPIClient("http://127.0.0.1:8000")
    try:
        client.ask("Hello")
    except APIClientError as exc:
        assert "unavailable" in str(exc).lower()
