"""EP.4 thumbnails (1280x720): Offbeat on the left, two pictures (Fin.K.L / IVE) on the right, big question text.
    cd episodes/ep04 && python3 make_thumbs.py
"""
import os, sys
sys.path.insert(0, "../../prototypes")
from PIL import Image, ImageDraw
import thumbnail as tb
import newsrig as nr

S = "../../assets/stock/ep04/"
CAST = "../../cast/"
OFFBEAT = {"head": CAST + "kpop_head.png", "body": CAST + "kpop_body.png", "ref": CAST + "kpop_ref.png", "label": "OFFBEAT",
           "shoulders": 520, "white_lens": True, "mouth": "open", "gaze": [0.8, 0.0]}
TW, TH = tb.TW, tb.TH


def vs_badge(size=130):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((4, 4, size - 4, size - 4), fill=(220, 38, 38), outline=nr.WHITE, width=7)
    d.text((size / 2, size / 2), "VS", font=nr.font(int(size * 0.46)), fill=nr.WHITE, anchor="mm", stroke_width=3, stroke_fill=nr.BLACK)
    return img


def thumb(left_pic, right_pic, text, out, vs=False, size=116, left_crop=None, right_crop=None):
    canvas = tb.backdrop("../../assets/studio/seoul_dusk.jpg").convert("RGBA")
    # two cards, right side, tilted opposite ways
    cw, chh = 350, 420
    cards = []
    for path, ang, crop in ((left_pic, 4, left_crop), (right_pic, -4, right_crop)):
        src = path
        if crop:
            im = Image.open(path).convert("RGB").crop(crop)
            src = "/tmp/_thumb_crop_%d.png" % len(cards)
            im.save(src)
        cards.append(tb.framed(src, cw, chh, border=12).rotate(ang, expand=True, resample=Image.BICUBIC))
    x0 = 470
    tb.shadowed(canvas, cards[0], (x0, 70))
    tb.shadowed(canvas, cards[1], (x0 + 390, 70))
    if vs:
        b = vs_badge()
        tb.shadowed(canvas, b, (x0 + 370 - b.width // 2 + 10, 70 + chh // 2 - b.height // 2), radius=8, offset=(4, 6))
    # Offbeat, left
    ch = tb.character(OFFBEAT)
    s = 880 / ch.height
    ch = ch.resize((round(ch.width * s), round(ch.height * s)), Image.LANCZOS)
    tb.shadowed(canvas, ch, (-70, TH - ch.height + 190), radius=18, offset=(0, 0))
    # text, bottom right
    d = ImageDraw.Draw(canvas)
    f = nr.font(size)
    while max(d.textlength(t, font=f) for t in text) > 760 and size > 60:
        size -= 4
        f = nr.font(size)
    y = TH - 40 - len(text) * size * 1.02
    for t in text:
        d.text((TW - 60, y), t, font=f, fill=tuple(nr.YELLOW), anchor="ra", stroke_width=max(6, size // 12), stroke_fill=nr.BLACK)
        y += size * 1.02
    nr.logo_mark(canvas, TW - 60, 52, 64)
    canvas.convert("RGB").save(out, quality=92)
    print(out)


os.makedirs("thumbs", exist_ok=True)
FIN = S + "recent_4.jpg"
IVE = S + "ive_poster.jpg"
thumb(FIN, IVE, ["FIN.K.L", "IS BACK?!"], "thumbs/thumb_A.jpg")
thumb(FIN, IVE, ["FIN.K.L", "VS IVE?!"], "thumbs/thumb_B.jpg", vs=True)
thumb(S + "img_7.jpg", S + "ive_4.jpg", ["BACK AFTER", "21 YEARS?!"], "thumbs/thumb_C.jpg")
