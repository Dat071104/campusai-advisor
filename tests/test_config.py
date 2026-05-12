from campusai.config import get_settings


def test_settings_defaults_load(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setenv("GROQ_MODEL", "")

    settings = get_settings()

    assert settings.groq_model == "llama-3.3-70b-versatile"
    assert settings.groq_base_url == "https://api.groq.com/openai/v1"
    assert settings.embedding_provider == "fastembed"
    assert settings.has_groq_key is False
