"""Keyword matching shared by scoring and the sensitivity check."""

from __future__ import annotations

import re


def _pattern(keyword: str) -> str:
    # Latin keywords match whole words ("war" must not hit "software"); a word
    # boundary only makes sense next to a word character ("u.s." ends in a dot).
    # Korean has no spaces between words and particles, so it matches as a substring.
    if not keyword.isascii():
        return re.escape(keyword)
    left = r"\b" if re.match(r"\w", keyword) else ""
    right = r"\b" if re.search(r"\w$", keyword) else ""
    return f"{left}{re.escape(keyword)}{right}"


def contains(text: str, keyword: str) -> bool:
    """text must already be lowercased."""
    return re.search(_pattern(keyword), text) is not None


def remove(text: str, keyword: str) -> str:
    return re.sub(_pattern(keyword), " ", text)
