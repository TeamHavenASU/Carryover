"""The ONLY file that talks to the AI model (Role D, D1).

Everything else calls call_llm(). To change provider or model, change backend/.env.
No other file needs to change.

Settings (all in backend/.env, never in code):
    LLM_PROVIDER   "anthropic" (default) or "openai"
                   "openai" means any service with an OpenAI style /chat/completions
                   API. Set LLM_BASE_URL for services other than OpenAI itself.
    LLM_MODEL      the model name for that provider
    LLM_API_KEY    the secret key
    LLM_BASE_URL   optional, only for the "openai" provider

Safety: on ANY error (no key, timeout, bad reply, network) call_llm returns the
safe fallback as JSON text. It never raises, and it never logs what the person
typed or any photo.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

log = logging.getLogger("carryover.llm")

TIMEOUT_SECONDS = 20
MAX_OUTPUT_TOKENS = 300

SAFE_FALLBACK = {
    "reply": "I'm not sure. Please ask someone you trust.",
    "step_id_guess": None,
    "needs_person": False,
}
FALLBACK_TEXT = json.dumps(SAFE_FALLBACK)

_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def is_fallback(text: str) -> bool:
    """True if call_llm gave up and returned the safe fallback."""
    return text == FALLBACK_TEXT


def _split_image(image: str) -> tuple[str, str]:
    """Accept a data URL ("data:image/jpeg;base64,...") or raw base64.

    Returns (media_type, base64_data).
    """
    if image.startswith("data:"):
        header, _, data = image.partition(",")
        media_type = header[5:].split(";")[0] or "image/jpeg"
    else:
        media_type, data = "image/jpeg", image
    if media_type not in _IMAGE_TYPES:
        raise ValueError("unsupported image type")
    return media_type, data


def _call_anthropic(system_prompt, user_text, image, key, model) -> str:
    content = []
    if image:
        media_type, data = _split_image(image)
        content.append(
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}}
        )
    content.append({"type": "text", "text": user_text})
    body = {
        "model": model,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": content}],
    }
    resp = httpx.post(
        os.getenv("LLM_BASE_URL", "https://api.anthropic.com").rstrip("/") + "/v1/messages",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=body,
        timeout=httpx.Timeout(TIMEOUT_SECONDS),
    )
    resp.raise_for_status()
    blocks = resp.json().get("content", [])
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")


def _call_openai_style(system_prompt, user_text, image, key, model) -> str:
    if image:
        media_type, data = _split_image(image)
        user_content = [
            {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{data}"}},
            {"type": "text", "text": user_text},
        ]
    else:
        user_content = user_text
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    }
    base = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    resp = httpx.post(
        base + "/chat/completions",
        headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
        json=body,
        timeout=httpx.Timeout(TIMEOUT_SECONDS),
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"] or ""


def call_llm(system_prompt: str, user_text: str, image: str | None = None) -> str:
    """Send one request to the model and return its reply as text.

    On any error, returns the safe fallback as JSON text (see SAFE_FALLBACK).
    """
    try:
        key = os.getenv("LLM_API_KEY", "").strip()
        model = os.getenv("LLM_MODEL", "claude-haiku-5-5").strip()
        provider = os.getenv("LLM_PROVIDER", "anthropic").strip().lower()
        if not key:
            raise RuntimeError("LLM_API_KEY is not set")
        if provider == "anthropic":
            text = _call_anthropic(system_prompt, user_text, image, key, model)
        elif provider == "openai":
            text = _call_openai_style(system_prompt, user_text, image, key, model)
        else:
            raise RuntimeError(f"unknown LLM_PROVIDER: {provider}")
        if not text.strip():
            raise RuntimeError("empty reply")
        return text
    except Exception as exc:  # noqa: BLE001  (we want to catch everything here)
        # Log the kind of error only. Never the prompt, the typed text or the photo.
        log.warning("call_llm failed: %s", type(exc).__name__)
        return FALLBACK_TEXT
