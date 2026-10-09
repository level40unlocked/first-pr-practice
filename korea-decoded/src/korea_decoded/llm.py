"""One place that calls Claude for structured (JSON-schema) output."""

from __future__ import annotations

import os
from typing import TypeVar

from pydantic import BaseModel

DEFAULT_MODEL = "claude-opus-5"

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    pass


def structured_call(client, system: str, user: str, schema: type[T], *, effort: str | None = None,
                    label: str = "request") -> T:
    response = client.beta.messages.create(
        model=os.environ.get("KD_MODEL", DEFAULT_MODEL),
        max_tokens=16000,
        # If the model declines, the API retries on Anthropic's recommended fallback model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        thinking={"type": "adaptive"},
        output_config={
            "effort": effort or os.environ.get("KD_EFFORT", "high"),
            "format": {"type": "json_schema", "schema": schema.model_json_schema()},
        },
        # System prompts are fixed per task, so cache them across calls.
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
    )
    if response.stop_reason == "refusal":
        raise LLMError(f"model declined {label}")
    if response.stop_reason == "max_tokens":
        raise LLMError(f"output truncated for {label}")
    text = next((b.text for b in response.content if b.type == "text"), None)
    if text is None:
        raise LLMError(f"no text in response for {label}")
    return schema.model_validate_json(text)
