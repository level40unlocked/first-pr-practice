"""YouTube thumbnail (1280x720) from the show's own parts: studio backdrop, one rigged character with a
big reaction face, one picture from the episode, and 2-4 words of big text.

    python3 thumbnail.py spec.json out.jpg

spec: {"background": "...jpg", "picture": "...png", "character": {<Puppet spec>, "mouth": "open",
       "gaze": [0.8, 0], "mood": null}, "text": ["IT WON'T", "LEAVE"], "text_color": [255, 212, 0]}
Paths are relative to the current directory, like the episode scripts.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

import dialog as dg
import newsrig as nr

TW, TH = 1280, 720
_HERE = os.path.dirname(os.path.abspath(__file__))
HANGUL_FONT = os.path.join(_HERE, "..", "assets", "fonts", "BlackHanSans-Regular.ttf")  # OFL
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"


def flag_kr(h):
    """South Korean flag at height h (color emoji glyph, rendered at its native size and scaled)."""
    f = ImageFont.truetype(EMOJI_FONT, 109)
    img = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((0, 0), "\U0001F1F0\U0001F1F7", font=f, embedded_color=True)
    img = img.crop(img.getbbox())
    return img.resize((round(img.width * h / img.height), h), Image.LANCZOS)


def badge(text, h=58):
    """Location chip: flag + white text on navy, e.g. "BUSAN, KOREA"."""
    f = nr.font(int(h * 0.55))
    fl = flag_kr(int(h * 0.62))
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = int(probe.textlength(text, font=f)) + fl.width + int(h * 0.9)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=nr.NAVY + (240,), outline=nr.WHITE, width=3)
    img.alpha_composite(fl, (int(h * 0.35), (h - fl.height) // 2))
    d.text((int(h * 0.35) + fl.width + int(h * 0.2), h / 2), text, font=f, fill=nr.WHITE, anchor="lm")
    return img


def name_tag(hangul, roman, size=74):
    """Yellow sticker with a hangul name and its romanization, with a pointer at the bottom middle."""
    fk, fr = ImageFont.truetype(HANGUL_FONT, size), nr.font(int(size * 0.34))
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = int(max(probe.textlength(hangul, font=fk), probe.textlength(roman, font=fr))) + size
    h = int(size * 1.55)
    tip = int(size * 0.35)
    img = Image.new("RGBA", (w + 8, h + tip + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 4, w + 4, h + 4), 18, fill=nr.YELLOW, outline=nr.BLACK, width=5)
    cx = (w + 8) // 2
    d.polygon([(cx - tip, h), (cx + tip, h), (cx, h + tip + 2)], fill=nr.YELLOW, outline=nr.BLACK)
    d.rectangle((cx - tip + 4, h - 2, cx + tip - 4, h + 3), fill=nr.YELLOW)
    d.text((cx, 4 + size * 0.62), hangul, font=fk, fill=nr.BLACK, anchor="mm")
    d.text((cx, 4 + size * 1.25), roman, font=fr, fill=nr.BLACK, anchor="mm")
    return img


def stamp(text, size=46, color=(220, 38, 38)):
    """Rubber-stamp label ("REAL NEWS"): bold red text in a double outline, tilted."""
    f = nr.font(size)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w, h = int(probe.textlength(text, font=f)) + size, int(size * 1.6)
    img = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 6, w + 6, h + 6), 10, fill=(255, 255, 255, 235), outline=color, width=6)
    d.rounded_rectangle((13, 13, w - 1, h - 1), 6, outline=color, width=2)
    d.text(((w + 12) / 2, (h + 12) / 2), text, font=f, fill=color, anchor="mm")
    return img.rotate(8, expand=True, resample=Image.BICUBIC)


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
    pw, ph = spec.get("picture_size", (660, 400))
    flat = framed(spec["picture"], pw, ph)
    tag = spec.get("tag")  # {"hangul": "부캉이", "roman": "BUKANG-I", "at": [0.47, 0.6]} (share of the picture)
    if tag:  # stuck on the picture so it tilts with it; the pointer lands on "at"
        nt = name_tag(tag["hangul"], tag["roman"], tag.get("size", 74))
        tx = int(12 + tag["at"][0] * pw - nt.width / 2)
        ty = int(12 + tag["at"][1] * ph - nt.height)
        pad = max(0, -ty)
        big = Image.new("RGBA", (flat.width, flat.height + pad), (0, 0, 0, 0))
        big.alpha_composite(flat, (0, pad))
        big.alpha_composite(nt, (max(0, min(tx, flat.width - nt.width)), ty + pad))
        flat = big
    pic = flat.rotate(-3, expand=True, resample=Image.BICUBIC)
    px, py = TW - pic.width - 30, spec.get("picture_y", 70)
    shadowed(canvas, pic, (px, py))
    if spec.get("badge"):
        b = badge(spec["badge"])
        shadowed(canvas, b, (px + 10, max(12, py + (pic.height - flat.height) // 2 - 22)), radius=8, offset=(4, 6))
    # character: left, big, cut by the bottom edge
    if spec.get("character_image"):  # a drawn reaction pose (transparent PNG) instead of the rig
        ch = Image.open(spec["character_image"]).convert("RGBA")
        if ch.getchannel("A").getextrema()[0] == 255:  # no transparency: cut out the flat background
            ch = nr.remove_bg(ch).convert("RGBA")
        ch = ch.crop(ch.getbbox())
    else:
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
    if spec.get("stamp"):  # {"text": "REAL NEWS"}: sits just above the headline's left edge
        st = stamp(spec["stamp"]["text"], spec["stamp"].get("size", 46))
        left = TW - 110 - max(d.textlength(t, font=f) for t in lines)
        shadowed(canvas, st, (int(left) - 10, int(y - st.height + 14)), radius=6, offset=(3, 5))
        d = ImageDraw.Draw(canvas)
    for t in lines:
        d.text((TW - 110, y), t, font=f, fill=tuple(spec.get("text_color", nr.YELLOW)), anchor="ra",
               stroke_width=max(6, size // 12), stroke_fill=nr.BLACK)
        y += size * 1.02
    nr.logo_mark(canvas, TW - 60, 52, 64)
    return canvas.convert("RGB")


if __name__ == "__main__":
    make(json.load(open(sys.argv[1]))).save(sys.argv[2], quality=92)
