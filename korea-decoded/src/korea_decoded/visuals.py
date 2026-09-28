"""Finds one background image per script line.

Claude plans each line's source (stock photo, AI image, or text card); the
sources are tried in order of preference and a locally drawn text card is the
fallback that never fails, so a render always has a full set of images.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import requests
from pydantic import BaseModel, ConfigDict, Field

from korea_decoded.config import PROMPTS_DIR
from korea_decoded.llm import structured_call
from korea_decoded.models import ShortScript

Source = Literal["stock", "ai", "card"]
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
NAVY, NAVY_LIGHT, YELLOW, WHITE = (14, 23, 38), (38, 52, 86), (255, 212, 0), (255, 255, 255)


class Scene(BaseModel):
    model_config = ConfigDict(extra="forbid")

    line: int
    source: Source
    stock_query: str = Field(description="2-4 English words for a stock photo search, or empty")
    ai_prompt: str = Field(description="Photorealistic vertical image description, or empty")
    card_text: str = Field(description="Big number or comparison for a text card, or empty")
    card_subtext: str = Field(description="Short label under the card text, or empty")


class VisualPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenes: list[Scene]


@dataclass
class Credit:
    line: int
    source: str
    detail: str  # photographer + page URL, AI prompt, or card text


class VisualPlanner:
    def __init__(self, client=None):
        if client is None:
            import anthropic
            client = anthropic.Anthropic()
        self.client = client
        self.system_prompt = (PROMPTS_DIR / "visual_plan.md").read_text(encoding="utf-8")

    def plan(self, script: ShortScript) -> VisualPlan:
        lines = "\n".join(
            f"{i}. {line.en}\n   visual note: {line.visual}" for i, line in enumerate(script.lines)
        )
        user = f"Title: {script.title}\nPillar: {script.pillar}\n\nLines:\n{lines}"
        plan = structured_call(self.client, self.system_prompt, user, VisualPlan, effort="low",
                               label=f"visual plan for '{script.title}'")
        return normalize_plan(plan, script)


def normalize_plan(plan: VisualPlan, script: ShortScript) -> VisualPlan:
    """Exactly one scene per line, in order; missing lines become text cards."""
    by_line = {s.line: s for s in plan.scenes if 0 <= s.line < len(script.lines)}
    scenes = [
        by_line.get(i) or Scene(line=i, source="card", stock_query="", ai_prompt="",
                                card_text=line.en[:40], card_subtext="")
        for i, line in enumerate(script.lines)
    ]
    return VisualPlan(scenes=scenes)


class PexelsSource:
    """Free stock photos (Pexels license: free for commercial use, no attribution required)."""

    SEARCH_URL = "https://api.pexels.com/v1/search"

    def __init__(self, api_key: str, session: requests.Session | None = None):
        self.api_key = api_key
        self.session = session or requests.Session()
        self.used_ids: set[int] = set()  # don't repeat a photo within one Short

    def fetch(self, scene: Scene, out_path: Path) -> tuple[Path, str] | None:
        if not scene.stock_query:
            return None
        resp = self.session.get(
            self.SEARCH_URL,
            params={"query": scene.stock_query, "orientation": "portrait", "per_page": 10},
            headers={"Authorization": self.api_key},
            timeout=20,
        )
        resp.raise_for_status()
        for photo in resp.json().get("photos", []):
            if photo["id"] in self.used_ids:
                continue
            url = photo["src"].get("large2x") or photo["src"]["original"]
            image = self.session.get(url, timeout=60)
            image.raise_for_status()
            path = out_path.with_suffix(".jpg")
            path.write_bytes(image.content)
            self.used_ids.add(photo["id"])
            return path, f"Photo by {photo.get('photographer', '?')} on Pexels ({photo.get('url', '')})"
        return None


class AIImageSource:
    """Text-to-image through the Higgsfield SDK (costs credits)."""

    def __init__(self, application: str, arguments: dict, client=None, session: requests.Session | None = None):
        if client is None:
            import higgsfield_client as client
        self.client = client
        self.application = application
        self.arguments = arguments
        self.session = session or requests.Session()

    def fetch(self, scene: Scene, out_path: Path) -> tuple[Path, str] | None:
        if not scene.ai_prompt:
            return None
        result = self.client.subscribe(self.application, arguments={"prompt": scene.ai_prompt, **self.arguments})
        images = result.get("images") if isinstance(result, dict) else None
        if not images:
            return None
        url = images[0]["url"]
        image = self.session.get(url, timeout=120)
        image.raise_for_status()
        suffix = Path(url.split("?")[0]).suffix.lower()
        path = out_path.with_suffix(suffix if suffix in IMAGE_EXTENSIONS else ".png")
        path.write_bytes(image.content)
        return path, f"AI image: {scene.ai_prompt}"


def make_card(text: str, subtext: str, out_path: Path, font_path: Path | None = None) -> Path:
    """A branded 1080x1920 text card: dark gradient, big yellow text, white label."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), NAVY)
    draw = ImageDraw.Draw(img)
    for y in range(height):  # vertical gradient
        t = y / height
        draw.line([(0, y), (width, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(NAVY, NAVY_LIGHT)))

    def font(size):
        if font_path and font_path.exists():
            return ImageFont.truetype(str(font_path), size)
        return ImageFont.load_default(size)

    def fit(txt, size, max_width=width - 140):
        while size > 30 and draw.textlength(txt, font=font(size)) > max_width:
            size = int(size * 0.9)
        return font(size)

    main_font = fit(text, 150)
    y = height * 0.40
    draw.text((width / 2, y), text, font=main_font, fill=YELLOW, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
    if subtext:
        draw.text((width / 2, y + 150), subtext, font=fit(subtext, 64), fill=WHITE, anchor="mm")
    path = out_path.with_suffix(".png")
    img.save(path)
    return path


def gather(plan: VisualPlan, out_dir: Path, sources: dict, font_path: Path | None = None,
           log=print) -> tuple[list[Path], list[Credit]]:
    """Fetches one image per scene into out_dir (named 00, 01, ... so render order is line order)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths, credits = [], []
    for scene in plan.scenes:
        target = out_dir / f"{scene.line:02d}"
        # Planned source first, then the other remote source, then a card.
        order = [scene.source] + [s for s in ("stock", "ai") if s != scene.source]
        found = None
        for name in order:
            source = sources.get(name)
            if name == "card" or source is None:
                continue
            try:
                found = source.fetch(scene, target)
            except Exception as e:  # a failed download shouldn't sink the whole Short
                log(f"  line {scene.line}: {name} failed ({e})")
            if found:
                paths.append(found[0])
                credits.append(Credit(scene.line, name, found[1]))
                break
        if not found:
            text = scene.card_text or scene.stock_query or f"#{scene.line + 1}"
            paths.append(make_card(text, scene.card_subtext, target, font_path))
            credits.append(Credit(scene.line, "card", text))
    (out_dir / "plan.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    (out_dir / "credits.json").write_text(json.dumps([asdict(c) for c in credits], indent=2), encoding="utf-8")
    return paths, credits


def build_sources(config) -> dict:
    """Stock needs PEXELS_API_KEY; AI images need Higgsfield credentials and allow_ai."""
    sources = {}
    if os.environ.get("PEXELS_API_KEY"):
        sources["stock"] = PexelsSource(os.environ["PEXELS_API_KEY"])
    settings = config.visuals
    if settings.get("allow_ai", False) and settings.get("ai_application"):
        sources["ai"] = AIImageSource(settings["ai_application"], dict(settings.get("ai_arguments", {})))
    return sources


def existing_images(folder: Path) -> list[Path]:
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS) if folder.is_dir() else []
