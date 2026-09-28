"""Turns a topic into a bilingual (EN + KO) Shorts script with Claude."""

from __future__ import annotations

import re
from pathlib import Path

import anthropic

from korea_decoded.config import EXAMPLES_DIR, PROMPTS_DIR, ChannelConfig
from korea_decoded.llm import LLMError, structured_call
from korea_decoded.models import ShortScript



# Kept as the name callers catch; the shared LLM helper raises it.
ScriptError = LLMError


def build_system_prompt(config: ChannelConfig, examples_dir: Path = EXAMPLES_DIR) -> str:
    template = (PROMPTS_DIR / "script_system.md").read_text(encoding="utf-8")
    examples = "\n\n---\n\n".join(
        p.read_text(encoding="utf-8").strip() for p in sorted(examples_dir.glob("*.md"))
    )
    return template.format(target_seconds=config.target_seconds, examples=examples)


def build_user_message(topic) -> str:
    pillar = topic["pillar"] or "unassigned (pick the closest pillar or 'society')"
    countries = topic["countries"] if "countries" in topic.keys() else ""
    return (
        "Write a Korea Decoded Short about this topic.\n\n"
        f"Title: {topic['title']}\n"
        f"Source: {topic['source']} ({topic['url']})\n"
        f"Suggested pillar: {pillar}\n"
        f"Countries mentioned: {countries or '(none)'}\n"
        f"Context: {topic['summary'] or '(none)'}\n\n"
        "The source is a starting point, not a script: find the angle a curious "
        "foreigner would find surprising, and explain it."
    )


class ScriptWriter:
    def __init__(self, config: ChannelConfig, client: anthropic.Anthropic | None = None):
        self.config = config
        self.client = client or anthropic.Anthropic()
        self.system_prompt = build_system_prompt(config)

    def write(self, topic) -> ShortScript:
        return structured_call(self.client, self.system_prompt, build_user_message(topic), ShortScript,
                               label=f"topic {topic['uid']}")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or "script"


def render_markdown(script: ShortScript, topic) -> str:
    """Same layout as the files in examples/, plus visuals and the fact-check list."""
    out = [
        f"# {script.title}",
        f"pillar: {script.pillar} | sensitivity: {script.sensitivity}"
        + (f" | vs: {', '.join(script.target_countries)}" if script.target_countries else ""),
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
