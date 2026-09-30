"""Whole-cast still: every character seated at one long desk (one row) or on two tiers (front desk +
raised back row), for the channel intro and thumbnails.

    python3 group_shot.py row out.jpg       # run from korea-decoded/ (cast images: cast/fetch.sh)
    python3 group_shot.py tiers out.jpg

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
    "tech": {"label": "TECH", **EXPERT, "head_ratio": 0.68, "chin_drop": 0.08},
    "travel": {"label": "TRAVEL", **EXPERT},
}
LAYOUTS = {
    # rows back to front: (keys left to right, scale, collar y, desk top y, x spacing)
    "row": [(["travel", "money", "news", "kangfree", "k", "joe", "chef", "kpop", "hidden", "tech"],
             0.56, 700, 885, 186)],
    "tiers": [(["news", "hidden", "kpop", "tech", "travel"], 0.46, 330, 480, 365),
              (["chef", "kangfree", "k", "joe", "money"], 0.6, 720, 895, 365)],
}


def cutout(key):
    """The character drawn at full rig size, on a transparent frame whose collar line is y = COLLAR_Y."""
    spec = {**CAST[key], "head": f"{C}{key}_head.png", "body": f"{C}{key}_body.png", "ref": f"{C}{key}_ref.png",
            "x": 450}
    p = dg.Puppet(spec)
    frame = Image.new("RGBA", (900, H), (0, 0, 0, 0))
    p.draw(frame, 0.0, (0.0, 0.1), 0.0, 0.0, 0.0, mood=spec.get("mood"))
    return frame, p.label


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
            frame, label = cutout(key)
            f = frame.resize((round(frame.width * scale), round(frame.height * scale)), Image.LANCZOS)
            cx = left + j * gap
            img.alpha_composite(f, (round(cx - f.width / 2), round(collar - dg.COLLAR_Y * scale)))
            plates.append((cx, label))
        bottom = rows[i + 1][3] if i + 1 < len(rows) else H
        desk(img, top, bottom, left - gap * 0.55, left + gap * (len(keys) - 0.45), plates, round(34 * scale))
    return img.convert("RGB")


if __name__ == "__main__":
    make(sys.argv[1]).save(sys.argv[2], quality=92)
