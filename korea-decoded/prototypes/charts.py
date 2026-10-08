"""Animated explainer graphics for the screen box: bars, ranking, donut, timeline, icons, big text, letters, steps, words.

    import charts; img = charts.draw(spec, w, h, t)      # PIL image, t = seconds since the graphic appeared

spec["type"] picks the graphic; everything is drawn on the brand navy and eased in, so the box never sits still.
Designed at 960x540 (the box beside the speaker) and scaled to any box size.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

import newsrig as nr

EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
HANGUL_FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "BlackHanSans-Regular.ttf")
PALE = (190, 200, 225)
BAR = (120, 140, 190)
RED = (235, 70, 70)


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def pop(u):
    """Overshoot ease for pop-in (0 -> 1.08 -> 1)."""
    u = min(max(u, 0.0), 1.0)
    return 1 + 2.4 * (u - 1) ** 3 + 1.4 * (u - 1) ** 2 if u < 1 else 1.0


def _base(w, h):
    img = Image.new("RGB", (w, h), nr.BRAND_NAVY)
    return img, ImageDraw.Draw(img), w / 960


def _title(d, spec, w, s, y=50):
    if spec.get("title"):
        f = nr.font(int(30 * s))
        while d.textlength(spec["title"], font=f) > w - 60 * s and f.size > 14:
            f = nr.font(f.size - 2)
        d.text((w / 2, y * s), spec["title"], font=f, fill=nr.YELLOW, anchor="mm")


def _fmt(v, spec):
    dec = spec.get("decimals", 0)
    return f"{spec.get('prefix', '')}{v:,.{dec}f}{spec.get('suffix', '')}"


def _emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    img = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((0, 0), ch, font=f, embedded_color=True)
    box = img.getbbox()
    img = img.crop(box) if box else img
    return img.resize((max(1, round(img.width * size / img.height)), size), Image.LANCZOS)


def bars(spec, w, h, t):
    img, d, s = _base(w, h)
    _title(d, spec, w, s)
    items = spec["bars"]
    n = len(items)
    top, base = 120 * s, h - 95 * s
    maxv = max(b["value"] for b in items)
    slot = (w - 120 * s) / n
    bw = min(slot * 0.62, 220 * s)
    for k, b in enumerate(items):
        u = ease((t - 0.2 - 0.3 * k) / 1.0)
        x = 60 * s + slot * (k + 0.5)
        bh = (base - top) * 0.88 * b["value"] / maxv * u
        col = nr.YELLOW if b.get("hl") else BAR
        d.rectangle((x - bw / 2, base - bh, x + bw / 2, base), fill=col)
        if u > 0.05:
            shown = b["text"] if (b.get("text") and u > 0.98) else _fmt(b["value"] * u, spec)
            d.text((x, base - bh - 26 * s), shown, font=nr.font(int(38 * s)), fill=nr.WHITE, anchor="mm")
        d.text((x, base + 34 * s), b["label"], font=nr.font(int(26 * s)), fill=PALE, anchor="mm")
    d.line((40 * s, base, w - 40 * s, base), fill=PALE, width=max(2, int(3 * s)))
    if spec.get("badge"):
        u = pop((t - 1.4) / 0.5)
        if u > 0:
            f = nr.font(int(52 * s * min(u, 1.1)))
            tw = d.textlength(spec["badge"], font=f)
            bx, by = w - 70 * s - tw / 2, 120 * s
            d.rounded_rectangle((bx - tw / 2 - 22 * s, by - 40 * s, bx + tw / 2 + 22 * s, by + 40 * s), 18 * s, fill=RED)
            d.text((bx, by), spec["badge"], font=f, fill=nr.WHITE, anchor="mm")
    return img


def hbars(spec, w, h, t):
    """Ranking: horizontal bars; values are only used for length unless show_values is set."""
    img, d, s = _base(w, h)
    _title(d, spec, w, s)
    items = spec["bars"]
    n = len(items)
    top, bottom = 105 * s, h - 55 * s
    row = (bottom - top) / n
    maxv = max(b["value"] for b in items)
    for k, b in enumerate(items):
        u = ease((t - 0.2 - 0.28 * k) / 0.8)
        y = top + row * (k + 0.5)
        col = nr.YELLOW if b.get("hl") else BAR
        x0 = 250 * s
        length = (w - 250 * s - 70 * s) * b["value"] / maxv * u
        d.rectangle((x0, y - row * 0.32, x0 + length, y + row * 0.32), fill=col)
        d.text((x0 - 20 * s, y), b["label"], font=nr.font(int(32 * s)), fill=nr.YELLOW if b.get("hl") else nr.WHITE, anchor="rm")
        if spec.get("show_values") and u > 0.2:
            d.text((x0 + length + 12 * s, y), _fmt(b["value"] * u, spec), font=nr.font(int(26 * s)), fill=nr.WHITE, anchor="lm")
    return img


def donut(spec, w, h, t):
    img, d, s = _base(w, h)
    _title(d, spec, w, s)
    u = ease((t - 0.2) / 1.2)
    cx, cy = w / 2, h / 2 + 25 * s
    r = min(h * 0.34, w * 0.3)
    box = (cx - r, cy - r, cx + r, cy + r)
    d.ellipse(box, fill=BAR)
    share = spec["value"] / 100.0
    d.pieslice(box, -90, -90 + 360 * share * u, fill=nr.YELLOW)
    d.ellipse((cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62), fill=nr.BRAND_NAVY)
    d.text((cx, cy - 8 * s), spec.get("center", f"{spec['value']:.0f}%"), font=nr.font(int(70 * s)), fill=nr.WHITE, anchor="mm")
    if spec.get("label"):
        d.text((cx, cy + 52 * s), spec["label"], font=nr.font(int(26 * s)), fill=PALE, anchor="mm")
    if spec.get("legend"):
        d.text((cx, h - 38 * s), spec["legend"], font=nr.font(int(26 * s)), fill=PALE, anchor="mm")
    return img


def timeline(spec, w, h, t):
    img, d, s = _base(w, h)
    _title(d, spec, w, s)
    ev = spec["events"]
    n = len(ev)
    y = h / 2 + 20 * s
    x0, x1 = 140 * s, w - 140 * s
    prog = ease((t - 0.2) / (0.7 + 0.5 * n))
    d.line((x0, y, x0 + (x1 - x0) * prog, y), fill=PALE, width=max(3, int(6 * s)))
    for k, e in enumerate(ev):
        x = x0 + (x1 - x0) * (k / max(1, n - 1))
        if prog * (n - 1) + 1e-6 < k:
            continue
        u = pop((t - 0.2 - (0.7 + 0.5 * n) * (k / max(1, n - 1)) * 0.75) / 0.5)
        if u <= 0.05:
            continue
        rr = 16 * s * min(u, 1.1)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=nr.YELLOW if e.get("hl") else nr.WHITE)
        up = k % 2 == 0
        ty = y - 105 * s if up else y + 70 * s
        d.text((x, ty), e["year"], font=nr.font(max(10, int(46 * s * min(u, 1.05)))), fill=nr.YELLOW, anchor="mm")
        d.text((x, ty + (46 if up else 44) * s * (1 if up else 1)), e["label"], font=nr.font(int(24 * s)), fill=nr.WHITE, anchor="mm")
    return img


def icons(spec, w, h, t):
    img, d, s = _base(w, h)
    _title(d, spec, w, s)
    items = spec["items"]
    cols = spec.get("cols", 3)
    rows = math.ceil(len(items) / cols)
    top, bottom = 110 * s, h - 40 * s
    cw, rh = w / cols, (bottom - top) / rows
    for k, (em, label) in enumerate(items):
        u = pop((t - 0.2 - 0.3 * k) / 0.5)
        if u <= 0:
            continue
        cx = cw * (k % cols + 0.5)
        cy = top + rh * (k // cols + 0.5)
        size = int(rh * 0.5 * min(u, 1.1))
        e = _emoji(em, max(8, size))
        img.paste(e, (int(cx - e.width / 2), int(cy - rh * 0.14 - e.height / 2)), e)
        d.text((cx, cy + rh * 0.30), label, font=nr.font(int(28 * s)), fill=nr.WHITE, anchor="mm")
    return img


def bigtext(spec, w, h, t):
    img, d, s = _base(w, h)
    if spec.get("title"):
        _title(d, spec, w, s, y=52)
    lines = spec["lines"]
    u = pop((t - 0.1) / 0.45)
    size = int(spec.get("size", 110) * s * min(max(u, 0.2), 1.06))
    col = tuple(spec.get("color", nr.YELLOW))
    mk = (lambda z: ImageFont.truetype(HANGUL_FONT, z)) if spec.get("hangul") else nr.font
    cx = w / 2 + (60 * s if spec.get("thermo") else 0)
    cy = h / 2 - (20 * s if spec.get("sub") else 0)
    f = mk(size)
    for ln in lines:
        while d.textlength(ln, font=f) > (w - 120 * s - (140 * s if spec.get("thermo") else 0)) and f.size > 20:
            f = mk(f.size - 4)
    lh = f.size * 1.15
    for k, ln in enumerate(lines):
        d.text((cx, cy + (k - (len(lines) - 1) / 2) * lh), ln, font=f, fill=col, anchor="mm", stroke_width=max(2, int(4 * s)), stroke_fill=nr.BRAND_NAVY)
    if spec.get("sub"):
        d.text((w / 2, h - 90 * s), spec["sub"], font=nr.font(int(32 * s)), fill=nr.WHITE, anchor="mm")
    if spec.get("thermo"):
        tx, ty0, ty1 = 110 * s, 110 * s, h - 90 * s
        d.rounded_rectangle((tx - 24 * s, ty0, tx + 24 * s, ty1), 24 * s, fill=(60, 75, 120))
        fill_top = ty1 - (ty1 - ty0) * 0.9 * ease((t - 0.3) / 1.4)
        d.rounded_rectangle((tx - 16 * s, fill_top, tx + 16 * s, ty1), 16 * s, fill=RED)
        d.ellipse((tx - 42 * s, ty1 - 22 * s, tx + 42 * s, ty1 + 50 * s), fill=RED)
    return img


def letters(spec, w, h, t):
    img, d, s = _base(w, h)
    _title(d, spec, w, s)
    items = spec["items"]
    n = len(items)
    f_big = ImageFont.truetype(HANGUL_FONT, int(190 * s))
    for k, (ch, label) in enumerate(items):
        u = pop((t - 0.2 - 0.5 * k) / 0.55)
        if u <= 0:
            continue
        cx = w * (k + 0.5) / n
        d.rounded_rectangle((cx - 130 * s, h / 2 - 140 * s, cx + 130 * s, h / 2 + 150 * s), 24 * s, fill=(30, 52, 110))
        d.text((cx, h / 2 - 10 * s), ch, font=ImageFont.truetype(HANGUL_FONT, int(190 * s * min(u, 1.05))), fill=nr.YELLOW, anchor="mm")
        d.text((cx, h / 2 + 195 * s), label, font=nr.font(int(26 * s)), fill=nr.WHITE, anchor="mm")
    return img


def steps(spec, w, h, t):
    img, d, s = _base(w, h)
    _title(d, spec, w, s)
    items = spec["items"]
    n = len(items)
    base = h - 70 * s
    for k, lab in enumerate(items):
        u = ease((t - 0.2 - 0.4 * k) / 0.7)
        bw = (w - 160 * s) / n
        x = 80 * s + bw * k
        bh = (60 + 110 * (k + 1)) * s * u
        d.rectangle((x + 6 * s, base - bh, x + bw - 6 * s, base), fill=nr.YELLOW if k == n - 1 else BAR)
        if u > 0.5:
            d.text((x + bw / 2, base - bh / 2), lab, font=nr.font(int(30 * s)), fill=nr.BLACK if k == n - 1 else nr.WHITE, anchor="mm")
    if spec.get("caption"):
        d.text((w / 2, h - 28 * s), spec["caption"], font=nr.font(int(26 * s)), fill=PALE, anchor="mm")
    return img


def words(spec, w, h, t):
    img, d, s = _base(w, h)
    _title(d, spec, w, s)
    items = spec["words"]
    n = len(items)
    top, bottom = 110 * s, h - 40 * s
    row = (bottom - top) / n
    for k, wd in enumerate(items):
        u = pop((t - 0.2 - 0.45 * k) / 0.5)
        if u <= 0:
            continue
        d.text((w / 2, top + row * (k + 0.5)), wd, font=nr.font(int(row * 0.62 * min(u, 1.06))), fill=nr.YELLOW if k == n - 1 else nr.WHITE, anchor="mm")
    return img


def draw(spec, w, h, t):
    return {"bars": bars, "hbars": hbars, "donut": donut, "timeline": timeline, "icons": icons, "bigtext": bigtext,
            "letters": letters, "steps": steps, "words": words}[spec["type"]](spec, w, h, t)
