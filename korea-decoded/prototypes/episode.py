"""One news segment with automatic shot planning: anchor solo, anchor + explainer screen, full screen,
panel two-shot, speaker close-up and wide, like a real news control room.

usage: python3 episode.py segment.json

Every line gets a shot from simple rules (plan_shots); a line can force one with "shot": "<name>".
Shots that only show the anchor are a different camera, so switching between the anchor camera and
the desk camera is a cut; moves within one camera ease.
Reuses the puppets from dialog.py and the drawing helpers from newsrig.py (same folder).
"""
import json
import math
import random
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

import dialog as dg
import newsrig as nr

W, H, FPS, SW, SH = nr.W, nr.H, nr.FPS, nr.SW, nr.SH
WORLD_W = 2400  # studio wider than the frame so a centered close-up of the anchor stays inside it
OX = (WORLD_W - W) // 2  # scene x (0..1920) -> world x
DESK_Y = dg.DESK_Y

SHOTS = ("anchor_solo", "anchor_screen", "screen_full", "two_shot", "speaker_close", "wide")
ANCHOR_CAMERA = {"anchor_solo", "anchor_screen", "screen_full"}  # the panel is not in this camera's view
SCREEN_OTS = (300, 250, 1060, 678)  # explainer box beside the anchor (view coords, 16:9)
SCREEN_FULL = (300, 130, 1620, 873)  # big, below the top tags, above the lower third, inside the Shorts crop


def plan_shots(lines, anchor="anchor"):
    """Picks a shot per line. Rules: open on the anchor alone; news lines with a visual get the
    explainer screen (a "big" visual goes full screen); a panel's first line is a two-shot that brings
    them in; after that the camera pushes in on whoever speaks."""
    shots, seen = [], set()
    for i, ln in enumerate(lines):
        who = ln["who"]
        if ln.get("shot"):
            shot = ln["shot"]
        elif who == anchor and ln.get("screen"):
            shot = "screen_full" if ln.get("big") else "anchor_screen"
        elif who == anchor:
            talking_to_panel = i > 0 and lines[i - 1]["who"] != anchor
            shot = "speaker_close" if talking_to_panel else "anchor_solo"
        elif who not in seen:
            shot = "two_shot"
        else:
            shot = "speaker_close"
        if shot not in SHOTS:
            raise ValueError(f"line {i}: unknown shot {shot!r}")
        seen.add(who)
        shots.append(shot)
    return shots


def world_background():
    bg = Image.new("RGB", (WORLD_W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line((0, y, WORLD_W, y), fill=tuple(int(a + (b - a) * t) for a, b in zip(nr.NAVY, nr.NAVY2)))
    for x in range(0, WORLD_W, 120):
        d.line((x, 0, x, 780), fill=(40, 58, 100), width=1)
    for y in range(60, 780, 120):
        d.line((0, y, WORLD_W, y), fill=(40, 58, 100), width=1)
    return bg


def desk_layer(puppets):
    img = Image.new("RGBA", (WORLD_W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(OX + 300, DESK_Y), (OX + 1620, DESK_Y), (OX + 1680, H), (OX + 240, H)], fill=(22, 26, 36))
    d.rectangle((OX + 300, DESK_Y, OX + 1620, DESK_Y + 12), fill=nr.YELLOW)
    f = nr.font(30)
    for p in puppets:
        tw = d.textlength(p.label, font=f)
        x = p.x + OX
        d.rounded_rectangle((x - tw / 2 - 18, DESK_Y + 30, x + tw / 2 + 18, DESK_Y + 80), 10, fill=nr.YELLOW)
        d.text((x, DESK_Y + 55), p.label, font=f, fill=nr.BLACK, anchor="mm")
    return img


def fit_cover(img, w, h):
    s = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * s) + 1, int(img.height * s) + 1), Image.LANCZOS)
    l, t = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((l, t, l + w, t + h))


def screen_layer(img, rect, alpha, label, credit):
    """Explainer box (white frame, label bar, credit line) drawn at rect with global alpha."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if alpha < 0.02:
        return layer
    x0, y0, x1, y1 = (int(round(v)) for v in rect)
    d = ImageDraw.Draw(layer)
    d.rectangle((x0 - 8, y0 - 8, x1 + 8, y1 + 8), fill=nr.WHITE)
    layer.paste(fit_cover(img, x1 - x0, y1 - y0).convert("RGBA"), (x0, y0))
    if label and y0 > 200:  # the label bar would cover the top tags when the box is full size
        f = nr.font(28)
        d.rectangle((x0 - 8, y0 - 52, x0 + d.textlength(label, font=f) + 30, y0 - 8), fill=nr.YELLOW)
        d.text((x0 + 10, y0 - 30), label, font=f, fill=nr.BLACK, anchor="lm")
    if credit:
        d.text((x0, y1 + 30), credit, font=nr.font(22), fill=(190, 200, 225), anchor="lm")
    if alpha < 0.999:
        a = np.asarray(layer).copy()
        a[..., 3] = (a[..., 3] * alpha).astype(np.uint8)
        layer = Image.fromarray(a)
    return layer


def broadcast_overlay(scene):
    """Graphics that stay fixed while the camera moves and also show in the Shorts crop."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    category = scene.get("category", "hidden_korea")
    label, color = dg.CATEGORIES[category]
    right = nr.episode_tag(d, 270, 50, scene.get("episode", 1))
    dg.category_badge(d, right + 16, 50, category)
    d.rectangle((240, 930, 1680, 1030), fill=nr.WHITE)
    d.rectangle((240, 930, 520, 1030), fill=color)
    topic = scene.get("topic")
    if topic:
        d.text((380, 965), f"TOPIC {topic[0]}/{topic[1]}", font=nr.font(34), fill=nr.WHITE, anchor="mm")
        d.text((380, 1003), scene.get("desk", label.split(" ")[0]), font=nr.font(24), fill=nr.WHITE, anchor="mm")
    f = nr.font(40)
    while d.textlength(scene["headline"], font=f) > 1100:
        f = nr.font(f.size - 2)
    d.text((550, 980), scene["headline"], font=f, fill=nr.BLACK, anchor="lm")
    return img


def bands(layer):
    """Splits a mostly transparent full-frame layer into (piece, (x, y)) row bands, so pasting it
    each frame only touches the pixels that have graphics."""
    alpha = np.asarray(layer)[..., 3] > 0
    rows = np.nonzero(alpha.any(axis=1))[0]
    out, start = [], None
    for k, y in enumerate(rows):
        if start is None:
            start = y
        if k == len(rows) - 1 or rows[k + 1] != y + 1:
            cols = np.nonzero(alpha[start:y + 1].any(axis=0))[0]
            box = (int(cols.min()), int(start), int(cols.max()) + 1, int(y) + 1)
            out.append((layer.crop(box), box[:2]))
            start = None
    return out


def paste_bands(img, pieces):
    for piece, xy in pieces:
        img.paste(piece, xy, piece)


def ticker_strip(items):
    """Pre-rendered UP NEXT text, repeated back to back for a seamless loop."""
    f = nr.font(24)
    text = "   |   ".join(items) + "   |   "
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = int(probe.textlength(text, font=f))
    copies = W // tw + 2  # enough repeats that any window of width W is covered
    strip = Image.new("RGB", (tw * copies, 40), nr.BRAND_NAVY)
    d = ImageDraw.Draw(strip)
    for k in range(copies):
        d.text((k * tw, 20), text, font=f, fill=nr.WHITE, anchor="lm")
    return strip, tw


def main():
    scene = json.load(open(sys.argv[1]))
    puppets = {k: dg.Puppet(v) for k, v in scene["characters"].items()}
    anchor_key = scene.get("anchor", "anchor")
    screens = {k: {**v, "img": Image.open(v["image"]).convert("RGB")} for k, v in scene.get("screens", {}).items()}

    # Timeline: lines back to back with a short gap, one audio track.
    gap = scene.get("gap", 0.35)
    silence = lambda s: np.zeros(int(16000 * s), np.float32)
    parts, t, lines = [silence(0.5)], 0.5, []
    for ln in scene["lines"]:
        s = nr.load_audio(ln["audio"], 60)
        lines.append({**ln, "start": t, "end": t + len(s) / 16000, "samples": s})
        parts += [s, silence(gap)]
        t += len(s) / 16000 + gap
    audio = np.concatenate(parts + [silence(0.6)])
    duration = len(audio) / 16000
    wav = scene["out_long"].rsplit(".", 1)[0] + ".wav"  # one per segment, so segments can render side by side
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", "16000", "-ac", "1", "-i", "-",
                    wav], input=audio.tobytes(), check=True)
    n = int(duration * FPS)

    shots = plan_shots(lines, anchor_key)
    for ln, shot in zip(lines, shots):
        ln["shot"] = shot

    envs = {k: np.zeros(n) for k in puppets}
    for ln in lines:
        i0 = int(ln["start"] * FPS)
        e = nr.envelope(ln["samples"], int(len(ln["samples"]) / 16000 * FPS))
        envs[ln["who"]][i0:i0 + len(e)] = e[: max(0, n - i0)]

    words = scene.get("words") or nr.transcribe(wav)
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or re.search(r"[.?!,…]$", w["w"]):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)

    bg = world_background()
    desks = {"all": bands(desk_layer(puppets.values())), "anchor": bands(desk_layer([puppets[anchor_key]]))}
    over = bands(broadcast_overlay(scene))
    ticker, ticker_w = ticker_strip(scene.get("up_next", ["More stories after this"]))
    bug = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nr.logo_mark(bug, 1800, 78, 76)  # long form only: sits outside the Shorts crop
    bd = ImageDraw.Draw(bug)
    bd.rectangle((0, 1040, 190, 1080), fill=nr.YELLOW)
    bd.text((95, 1060), "UP NEXT", font=nr.font(24), fill=nr.NAVY, anchor="mm")
    bug = bands(bug)

    # Shorts: the whole segment, or only the lines in "short": {"from": i, "to": j}; false for none
    short_spec = scene.get("short", {})
    if short_spec is False:
        s_from = s_to = None
    else:
        a_line = lines[short_spec.get("from", 0)]
        b_line = lines[short_spec.get("to", len(lines) - 1)]
        s_from, s_to = max(0.0, a_line["start"] - 0.4), min(duration, b_line["end"] + 0.6)

    short_static = Image.new("RGB", (SW, SH), nr.BRAND_NAVY)
    sd = ImageDraw.Draw(short_static)
    sd.multiline_text((SW / 2, 300), scene["hook"], font=nr.font(72), fill=nr.WHITE, anchor="mm",
                      align="center", spacing=18)
    nr.shorts_promo(short_static, sd)

    blinks = {k: dg.blink_schedule(duration, i * 11 + 3) for i, k in enumerate(puppets)}
    rnd = random.Random(5)
    sacc = {k: {} for k in puppets}
    for k in puppets:
        tt = 0
        while tt < duration:
            sacc[k][int(tt * FPS)] = (rnd.uniform(-0.2, 0.2), rnd.uniform(-0.15, 0.15))
            tt += rnd.uniform(0.7, 1.9)

    def line_at(t):
        """The line whose shot is on screen at t (shots switch just before each line starts)."""
        cur = lines[0]
        for ln in lines:
            if t >= ln["start"] - 0.15:
                cur = ln
        return cur

    def speaking(t):
        return next((ln for ln in lines if ln["start"] - 0.1 <= t <= ln["end"] + 0.15), None)

    ax = puppets[anchor_key].x + OX

    def cam_target(ln, t):
        shot, p = ln["shot"], puppets[ln["who"]]
        if shot == "anchor_solo":
            target = [ax, 480, 1.25]
        elif shot in ("anchor_screen", "screen_full"):
            z = 1.05
            target = [ax - 370 / z, 540, z]
        elif shot == "two_shot":
            others = [q.x + OX for k, q in puppets.items()]
            target = [(min(others) + max(others)) / 2, 520, 1.1]
        elif shot == "speaker_close":
            target = [p.x + OX, 470, 1.32]
        else:  # wide
            target = [WORLD_W / 2, 540, 1.0]
        held = t - (ln["start"] - 0.15)
        if held > 4 and shot != "screen_full":  # slow push so a long shot doesn't sit still
            target[2] += min(0.06, 0.015 * (held - 4))
        return target

    def ff(path, w, h, start=0.0):
        return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                                 "-r", str(FPS), "-i", "-", "-ss", f"{start:.3f}", "-i", wav, "-c:v", "libx264",
                                 "-preset", "superfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac",
                                 "-ar", "48000", "-shortest", path], stdin=subprocess.PIPE)

    lp = ff(scene["out_long"], W, H)
    sp = ff(scene["out_short"], SW, SH, s_from) if s_from is not None else None
    box_cache = {}
    cam = cam_target(lines[0], 0)
    rect, alpha = list(SCREEN_OTS), 0.0
    shown_screen, prev_line = None, None
    base_gaze = {k: (0.0, 0.0) for k in puppets}
    for i in range(n):
        t = i / FPS
        ln = line_at(t)
        spk = speaking(t)
        anchor_cam = ln["shot"] in ANCHOR_CAMERA
        visible = [anchor_key] if anchor_cam else list(puppets)

        # camera: cut when switching between the anchor camera and the desk camera, otherwise ease
        tx, ty, tz = cam_target(ln, t)
        if prev_line is not None and ln is not prev_line and (prev_line["shot"] in ANCHOR_CAMERA) != anchor_cam:
            cam = [tx, ty, tz]
        a = 0.14
        cam = [cam[0] + (tx - cam[0]) * a, cam[1] + (ty - cam[1]) * a, cam[2] + (tz - cam[2]) * a]
        prev_line = ln

        # explainer screen: slides between beside-anchor and full frame, fades when not used
        if ln.get("screen") and ln["shot"] in ("anchor_screen", "screen_full"):
            shown_screen = screens[ln["screen"]]
            goal, goal_a = (SCREEN_FULL if ln["shot"] == "screen_full" else SCREEN_OTS), 1.0
        else:
            goal, goal_a = rect, 0.0
        rect = [r + (g - r) * 0.2 for r, g in zip(rect, goal)]
        alpha += (goal_a - alpha) * (0.3 if goal_a else 0.5)
        if not anchor_cam:
            alpha = 0.0  # a camera cut takes the box with it

        world = bg.copy()
        for k in visible:
            p = puppets[k]
            if i in sacc[k]:
                base_gaze[k] = sacc[k][i]
            g, nod = base_gaze[k], 0.0
            if spk is not None and spk["who"] != k and spk["who"] in visible:
                other = puppets[spk["who"]]
                g = (0.85 if other.x > p.x else -0.85, 0.05)  # listeners look at the speaker
                since = t - spk["start"]
                nod = 2.5 * math.sin(since / 0.6 * math.pi) if since < 0.6 else 0.0
            elif k == anchor_key and ln["shot"] in ("anchor_screen", "screen_full") and t - ln["start"] < 0.7:
                g = (-0.8, 0.1)  # glance at the screen, then back to camera
            p.draw(world, t, g, dg.lid_at(t, blinks[k]), envs[k][i], nod, ox=OX)
        paste_bands(world, desks["anchor" if anchor_cam else "all"])

        cw, ch = W / cam[2], H / cam[2]
        cx = min(max(cam[0], cw / 2), WORLD_W - cw / 2)
        cy = min(max(cam[1], ch / 2), H - ch / 2)
        view = world.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize(
            (W, H), Image.BILINEAR)
        if shown_screen is not None and alpha > 0.02:
            key = (id(shown_screen), tuple(round(v) for v in rect), round(alpha, 2))
            if key not in box_cache:  # the box only changes while it slides or fades
                box_cache.clear()
                box_cache[key] = bands(screen_layer(shown_screen["img"], rect, alpha, shown_screen.get("label", ""),
                                                    shown_screen.get("credit", "")))
            paste_bands(view, box_cache[key])
        paste_bands(view, over)

        if sp is not None and s_from <= t <= s_to:
            crop = view.crop((240, 0, 1680, 1080)).resize((1080, 810), Image.BILINEAR)
            sframe = short_static.copy()
            sframe.paste(crop, (0, 600))
            grp = next((g for g in groups if g[0]["s"] <= t <= g[-1]["e"] + 0.15), None)
            if grp:
                nr.draw_caption(sframe, grp, t)
            sp.stdin.write(np.asarray(sframe).tobytes())

        off = int(t * 110) % ticker_w
        view.paste(ticker.crop((off, 0, off + W - 190, 40)), (190, 1040))
        paste_bands(view, bug)
        lp.stdin.write(np.asarray(view).tobytes())

    for p in (lp, sp):
        if p is not None:
            p.stdin.close()
            p.wait()
    print(json.dumps({"duration": round(duration, 2),
                      "shots": [(l["who"], l["shot"], round(l["start"], 2)) for l in lines]}))


if __name__ == "__main__":
    main()
