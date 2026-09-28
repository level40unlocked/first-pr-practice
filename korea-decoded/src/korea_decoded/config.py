"""Channel configuration loaded from config/channel.toml."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "channel.toml"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
EXAMPLES_DIR = PROJECT_ROOT / "examples"
DATA_DIR = Path(os.environ.get("KD_DATA_DIR", PROJECT_ROOT / "data"))
OUTPUT_DIR = Path(os.environ.get("KD_OUTPUT_DIR", PROJECT_ROOT / "output"))


@dataclass(frozen=True)
class Pillar:
    key: str
    label: str
    weight: float
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class ChannelConfig:
    name: str
    target_seconds: int
    pillars: tuple[Pillar, ...]
    negative_keywords: tuple[str, ...]
    reddit_subreddits: tuple[str, ...]
    reddit_timeframe: str
    rss_feeds: tuple[str, ...]
    naver_queries: tuple[str, ...]


def load_config(path: Path = CONFIG_PATH) -> ChannelConfig:
    with open(path, "rb") as f:
        raw = tomllib.load(f)
    pillars = tuple(
        Pillar(
            key=key,
            label=p["label"],
            weight=float(p["weight"]),
            keywords=tuple(k.lower() for k in p["keywords"]),
        )
        for key, p in raw["pillars"].items()
    )
    return ChannelConfig(
        name=raw["channel"]["name"],
        target_seconds=int(raw["channel"]["target_seconds"]),
        pillars=pillars,
        negative_keywords=tuple(k.lower() for k in raw["sensitivity"]["negative_keywords"]),
        reddit_subreddits=tuple(raw["sources"]["reddit_subreddits"]),
        reddit_timeframe=raw["sources"]["reddit_timeframe"],
        rss_feeds=tuple(raw["sources"]["rss_feeds"]),
        naver_queries=tuple(raw["sources"]["naver_queries"]),
    )
