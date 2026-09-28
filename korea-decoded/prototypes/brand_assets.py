"""Writes the channel mark (yellow disc + navy round glasses) as transparent PNGs.

    python prototypes/brand_assets.py   # -> assets/brand/watermark_150.png, logo_mark_800.png

watermark_150.png is the YouTube branding watermark (Studio > Customization > Branding).
"""

from pathlib import Path

from PIL import Image, ImageDraw

import newsrig as nr

OUT = Path(__file__).resolve().parent.parent / "assets" / "brand"


def mark(size: int) -> Image.Image:
    big = size * 4  # draw large, then downsample for smooth edges
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, big - 1, big - 1), fill=nr.YELLOW + (255,))
    nr.glasses_logo(draw, big / 2, big / 2, big, nr.NAVY)
    return img.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    mark(150).save(OUT / "watermark_150.png")
    mark(800).save(OUT / "logo_mark_800.png")
