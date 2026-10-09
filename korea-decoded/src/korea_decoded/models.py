"""Data shapes shared across the pipeline."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Sensitivity = Literal["go", "review"]


@dataclass
class RawTopic:
    """A candidate topic as returned by a collector, before scoring."""

    source: str
    title: str
    url: str
    summary: str = ""
    engagement: int = 0  # upvotes, comments, etc. Collector-specific scale.
    published_at: str = ""  # ISO 8601 when known
    extra: dict = field(default_factory=dict)

    @property
    def uid(self) -> str:
        return hashlib.sha256(self.url.encode()).hexdigest()[:16]


class ScriptLine(BaseModel):
    model_config = ConfigDict(extra="forbid")  # structured outputs need additionalProperties: false

    en: str = Field(description="One narration line in casual English")
    ko: str = Field(description="Natural casual Korean translation of the same line")
    visual: str = Field(description="Short visual direction for this line")


class FactCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")  # structured outputs need additionalProperties: false

    claim: str
    where_to_verify: str


class ShortScript(BaseModel):
    model_config = ConfigDict(extra="forbid")  # structured outputs need additionalProperties: false

    title: str = Field(description="YouTube title, under 70 characters")
    hook_text: str = Field(description="Big on-screen text for the first 2 seconds")
    pillar: str
    target_countries: list[str] = Field(
        description="ISO 3166 alpha-2 codes of the countries this Short compares Korea with "
        "(their viewers are the target audience); empty if it is not a comparison"
    )
    sensitivity: Sensitivity
    sensitivity_reason: str = Field(description="Why the topic is or isn't sensitive")
    lines: list[ScriptLine]
    fact_checks: list[FactCheck]
    hashtags: list[str]
