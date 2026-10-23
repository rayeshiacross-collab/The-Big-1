"""Minimal client for local OpenAI-compatible endpoints (Ollama, vLLM, llama.cpp, LM Studio)."""

from __future__ import annotations

import json
from typing import Any

import requests

from .config import LOCAL_MODEL_BASE_URL, LOCAL_MODEL_NAME, assert_open_stack


class LocalModelError(Exception):
    pass


def chat(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
    temperature: float = 0.4,
    max_tokens: int = 2048,
) -> str:
    """Call a local OpenAI-compatible /v1/chat/completions endpoint."""
    assert_open_stack()
    model = model or LOCAL_MODEL_NAME
    url = LOCAL_MODEL_BASE_URL.rstrip("/")

    # Ollama native style
    if "11434" in url and not url.endswith("/v1"):
        # try Ollama /api/chat
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        r = requests.post(f"{url}/api/chat", json=payload, timeout=300)
        if r.status_code == 200:
            data = r.json()
            return data.get("message", {}).get("content", "") or data.get("response", "")
        # fall through to openai-compat attempt

    # OpenAI-compatible
    if not url.endswith("/v1"):
        url = url + "/v1"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    r = requests.post(f"{url}/chat/completions", json=payload, timeout=300)
    if r.status_code != 200:
        raise LocalModelError(f"Local model error {r.status_code}: {r.text[:500]}")
    data = r.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise LocalModelError(f"Unexpected response shape: {json.dumps(data)[:500]}") from e


def doctor_check() -> dict[str, Any]:
    """Quick reachability check for the doctor skill."""
    try:
        reply = chat(
            [{"role": "user", "content": "Reply with exactly: OK"}],
            max_tokens=8,
            temperature=0,
        )
        ok = "OK" in (reply or "").upper()
        return {"reachable": True, "ok": ok, "sample": (reply or "")[:80]}
    except Exception as e:
        return {"reachable": False, "ok": False, "error": str(e)}
