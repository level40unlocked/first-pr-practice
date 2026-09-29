"""YouTube thumbnail (1280x720) from the show's own parts: studio backdrop, one rigged character with a
big reaction face, one picture from the episode, and 2-4 words of big text.

    python3 thumbnail.py spec.json out.jpg

spec: {"background": "...jpg", "picture": "...png", "character": {<Puppet spec>, "mouth": "open",
       "gaze": [0.8, 0], "mood": null}, "text": ["IT WON'T", "LEAVE"], "text_color": [255, 212, 0]}
Paths are relative to the current directory, like the episode scripts.
"""
import json
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import dialog as dg
import newsrig as nr

TW, TH = 1280, 720


def backdrop(path):
    img = Image.open(path).convert("RGB")
    s = max(TW / img.width, TH / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0, y0 = (img.width - TW) // 2, (img.height - TH) // 3
    img = img.crop((x0, y0, x0 + TW, y0 + TH)).filter(ImageFilter.GaussianBlur(3))
    return ImageEnhance.Brightness(img).enhance(0.55)


def character(spec):
    """The character cut out (RGBA, tight box) with its reaction face."""
    p = dg.Puppet({**spec, "x": 800})
    frame = Image.new("RGBA", (1600, 1400), (0, 0, 0, 0))
    mouth = spec.get("mouth", "open")
    env = {"closed": 0.0, "mid": 0.3, "open": 1.0}[mouth]
    p.draw(frame, 0, tuple(spec.get("gaze", (0.8, 0.0))), 0, env, 0, mood=spec.get("mood"))
    return frame.crop(frame.getbbox())


def framed(picture, w, h, border=12):
    img = Image.open(picture).convert("RGB")
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0, y0 = (img.width - w) // 2, (img.height - h) // 2
    img = img.crop((x0, y0, x0 + w, y0 + h))
    out = Image.new("RGBA", (w + 2 * border, h + 2 * border), nr.WHITE + (255,))
    out.paste(img, (border, border))
    return out


def shadowed(canvas, piece, xy, radius=14, offset=(10, 14)):
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mask = Image.new("RGBA", piece.size, (0, 0, 0, 170))
    shadow.paste(mask, (xy[0] + offset[0], xy[1] + offset[1]), piece.getchannel("A"))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(radius)))
    canvas.alpha_composite(piece, xy)


def make(spec):
    canvas = backdrop(spec["background"]).convert("RGBA")
    # picture: right side, tilted a little so it reads as a "photo" card
    pic = framed(spec["picture"], 660, 400).rotate(-3, expand=True, resample=Image.BICUBIC)
    shadowed(canvas, pic, (TW - pic.width - 30, 70))
    # character: left, big, cut by the bottom edge
    ch = character(spec["character"])
    s = spec.get("character_height", 700) / ch.height
    ch = ch.resize((round(ch.width * s), round(ch.height * s)), Image.LANCZOS)
    shadowed(canvas, ch, (spec.get("character_x", -20), TH - ch.height + 150), radius=18, offset=(0, 0))
    # text: bottom right, clear of the duration badge in the corner
    d = ImageDraw.Draw(canvas)
    lines = spec["text"]
    size = spec.get("text_size", 118)
    f = nr.font(size)
    while max(d.textlength(t, font=f) for t in lines) > 760 and size > 60:
        size -= 4
        f = nr.font(size)
    y = TH - 40 - len(lines) * size * 1.02
    for t in lines:
        d.text((TW - 110, y), t, font=f, fill=tuple(spec.get("text_color", nr.YELLOW)), anchor="ra",
               stroke_width=max(6, size // 12), stroke_fill=nr.BLACK)
        y += size * 1.02
    nr.logo_mark(canvas, TW - 60, 52, 64)
    return canvas.convert("RGB")


if __name__ == "__main__":
    make(json.load(open(sys.argv[1]))).save(sys.argv[2], quality=92)
