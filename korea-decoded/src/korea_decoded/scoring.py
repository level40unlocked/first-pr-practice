"""Assigns each topic a content pillar and a priority score."""

from __future__ import annotations

import math

from korea_decoded import textmatch
from korea_decoded.config import ChannelConfig, Pillar
from korea_decoded.models import RawTopic


def _keyword_hits(text: str, pillar: Pillar) -> int:
    return sum(textmatch.contains(text, kw) for kw in pillar.keywords)


def detect_countries(topic: RawTopic, config: ChannelConfig) -> list[str]:
    """Country codes mentioned in the topic, for "Korea vs X" comparisons."""
    text = f"{topic.title} {topic.summary}".lower()
    # Longest names first, removed once matched, so "인도네시아" doesn't also count as "인도".
    names = sorted(((n, code) for code, ns in config.countries.items() for n in ns), key=lambda x: -len(x[0]))
    found = []
    for name, code in names:
        if textmatch.contains(text, name):
            text = textmatch.remove(text, name)
            if code not in found:
                found.append(code)
    return sorted(found)


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
