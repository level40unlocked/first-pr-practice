"""Turns a topic into a bilingual (EN + KO) Shorts script with Claude."""

from __future__ import annotations

import os
import re
from pathlib import Path

import anthropic

from korea_decoded.config import EXAMPLES_DIR, PROMPTS_DIR, ChannelConfig
from korea_decoded.models import ShortScript

DEFAULT_MODEL = "claude-opus-5"


class ScriptError(RuntimeError):
    pass


def build_system_prompt(config: ChannelConfig, examples_dir: Path = EXAMPLES_DIR) -> str:
    template = (PROMPTS_DIR / "script_system.md").read_text(encoding="utf-8")
    examples = "\n\n---\n\n".join(
        p.read_text(encoding="utf-8").strip() for p in sorted(examples_dir.glob("*.md"))
    )
    return template.format(target_seconds=config.target_seconds, examples=examples)


def build_user_message(topic) -> str:
    pillar = topic["pillar"] or "unassigned (pick the closest pillar or 'society')"
    return (
        "Write a Korea Decoded Short about this topic.\n\n"
        f"Title: {topic['title']}\n"
        f"Source: {topic['source']} ({topic['url']})\n"
        f"Suggested pillar: {pillar}\n"
        f"Context: {topic['summary'] or '(none)'}\n\n"
        "The source is a starting point, not a script: find the angle a curious "
        "foreigner would find surprising, and explain it."
    )


class ScriptWriter:
    def __init__(self, config: ChannelConfig, client: anthropic.Anthropic | None = None):
        self.config = config
        self.client = client or anthropic.Anthropic()
        self.model = os.environ.get("KD_MODEL", DEFAULT_MODEL)
        self.system_prompt = build_system_prompt(config)

    def write(self, topic) -> ShortScript:
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            # If the model declines, the API retries on Anthropic's recommended fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            thinking={"type": "adaptive"},
            output_config={
                "effort": os.environ.get("KD_EFFORT", "high"),
                "format": {"type": "json_schema", "schema": ShortScript.model_json_schema()},
            },
            # The system prompt (rules + approved examples) is identical for every
            # topic, so cache it.
            system=[
                {"type": "text", "text": self.system_prompt, "cache_control": {"type": "ephemeral"}}
            ],
            messages=[{"role": "user", "content": build_user_message(topic)}],
        )
        if response.stop_reason == "refusal":
            raise ScriptError(f"model declined topic {topic['uid']}")
        if response.stop_reason == "max_tokens":
            raise ScriptError(f"output truncated for topic {topic['uid']}")
        text = next((b.text for b in response.content if b.type == "text"), None)
        if text is None:
            raise ScriptError(f"no text in response for topic {topic['uid']}")
        return ShortScript.model_validate_json(text)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or "script"


def render_markdown(script: ShortScript, topic) -> str:
    """Same layout as the files in examples/, plus visuals and the fact-check list."""
    out = [
        f"# {script.title}",
        f"pillar: {script.pillar} | sensitivity: {script.sensitivity}",
        f"hook_text: {script.hook_text}",
        f"source: {topic['url']}",
    ]
    if script.sensitivity == "review":
        out.append(f"⚠️ review reason: {script.sensitivity_reason}")
    out += ["", "## EN"] + [line.en for line in script.lines]
    out += ["", "## KO"] + [line.ko for line in script.lines]
    out += ["", "## Visuals"] + [f"{i}. {line.visual}" for i, line in enumerate(script.lines, 1)]
    out += ["", "## Fact check before upload"]
    out += [f"- [ ] {fc.claim} → {fc.where_to_verify}" for fc in script.fact_checks]
    out += ["", "## Hashtags", " ".join(script.hashtags), ""]
    return "\n".join(out)
