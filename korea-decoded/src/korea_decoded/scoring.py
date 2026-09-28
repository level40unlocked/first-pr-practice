"""Assigns each topic a content pillar and a priority score."""

from __future__ import annotations

import math
import re

from korea_decoded.config import ChannelConfig, Pillar
from korea_decoded.models import RawTopic


def _keyword_hits(text: str, pillar: Pillar) -> int:
    hits = 0
    for kw in pillar.keywords:
        if kw.isascii():
            hits += bool(re.search(rf"\b{re.escape(kw)}\b", text))
        else:
            hits += kw in text
    return hits


def detect_pillar(topic: RawTopic, config: ChannelConfig) -> Pillar | None:
    text = f"{topic.title} {topic.summary}".lower()
    best, best_hits = None, 0
    for pillar in config.pillars:
        hits = _keyword_hits(text, pillar)
        if hits > best_hits:
            best, best_hits = pillar, hits
    return best


def score(topic: RawTopic, pillar: Pillar | None) -> float:
    """Higher is better. Off-pillar topics are kept but ranked well below on-pillar ones."""
    engagement = math.log10(max(topic.engagement, 0) + 10)  # 1.0 at zero engagement
    weight = pillar.weight if pillar else 0.5
    return round(engagement * weight, 3)
