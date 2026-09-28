"""Two-character news dialogue: anchor + panel at one desk, camera pushes in on the speaker.

usage: python3 dialog.py scene.json
Reuses the validated puppet pieces from newsrig.py (same folder).
"""
import json
import math
import random
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

import newsrig as nr

W, H, FPS, SW, SH = nr.W, nr.H, nr.FPS, nr.SW, nr.SH
COLLAR_Y, DESK_Y = 520, 800

# News desks (sub-categories). Each gets its own badge colour; experts per desk come later.
CATEGORIES = {
    "current_affairs": ("CURRENT AFFAIRS", (214, 40, 57)),
    "kpop": ("K-POP & ENTERTAINMENT", (236, 72, 153)),
    "hidden_korea": ("HIDDEN KOREA", (124, 58, 237)),
    "korea_vs_world": ("KOREA VS WORLD", (37, 99, 235)),
    "money_business": ("MONEY & BUSINESS", (22, 163, 74)),
    "tech": ("TECH", (8, 145, 178)),
    "food_life": ("K-FOOD & LIFE", (234, 88, 12)),
    "travel": ("TRAVEL", (13, 148, 136)),
}


def category_badge(draw, x, y, key, size=30, anchor="left"):
    """Draws a rounded category pill; returns its right edge."""
    label, color = CATEGORIES[key]
    f = nr.font(size)
    tw = draw.textlength(label, font=f)
    h, pad = int(size * 1.7), int(size * 0.7)
    x0 = x if anchor == "left" else x - (tw + 2 * pad) / 2
    draw.rounded_rectangle((x0, y, x0 + tw + 2 * pad, y + h), h // 4, fill=color)
    draw.text((x0 + pad, y + h / 2), label, font=f, fill=nr.WHITE, anchor="lm")
    return x0 + tw + 2 * pad


class Puppet:
    def __init__(self, spec):
        head = nr.remove_bg(Image.open(spec["head"]))
        body = nr.remove_bg(Image.open(spec["body"]))
        rig = nr.analyze_head(head)
        ref = nr.remove_bg(Image.open(spec["ref"]))
        widths = nr.fg_widths(ref)
        # Measured from the reference sheet unless set per character (hair buns inflate the measurement).
        ratio = spec.get("head_ratio") or max(widths[: int(len(widths) * 0.4)]) / max(widths[-40:])
        shoulders = spec.get("shoulders", 520)
        sb = shoulders / max(nr.fg_widths(body)[-40:])
        self.body = body.resize((int(body.width * sb), int(body.height * sb)), Image.LANCZOS)
        sh = ratio * shoulders / head.width
        self.head = head.resize((int(head.width * sh), int(head.height * sh)), Image.LANCZOS)
        self.rig = {**rig, "eyes": [(x * sh, y * sh) for x, y in rig["eyes"]], "r": rig["r"] * sh,
                    "sep": rig["sep"] * sh, "mouth": (rig["mouth"][0] * sh, rig["mouth"][1] * sh),
                    "mouth_w": rig["mouth_w"] * sh, "chin": rig["chin"] * sh}
        self.x = spec["x"]
        self.label = spec["label"]
        self.energy = spec.get("energy", 1.0)
        alpha = np.asarray(self.body)[..., 3] > 0
        collar_top = int(np.nonzero(alpha.any(axis=1))[0].min())
        self.body_pos = (self.x - self.body.width // 2, COLLAR_Y - collar_top)
        self.pivot = (self.x, COLLAR_Y + int(0.03 * self.head.height))
        self.info = {"ratio": round(ratio, 3), "eyes": [tuple(round(v) for v in e) for e in rig["eyes"]]}

    def draw(self, frame, t, gaze, lid, env, nod):
        mouth = "closed" if env < 0.15 else ("mid" if env < 0.45 else "open")
        face = nr.face_layer(self.head, self.rig, gaze, lid, mouth)
        angle = (1.4 * math.sin(2 * math.pi * t / 3.9 + self.x) + 2.4 * self.energy * env
                 * math.sin(2 * math.pi * t * 1.2) + nod)
        angle += 2.5 * gaze[0] * -1  # lean toward where the eyes look
        cx, chin = face.width / 2, self.rig["chin"]
        canvas = Image.new("RGBA", (face.width * 2, face.height * 2), (0, 0, 0, 0))
        canvas.paste(face, (face.width // 2, face.height // 2))
        rot = canvas.rotate(angle, resample=Image.BICUBIC, center=(face.width // 2 + cx, face.height // 2 + chin))
        frame.paste(self.body, self.body_pos, self.body)
        hx = int(self.pivot[0] - (face.width // 2 + cx))
        hy = int(self.pivot[1] - (face.height // 2 + chin) - 8 * self.energy * env)
        frame.paste(rot, (hx, hy), rot)


def blink_schedule(duration, seed):
    rnd, t, out = random.Random(seed), rnd_start(seed), []
    while t < duration:
        out.append(t)
        t += rnd.uniform(2.2, 4.8)
    return out


def rnd_start(seed):
    return 0.8 + (seed % 7) * 0.23


def lid_at(t, blinks):
    for bt in blinks:
        k = (t - bt) * FPS
        if 0 <= k < 5:
            return [0.5, 1.0, 1.0, 0.6, 0.2][int(k)]
    return 0.0


def ease(a):
    return a * a * (3 - 2 * a)


def main():
    scene = json.load(open(sys.argv[1]))
    puppets = {k: Puppet(v) for k, v in scene["characters"].items()}

    # Timeline: lines back to back with a short gap; one combined audio track.
    gap = scene.get("gap", 0.3)
    parts, t, lines = [], 0.4, []
    silence = lambda s: np.zeros(int(16000 * s), np.float32)
    parts.append(silence(0.4))
    for ln in scene["lines"]:
        s = nr.load_audio(ln["audio"], 60)
        lines.append({**ln, "start": t, "end": t + len(s) / 16000, "samples": s})
        parts += [s, silence(gap)]
        t += len(s) / 16000 + gap
    audio = np.concatenate(parts + [silence(0.4)])
    duration = len(audio) / 16000
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", "16000", "-ac", "1", "-i", "-",
                    "dialog.wav"], input=audio.tobytes(), check=True)
    n = int(duration * FPS)

    envs = {k: np.zeros(n) for k in puppets}
    for ln in lines:
        i0 = int(ln["start"] * FPS)
        e = nr.envelope(ln["samples"], int(len(ln["samples"]) / 16000 * FPS))
        envs[ln["who"]][i0:i0 + len(e)] = e[: max(0, n - i0)]

    words = scene.get("words") or nr.transcribe("dialog.wav")
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or re.search(r"[.?!,…]$", w["w"]):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)

    # Static layers: studio without the explainer screen, one long desk, name tags, lower third.
    bg = nr.studio_background()
    desk = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(desk)
    d.polygon([(300, DESK_Y), (1620, DESK_Y), (1680, H), (240, H)], fill=(22, 26, 36))
    d.rectangle((300, DESK_Y, 1620, DESK_Y + 12), fill=nr.YELLOW)
    for p in puppets.values():
        f = nr.font(30)
        tw = d.textlength(p.label, font=f)
        d.rounded_rectangle((p.x - tw / 2 - 18, DESK_Y + 30, p.x + tw / 2 + 18, DESK_Y + 80), 10, fill=nr.YELLOW)
        d.text((p.x, DESK_Y + 55), p.label, font=f, fill=nr.BLACK, anchor="mm")
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o = ImageDraw.Draw(over)
    o.rounded_rectangle((270, 50, 420, 100), 12, fill=nr.RED)
    o.ellipse((288, 66, 306, 84), fill=nr.WHITE)
    o.text((316, 75), "LIVE", font=nr.font(30), fill=nr.WHITE, anchor="lm")
    o.rectangle((240, 930, 1680, 1030), fill=nr.WHITE)
    category = scene.get("category", "hidden_korea")
    cat_color = CATEGORIES[category][1]
    category_badge(o, 436, 50, category)  # next to LIVE, same height
    o.rectangle((240, 930, 520, 1030), fill=cat_color)
    o.text((380, 980), "PANEL", font=nr.font(40), fill=nr.WHITE, anchor="mm")
    o.text((550, 980), scene["headline"], font=nr.font(38), fill=nr.BLACK, anchor="lm")

    short_static = Image.new("RGB", (SW, SH), nr.BRAND_NAVY)
    sd = ImageDraw.Draw(short_static)
    category_badge(sd, SW / 2, 130, category, size=36, anchor="center")
    sd.multiline_text((SW / 2, 370), scene["hook"], font=nr.font(72), fill=nr.WHITE, anchor="mm",
                      align="center", spacing=18)
    nr.shorts_promo(short_static, sd)

    blinks = {k: blink_schedule(duration, i * 11 + 3) for i, k in enumerate(puppets)}
    rnd = random.Random(5)
    sacc = {k: {} for k in puppets}
    for k in puppets:
        t = 0
        while t < duration:
            sacc[k][int(t * FPS)] = (rnd.uniform(-0.2, 0.2), rnd.uniform(-0.15, 0.15))
            t += rnd.uniform(0.7, 1.9)

    def speaker_at(t):
        for ln in lines:
            if ln["start"] - 0.1 <= t <= ln["end"] + 0.15:
                return ln
        return None

    # Camera: wide for the first line, then a push-in on whoever speaks.
    def cam_target(t):
        ln = speaker_at(t)
        if ln is None or ln is lines[0]:
            return (W / 2, H / 2, 1.0)
        p = puppets[ln["who"]]
        return (p.x, 470, 1.32)

    cam = list(cam_target(0))

    def ff(path, w, h):
        return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                                 "-r", str(FPS), "-i", "-", "-i", "dialog.wav", "-c:v", "libx264", "-preset",
                                 "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", path],
                                stdin=subprocess.PIPE)

    lp, sp = ff(scene["out_long"], W, H), ff(scene["out_short"], SW, SH)
    base_gaze = {k: (0.0, 0.0) for k in puppets}
    for i in range(n):
        t = i / FPS
        ln = speaker_at(t)
        frame = bg.copy()
        for k, p in puppets.items():
            if i in sacc[k]:
                base_gaze[k] = sacc[k][i]
            g, nod = base_gaze[k], 0.0
            if ln is not None and ln["who"] != k:
                other = puppets[ln["who"]]
                g = (0.85 if other.x > p.x else -0.85, 0.05)  # look at the speaker
                since = t - ln["start"]
                nod = 2.5 * math.sin(min(since, 0.6) / 0.6 * math.pi) if since < 0.6 else 0.0
            elif ln is not None and t - ln["start"] < 0.5 and ln is not lines[0]:
                other = next(q for q in puppets.values() if q is not p)
                g = (0.7 if other.x > p.x else -0.7, 0.0)  # glance at the partner, then the camera
            p.draw(frame, t, g, lid_at(t, blinks[k]), envs[k][i], nod)
        frame.paste(desk, (0, 0), desk)

        tx, ty, tz = cam_target(t)
        a = 0.18  # smoothing per frame ~ 0.3s ease
        cam = [cam[0] + (tx - cam[0]) * a, cam[1] + (ty - cam[1]) * a, cam[2] + (tz - cam[2]) * a]
        cw, ch = W / cam[2], H / cam[2]
        cx = min(max(cam[0], cw / 2), W - cw / 2)
        cy = min(max(cam[1], ch / 2), H - ch / 2)
        view = frame.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize(
            (W, H), Image.BICUBIC) if cam[2] > 1.001 else frame.copy()
        view.paste(over, (0, 0), over)  # broadcast graphics stay fixed while the camera moves
        lp.stdin.write(np.asarray(view).tobytes())

        crop = view.crop((240, 0, 1680, 1080)).resize((1080, 810), Image.BILINEAR)
        sframe = short_static.copy()
        sframe.paste(crop, (0, 600))
        grp = next((g for g in groups if g[0]["s"] <= t <= g[-1]["e"] + 0.15), None)
        if grp:
            nr.draw_caption(sframe, grp, t)
        sp.stdin.write(np.asarray(sframe).tobytes())

    for p in (lp, sp):
        p.stdin.close()
        p.wait()
    print(json.dumps({"duration": round(duration, 2), "lines": [(l["who"], round(l["start"], 2), round(l["end"], 2))
                                                                   for l in lines],
                      "puppets": {k: p.info for k, p in puppets.items()}}))


if __name__ == "__main__":
    main()
