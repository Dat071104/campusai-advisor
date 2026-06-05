from campusai.config import get_settings


def test_settings_defaults_load(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setenv("GROQ_MODEL", "")
    monkeypatch.setenv("CAMPUSAI_API_BASE_URL", "")

    settings = get_settings()

    assert settings.groq_model == "llama-3.3-70b-versatile"
    assert settings.groq_base_url == "https://api.groq.com/openai/v1"
    assert settings.embedding_provider == "fastembed"
    assert settings.has_groq_key is False
    assert settings.campusai_api_base_url is None


def test_python_dotenv_disabled_skips_local_env_file(monkeypatch, tmp_path):
    get_settings.cache_clear()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    (tmp_path / ".env").write_text("GROQ_API_KEY=fake_local_key\n", encoding="utf-8")

    settings = get_settings()

    assert settings.groq_api_key is None
    assert settings.has_groq_key is False
