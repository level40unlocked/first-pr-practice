"""Whole-cast still: every character seated at one long desk (one row) or on two tiers (front desk +
raised back row), for the channel intro and thumbnails.

    python3 group_shot.py row out.jpg       # run from korea-decoded/ (cast images: cast/fetch.sh)
    python3 group_shot.py tiers out.jpg
    python3 group_shot.py supper out.jpg    # Last Supper composition: one long table, K in the middle

Each character is drawn once at full size by dialog.Puppet (same rig as the episodes), then scaled and
placed so its collar sits on the row's collar line; the desk covers everything below the desk top.
"""
import sys

from PIL import Image, ImageDraw

import dialog as dg
import episode as ep
import newsrig as nr

W, H = nr.W, nr.H
C = "cast/"
EXPERT = {"shoulders": 520, "white_lens": True}
CAST = {  # key: rig spec + nameplate
    "k": {"label": "MASTER K"},
    "kangfree": {"label": "DR. KANGFREE", "head_ratio": 0.74, "shoulders": 500, "chin_drop": 0.12},
    "joe": {"label": "WHISTLE JOE", **EXPERT, "head_ratio": 0.68, "chin_drop": 0.16},
    "chef": {"label": "CHEF CLAMSAY", **EXPERT, "head_ratio": 0.74, "chin_drop": 0.16, "mood": "frown"},
    "news": {"label": "NEWS", **EXPERT},
    "kpop": {"label": "K-POP", **EXPERT},
    "hidden": {"label": "HISTORY", **EXPERT},
    "money": {"label": "MONEY", **EXPERT, "head_ratio": 0.68},
    "tech": {"label": "BILL DUSK", **EXPERT, "head_ratio": 0.68, "chin_drop": 0.08},
    "travel": {"label": "TRAVEL", **EXPERT},
}
LAYOUTS = {
    # rows back to front: (keys left to right, scale, collar y, desk top y, x spacing)
    "row": [(["travel", "money", "news", "kangfree", "k", "joe", "chef", "kpop", "hidden", "tech"],
             0.56, 700, 885, 186)],
    "tiers": [(["news", "hidden", "kpop", "tech", "travel"], 0.46, 330, 480, 365),
              (["chef", "kangfree", "k", "joe", "money"], 0.6, 720, 895, 365)],
}


def cutout(key, gaze=(0.0, 0.1), env=0.0, mood=None):
    """The character drawn at full rig size, on a transparent frame whose collar line is y = COLLAR_Y.
    gaze also leans the head that way; env > 0.45 opens the mouth."""
    spec = {**CAST[key], "head": f"{C}{key}_head.png", "body": f"{C}{key}_body.png", "ref": f"{C}{key}_ref.png",
            "x": 450}
    p = dg.Puppet(spec)
    frame = Image.new("RGBA", (900, H), (0, 0, 0, 0))
    p.draw(frame, 0.0, gaze, 0.0, env, 0.0, mood=mood or spec.get("mood"))
    return frame, p.label, p.rig["sep"]


def desk(img, top, bottom, x0, x1, plates, size):
    d = ImageDraw.Draw(img)
    d.polygon([(x0, top), (x1, top), (x1 + 40, bottom), (x0 - 40, bottom)], fill=(22, 26, 36))
    d.rectangle((x0, top, x1, top + 10), fill=nr.YELLOW)
    f = nr.font(size)
    for x, label in plates:
        tw = d.textlength(label, font=f)
        y = top + 18 + size * 0.9
        d.rounded_rectangle((x - tw / 2 - 12, y - size * 0.85, x + tw / 2 + 12, y + size * 0.85), 8, fill=nr.YELLOW)
        d.text((x, y), label, font=f, fill=nr.BLACK, anchor="mm")


def make(layout):
    bg = ep.studio_backdrop("assets/studio/seoul_dusk.jpg", 0.8, 1.5)
    x0 = (bg.width - W) // 2
    img = bg.crop((x0, 0, x0 + W, H)).convert("RGBA")
    rows = LAYOUTS[layout]
    for i, (keys, scale, collar, top, gap) in enumerate(rows):
        left = W / 2 - gap * (len(keys) - 1) / 2
        plates = []
        for j, key in enumerate(keys):
            frame, label, _ = cutout(key)
            f = frame.resize((round(frame.width * scale), round(frame.height * scale)), Image.LANCZOS)
            cx = left + j * gap
            img.alpha_composite(f, (round(cx - f.width / 2), round(collar - dg.COLLAR_Y * scale)))
            plates.append((cx, label))
        bottom = rows[i + 1][3] if i + 1 < len(rows) else H
        desk(img, top, bottom, left - gap * 0.55, left + gap * (len(keys) - 0.45), plates, round(34 * scale))
    return img.convert("RGB")


# Last Supper: groups of two or three lean toward each other, K sits alone in the middle under the big
# window. (key, x, scale, lean in degrees (+ = toward the right), gaze x, mouth open, mood)
SUPPER_W = ep.WORLD_W  # the whole studio width: a still for banners, and the camera can pan across it
# Size: the source drawings differ (big glasses, small faces), so eye spacing is only half the story: the
# scale moves halfway (square root) toward equal eye spacing, and "size" nudges what is left.
BASE, SEP_REF = 0.47, 125
SUPPER = [  # x is the offset from the middle of the table; size is relative to SEP
    ("tech", -1180, 1.0, 3, 0.6, 0.0, None), ("money", -960, 1.0, -2, 0.5, 0.6, None),
    ("news", -740, 1.0, -5, 0.7, 0.0, None),
    ("hidden", -480, 1.0, 4, 0.7, 0.0, None), ("kangfree", -260, 1.07, -6, 0.9, 0.9, None),
    ("k", 0, 1.05, 0, 0.0, 0.0, None),
    ("joe", 260, 1.0, 6, -0.9, 0.9, None), ("chef", 485, 0.95, 3, -0.6, 0.0, None),
    ("kpop", 800, 1.0, 5, -0.7, 0.9, None), ("travel", 1060, 1.0, -3, -0.5, 0.0, None),
]
TABLE_TOP, TABLE_FRONT = 850, 935
FRAME = (70, 60, 50, 255)


def room(bg):
    """Dark back wall with three arched windows onto the skyline; the middle one, behind K, is the largest."""
    w, cx = bg.width, bg.width // 2
    wall = Image.new("RGBA", bg.size, (14, 18, 34, 230))
    d = ImageDraw.Draw(wall)
    windows = [(cx - 200, 250, cx + 200, 800), (cx - 690, 360, cx - 450, 760), (cx + 450, 360, cx + 690, 760)]
    for x0, y0, x1, y1 in windows:
        d.rectangle((x0, y0 + (x1 - x0) // 2, x1, y1), fill=(0, 0, 0, 0))
        d.pieslice((x0, y0, x1, y0 + (x1 - x0)), 180, 360, fill=(0, 0, 0, 0))  # arched top
    for x0, y0, x1, y1 in windows:  # frames
        d.arc((x0 - 6, y0 - 6, x1 + 6, y0 + (x1 - x0) + 6), 180, 360, fill=FRAME, width=12)
        d.line((x0, y0 + (x1 - x0) // 2, x0, y1), fill=FRAME, width=12)
        d.line((x1, y0 + (x1 - x0) // 2, x1, y1), fill=FRAME, width=12)
    side = w * 0.2
    for x, sgn in ((0, 1), (w, -1)):  # side walls in perspective, like the painting's tapestries
        d.polygon([(x, 0), (x + sgn * side, 200), (x + sgn * side, 820), (x, 900)], fill=(24, 28, 46, 255))
        for k in range(1, 5):  # wall panels
            px = x + sgn * side * k / 5
            d.line((px, 40 * k, px, 900 - 16 * k), fill=(40, 46, 70, 255), width=4)
    d.polygon([(0, 0), (w, 0), (w - side, 200), (side, 200)], fill=(20, 24, 40, 255))  # ceiling
    for k in range(1, 10):  # coffered ceiling lines toward the vanishing point behind K
        d.line((k * w / 10, 0, side + k * (w - 2 * side) / 10, 200), fill=(40, 46, 70, 255), width=3)
    d.line((side, 200, w - side, 200), fill=(40, 46, 70, 255), width=4)
    bg.alpha_composite(wall)


def table(img, plates, bottles):
    w = img.width
    d = ImageDraw.Draw(img)
    d.polygon([(40, TABLE_TOP), (w - 40, TABLE_TOP), (w, TABLE_FRONT), (0, TABLE_FRONT)], fill=(236, 232, 220))
    d.rectangle((0, TABLE_FRONT, w, H), fill=(214, 208, 192))
    for x in range(60, w, 160):  # cloth folds
        d.line((x, TABLE_FRONT + 6, x + 10, H), fill=(196, 188, 170), width=3)
    d.rectangle((0, TABLE_FRONT - 4, w, TABLE_FRONT + 4), fill=nr.YELLOW)
    # Korean dinner: ramen, kimchi or rice in front of everyone, chopsticks, green soju bottles
    for i, (x, _) in enumerate(plates):
        y = TABLE_TOP + 40
        d.ellipse((x - 46, y - 14, x + 46, y + 14), fill=(250, 250, 250), outline=(120, 120, 120), width=2)
        if i % 3 == 0:  # ramen
            d.ellipse((x - 36, y - 10, x + 36, y + 8), fill=(214, 90, 40))
            d.arc((x - 24, y - 8, x + 24, y + 4), 180, 360, fill=(250, 214, 120), width=4)
        elif i % 3 == 1:  # kimchi
            d.ellipse((x - 30, y - 9, x + 30, y + 7), fill=(200, 40, 30))
        else:  # rice
            d.ellipse((x - 30, y - 16, x + 30, y + 8), fill=(255, 255, 255), outline=(200, 200, 200))
        d.line((x + 52, y - 4, x + 88, y + 20), fill=(160, 160, 160), width=4)  # chopsticks
        d.line((x + 58, y - 8, x + 94, y + 16), fill=(160, 160, 160), width=4)
    for x in bottles:  # soju
        d.rounded_rectangle((x - 16, TABLE_TOP - 70, x + 16, TABLE_TOP + 30), 10, fill=(40, 150, 80))
        d.rectangle((x - 7, TABLE_TOP - 100, x + 7, TABLE_TOP - 66), fill=(40, 150, 80))
        d.rectangle((x - 14, TABLE_TOP - 40, x + 14, TABLE_TOP - 10), fill=(240, 240, 230))
    f = nr.font(22)
    for x, label in plates:  # place cards on the front edge
        tw = d.textlength(label, font=f)
        d.rounded_rectangle((x - tw / 2 - 10, TABLE_FRONT + 22, x + tw / 2 + 10, TABLE_FRONT + 60), 7, fill=nr.YELLOW)
        d.text((x, TABLE_FRONT + 41), label, font=f, fill=nr.BLACK, anchor="mm")


def make_supper(width=SUPPER_W):
    img = ep.studio_backdrop("assets/studio/seoul_dusk.jpg", 1.0, 0.8).convert("RGBA")
    if img.width != width:
        img = img.resize((width, H))
    room(img)
    cx = width // 2
    plates = []
    for key, dx, size, lean, gx, env, mood in SUPPER:
        frame, label, sep = cutout(key, (gx, 0.05), env, mood)
        scale = BASE * size * (SEP_REF / sep) ** 0.5
        pivot = (450, dg.COLLAR_Y + 300)  # lean from the seat, below the table top
        frame = frame.rotate(-lean, resample=Image.BICUBIC, center=pivot)
        f = frame.resize((round(frame.width * scale), round(frame.height * scale)), Image.LANCZOS)
        collar = TABLE_TOP - 130 * scale / 0.47
        img.alpha_composite(f, (round(cx + dx - f.width / 2), round(collar - dg.COLLAR_Y * scale)))
        plates.append((cx + dx, label))
    table(img, plates, [cx - 610, cx + 130, cx + 645])  # in the gaps between the groups
    return img.convert("RGB")


if __name__ == "__main__":
    (make_supper() if sys.argv[1] == "supper" else make(sys.argv[1])).save(sys.argv[2], quality=92)
