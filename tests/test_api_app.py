from fastapi.testclient import TestClient

from campusai.api.app import app
from campusai.config import get_settings


def test_health_endpoint_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_status_endpoint_does_not_expose_secret(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("GROQ_API_KEY", "gsk_secret_for_test")

    client = TestClient(app)
    response = client.get("/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["has_groq_key"] is True
    assert "gsk_secret_for_test" not in response.text
    get_settings.cache_clear()
