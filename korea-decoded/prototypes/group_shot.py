"""Whole-cast still: every character seated behind one long, gently curved news desk with the channel logo
on its front, for the channel intro, the banner and thumbnails.

    python3 group_shot.py out.jpg       # run from korea-decoded/ (cast images: cast/fetch.sh)

Each character is drawn once at full size by dialog.Puppet (same rig as the episodes), then scaled and
placed so its collar sits just above the desk; the desk covers everything below its top. The desk bulges
toward the camera in the middle, so Master K (centre) is nearest and the ends sit a little farther back.
"""
import sys

from PIL import Image, ImageDraw

import dialog as dg
import episode as ep
import newsrig as nr

H = nr.H
WIDTH = ep.WORLD_W  # the whole studio: a still for the banner, and the camera can pan across it
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
SEATS = ["tech", "money", "news", "hidden", "kangfree", "k", "joe", "chef", "kpop", "travel"]  # left to right
# Size: the source drawings differ (big glasses, small faces), so the scale moves halfway (square root)
# toward equal eye spacing, and SIZE nudges what is left. K, in the middle, is a touch bigger.
BASE, SEP_REF = 0.47, 125
SIZE = {"k": 1.05, "kangfree": 1.07, "chef": 0.95}
REACT = {"kangfree": 0.9, "joe": 0.9, "kpop": 0.9}  # mouths open: the rest of the desk reacting
DESK_TOP, BULGE, HALF = 850, 45, 1250  # front edge at the ends, how far the middle comes forward, half width
DESK_DEPTH = 45  # desk top surface, back edge to front edge


def cutout(key, gaze=(0.0, 0.1), env=0.0):
    """The character drawn at full rig size, on a transparent frame whose collar line is y = COLLAR_Y.
    gaze also leans the head that way; env > 0.45 opens the mouth."""
    spec = {**CAST[key], "head": f"{C}{key}_head.png", "body": f"{C}{key}_body.png", "ref": f"{C}{key}_ref.png",
            "x": 450}
    p = dg.Puppet(spec)
    frame = Image.new("RGBA", (900, H), (0, 0, 0, 0))
    p.draw(frame, 0.0, gaze, 0.0, env, 0.0, mood=spec.get("mood"))
    return frame, p.label, p.rig["sep"]


def front_edge(dx):
    """y of the desk's front edge at dx from the middle: lowest (nearest) in the middle."""
    u = min(1.0, abs(dx) / HALF)
    return DESK_TOP + BULGE * (1 - u * u)


def desk(img, cx, plates):
    w = img.width
    d = ImageDraw.Draw(img)
    front = [(x, front_edge(x - cx)) for x in range(0, w + 1, 20)]
    back = [(x, y - DESK_DEPTH) for x, y in front]
    d.polygon(back + front[::-1], fill=(44, 52, 72))  # top surface
    d.polygon(front + [(w, H), (0, H)], fill=(22, 26, 36))  # front panel
    d.line(front, fill=nr.YELLOW, width=12)
    nr.logo_mark(img, cx, round((front_edge(0) + H) / 2 + 45), 120)  # channel mark in the middle of the front
    d = ImageDraw.Draw(img)
    f = nr.font(24)
    for x, label in plates:
        y = front_edge(x - cx) + 40
        tw = d.textlength(label, font=f)
        d.rounded_rectangle((x - tw / 2 - 14, y - 20, x + tw / 2 + 14, y + 20), 8, fill=nr.YELLOW)
        d.text((x, y), label, font=f, fill=nr.BLACK, anchor="mm")


def make(width=WIDTH):
    img = ep.studio_backdrop("assets/studio/seoul_dusk.jpg", 0.8, 1.5).convert("RGBA")
    if img.width != width:
        img = img.resize((width, H))
    cx = width // 2
    n = len(SEATS)
    plates, placed = [], []
    for i, key in enumerate(SEATS):
        dx = (i - (n - 1) / 2) * (2 * HALF * 0.92 / (n - 1))
        u = abs(dx) / HALF
        gx = max(-0.8, min(0.8, -dx / HALF * 1.2))  # everyone glances toward the middle
        frame, label, sep = cutout(key, (gx, 0.05), REACT.get(key, 0.0))
        scale = BASE * SIZE.get(key, 1.0) * (SEP_REF / sep) ** 0.5 * (1.04 - 0.1 * u * u)  # ends a bit farther
        placed.append((u, dx, frame, scale))
        plates.append((cx + dx, label))
    for u, dx, frame, scale in sorted(placed, key=lambda p: -p[0]):  # farther (ends) first
        f = frame.resize((round(frame.width * scale), round(frame.height * scale)), Image.LANCZOS)
        collar = front_edge(dx) - DESK_DEPTH - 170 * scale / 0.47
        img.alpha_composite(f, (round(cx + dx - f.width / 2), round(collar - dg.COLLAR_Y * scale)))
    desk(img, cx, plates)
    return img.convert("RGB")


if __name__ == "__main__":
    make().save(sys.argv[1], quality=92)
