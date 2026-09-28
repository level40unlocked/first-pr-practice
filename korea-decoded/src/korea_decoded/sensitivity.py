"""Rule-based sensitivity check that runs before any script is written.

Topics that could portray Korea negatively go to the review queue instead of the
production queue. The script writer runs a second, model-based check, and the
stricter of the two wins.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from korea_decoded.models import Sensitivity


@dataclass(frozen=True)
class SensitivityResult:
    level: Sensitivity
    matched: tuple[str, ...]

    @property
    def reason(self) -> str:
        if not self.matched:
            return ""
        return "matched keywords: " + ", ".join(self.matched)


def classify(text: str, negative_keywords: tuple[str, ...]) -> SensitivityResult:
    lowered = text.lower()
    matched = []
    for kw in negative_keywords:
        if kw.isascii():
            # Word boundaries so "war" doesn't match "software" or "award".
            if re.search(rf"\b{re.escape(kw)}\b", lowered):
                matched.append(kw)
        elif kw in lowered:
            # Korean has no word boundaries between particles, so substring match.
            matched.append(kw)
    return SensitivityResult(level="review" if matched else "go", matched=tuple(matched))


def stricter(a: Sensitivity, b: Sensitivity) -> Sensitivity:
    return "review" if "review" in (a, b) else "go"
