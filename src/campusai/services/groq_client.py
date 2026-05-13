"""Groq OpenAI-compatible chat client with conservative free-tier safeguards."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Protocol

from campusai.config import Settings, get_settings


class GroqClientError(RuntimeError):
    """User-safe Groq client error."""


@dataclass(frozen=True)
class LLMResponse:
    content: str
    used_live_api: bool
    error: str | None = None


class ChatClient(Protocol):
    def generate(self, prompt: str, *, system_prompt: str | None = None) -> LLMResponse:
        """Generate an answer for a prompt."""


class GroqChatClient:
    _last_request_at: float = 0.0

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> LLMResponse:
        if not self.settings.groq_api_key:
            return LLMResponse(
                content="GROQ_API_KEY is not configured. Copy .env.example to .env and set GROQ_API_KEY locally to enable live LLM answers.",
                used_live_api=False,
                error="missing_api_key",
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise GroqClientError('Missing dependency "openai". Run: python -m pip install -e ".[dev]"') from exc

        client = OpenAI(
            api_key=self.settings.groq_api_key,
            base_url=self.settings.groq_base_url,
            timeout=self.settings.groq_timeout_seconds,
            max_retries=0,
        )
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        attempt = 0
        while True:
            try:
                self._respect_min_delay()
                GroqChatClient._last_request_at = time.monotonic()
                response = client.chat.completions.create(
                    model=self.settings.groq_model,
                    messages=messages,
                    max_tokens=self.settings.groq_max_tokens,
                    temperature=0.2,
                )
                content = response.choices[0].message.content or ""
                return LLMResponse(content=content.strip(), used_live_api=True)
            except Exception as exc:
                if attempt >= self.settings.groq_max_retries or not _is_retryable(exc):
                    return LLMResponse(
                        content=_friendly_error_message(exc),
                        used_live_api=False,
                        error=_error_code(exc),
                    )
                delay = _retry_delay(exc, attempt)
                time.sleep(delay)
                attempt += 1

    def _respect_min_delay(self) -> None:
        elapsed = time.monotonic() - GroqChatClient._last_request_at
        remaining = self.settings.groq_min_seconds_between_requests - elapsed
        if remaining > 0:
            time.sleep(remaining)


def redact_secret(value: str | None) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "***REDACTED***"
    return f"{value[:3]}***REDACTED***{value[-3:]}"


def _is_retryable(exc: Exception) -> bool:
    status = getattr(exc, "status_code", None)
    name = exc.__class__.__name__.lower()
    if status == 429 or (isinstance(status, int) and status >= 500):
        return True
    return "timeout" in name or "timeout" in str(exc).lower()


def _retry_delay(exc: Exception, attempt: int) -> float:
    retry_after = None
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if headers:
        retry_after = headers.get("retry-after") or headers.get("Retry-After")
    if retry_after:
        try:
            return min(float(retry_after), 30.0)
        except ValueError:
            pass
    return min((2**attempt) + random.uniform(0.1, 0.5), 10.0)


def _error_code(exc: Exception) -> str:
    status = getattr(exc, "status_code", None)
    if status == 429:
        return "rate_limited"
    if isinstance(status, int) and status >= 500:
        return "server_error"
    if "timeout" in exc.__class__.__name__.lower() or "timeout" in str(exc).lower():
        return "timeout"
    return "groq_error"


def _friendly_error_message(exc: Exception) -> str:
    code = _error_code(exc)
    if code == "rate_limited":
        return "Groq rate limit reached. Wait a bit, then try your question again."
    if code == "timeout":
        return "Groq request timed out. Try a shorter question or wait a few seconds and retry."
    if code == "server_error":
        return "Groq returned a temporary server error. Please try again later."
    return "Could not reach Groq right now. Check your .env configuration and network connectivity."
