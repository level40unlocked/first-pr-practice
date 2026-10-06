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
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import charts
import dialog as dg
import newsrig as nr

W, H, FPS, SW, SH = nr.W, nr.H, nr.FPS, nr.SW, nr.SH
WORLD_W = 5300  # studio wider than the frame: room for a panel seat far left and a guest seat far right, so a close-up never catches the neighbour
OX = (WORLD_W - W) // 2  # scene x (0..1920) -> world x
DESK_Y = dg.DESK_Y

SHOTS = ("anchor_solo", "anchor_screen", "screen_full", "two_shot", "speaker_close", "wide", "still", "cam", "k_screen", "host_screen")
# "k_screen": the anchor on the left and the explainer screen on the right, nobody else in frame (the camera is
# zoomed in and starts right of the panel seat). Used when the anchor presents a picture.
# "cam": the line names its own camera, "cam": [x, y, zoom] in scene coordinates (x 0..1920, y ~470, zoom >= 1),
# and optionally "ease" (share of the way the camera moves per frame; low = a slow pan, 0.3 = a snap).
# "still": the line plays over a picture from scene["still"] (e.g. the whole cast), slowly pushing in; the
# Short shows it whole (fit to width) instead of cropped. A line's "tags" pop name labels onto it.
ANCHOR_CAMERA = {"anchor_solo"}  # the anchor close-up; every other shot keeps the whole desk in view
SCREEN_SHOTS = ("anchor_screen", "screen_full", "k_screen", "host_screen")
# "host_screen": the leftmost two people (the hosts) both stay in frame and the small box goes to ONE side of them, never over anybody:
# line["side"] = "right" (hosts on the left) or "left" (hosts on the right). The side is kept for a whole run of lines with the same
# picture, so a change of speaker is a plain change of who talks: no cut, no moving box. A line may also set "box": "small" on a k_screen line
# (the guest in close-up) so the box stays at the same place when the camera cuts to or from the guest.
SCREEN_LEFT = (50, 230, 740, 618)  # the small box on the left
SCREEN_OTS = (1190, 230, 1880, 618)  # explainer box to the anchor's right (view coords, 16:9), the panel stays
ANCHOR_VIEW_X = 930  # where the anchor sits in the view during screen shots
SHORT_W = 1440  # a Short shows this much of the 1920-wide view
SHORT_X = {"anchor_screen": 480}  # left edge of the Short's crop per shot (anchor + side screen); else centered
SCREEN_K = (880, 210, 1840, 750)  # explainer box for "k_screen" (960 x 540)
SCREEN_FULL = (300, 128, 1620, 885)  # big, below the top tags, above the lower third, inside the Shorts crop;
# the bottom edge also hides the nameplates on the desk


def plan_shots(lines, anchor="anchor"):
    """Picks a shot per line. Rules: open on the whole desk when anyone else is on it (so nobody pops in
    later), otherwise on the anchor alone; news lines with a visual get the explainer screen to the
    anchor's right with the panel still at the desk (a "big" visual goes full screen); a panel's first
    line is a two-shot that brings them in; after that the camera pushes in on whoever speaks."""
    shots, seen = [], set()
    has_guests = any(ln["who"] != anchor for ln in lines)
    for i, ln in enumerate(lines):
        who = ln["who"]
        if ln.get("shot"):
            shot = ln["shot"]
        elif who == anchor and ln.get("screen"):
            shot = "screen_full" if ln.get("big") else "anchor_screen"
        elif ln.get("screen"):  # a panel line over a visual: the voice plays over the full screen
            shot = "screen_full"
        elif i == 0 and who == anchor and has_guests:
            shot = "wide"
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


def studio_backdrop(path, dim=0.8, blur=1.5, top=0.0):
    """A studio picture (e.g. a skyline window) as the set wall: fills the world width, shifted up by
    `top` (share of the spare height), softened and dimmed so the hosts and screens stay in front."""
    img = Image.open(path).convert("RGB")
    s = max(WORLD_W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0 = (img.width - WORLD_W) // 2
    y0 = int((img.height - H) * top)
    img = img.crop((x0, y0, x0 + WORLD_W, y0 + H))
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    return ImageEnhance.Brightness(img).enhance(dim)


def world_background(scene=None):
    spec = (scene or {}).get("background")
    if spec:
        spec = {"image": spec} if isinstance(spec, str) else spec
        return studio_backdrop(spec["image"], spec.get("dim", 0.8), spec.get("blur", 1.5), spec.get("top", 0.0))
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


def desk_layer(puppets, nameplates=True):
    img = Image.new("RGBA", (WORLD_W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    xs = [p.x for p in puppets]
    left, right = min([300] + [x - 300 for x in xs]), max([1620] + [x + 300 for x in xs])  # wider for a third seat
    d.polygon([(OX + left, DESK_Y), (OX + right, DESK_Y), (OX + right + 60, H), (OX + left - 60, H)], fill=(22, 26, 36))
    d.rectangle((OX + left, DESK_Y, OX + right, DESK_Y + 12), fill=nr.YELLOW)
    f = nr.font(30)
    for p in puppets if nameplates else []:  # with "name_chips" the names are drawn above the lower third instead
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


KB_SECONDS = 7.0  # Ken Burns: how long a slow push/pan takes to reach its end point
FADE = 0.3  # crossfade between screens inside one line


END_CARD = 2.5  # seconds a Short holds its "full episode on the channel" card after the last line


def end_card(last, t, where="on our channel", card=None):
    """The Short's closing card over its frozen last frame; fades in over 0.35 s. `where` names the place of
    the full episode ("on YouTube" when the clip is posted on another platform). `card` = {"title", "line"}
    replaces the two texts (the channel intro says FOLLOW FOR MORE instead)."""
    title, line = (card["title"], card["line"]) if card else ("WANT THE FULL STORY?", f"Full episode {where}")
    u = ease(min(1.0, t / 0.35))
    frame = Image.blend(last, Image.new("RGB", last.size, nr.BRAND_NAVY), 0.6 * u)
    card = Image.new("RGBA", last.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rectangle((0, 600, SW, 1410), fill=nr.BRAND_NAVY)  # hide the frozen caption and screen behind the text
    cx = SW / 2
    d.text((cx, 760), title, font=nr.font(64), fill=nr.YELLOW, anchor="mm")
    d.text((cx, 870), line, font=nr.font(50 if len(line) < 34 else 40), fill=nr.WHITE, anchor="mm")
    d.rounded_rectangle((cx - 330, 950, cx + 330, 1050), 50, fill=nr.YELLOW)
    d.text((cx, 1000), nr.HANDLE, font=nr.font(48), fill=nr.NAVY, anchor="mm")
    card.putalpha(card.getchannel("A").point(lambda a: int(a * u)))
    frame.paste(card, (0, 0), card)
    return frame


OUT_SR = 48000  # soundtrack sample rate (YouTube's native rate)


def load_audio_hq(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-t", "60", "-ac", "1", "-ar", str(OUT_SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def prepare_screen(key, spec):
    """Loads one screen: a picture (with baked-in text overlays) or a number card."""
    out = {**spec, "key": key}
    if "card" in spec or "chart" in spec:
        return out
    img = Image.open(spec["image"]).convert("RGB")
    img = fit_cover(img, 1650, 929)  # a bit bigger than the full-size box, room for the slow push
    if spec.get("overlays"):
        d = ImageDraw.Draw(img)
        for o in spec["overlays"]:
            d.text((o["x"] * img.width, o["y"] * img.height), o["text"], font=nr.font(o.get("size", 44)),
                   fill=o.get("color", nr.WHITE), anchor=o.get("anchor", "mm"),
                   stroke_width=o.get("stroke", 6), stroke_fill=o.get("stroke_color", nr.NAVY))
    out["img"] = img
    # direction of the slow move: explicit, or picked from the key so neighbours differ
    moves = ("in", "out", "left", "right")
    out["kb"] = spec.get("kb", moves[sum(map(ord, key)) % 4])
    return out


def ken_burns(src, w, h, u, move):
    """Crop of src for progress u (0..1): push in, pull out, or pan, then scaled to w x h."""
    u = ease(u)
    sw, sh = src.size
    if move == "in":
        z, fx = 1.0 + 0.14 * u, 0.5
    elif move == "out":
        z, fx = 1.14 - 0.14 * u, 0.5
    elif move == "left":
        z, fx = 1.12, 0.62 - 0.24 * u
    else:
        z, fx = 1.12, 0.38 + 0.24 * u
    cw = min(sw, sh * w / h) / z
    ch = min(sh, cw * h / w)  # never taller than the picture (an odd box shape mid-slide used to push y0 below 0)
    x0 = max(0.0, (sw - cw) * fx)
    y0 = max(0.0, (sh - ch) * 0.5)
    return src.resize((w, h), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def fmt_number(v, st):
    dec = st.get("decimals", 0)
    txt = f"{v:,.{dec}f}"
    return f"{st.get('prefix', '')}{txt}{st.get('suffix', '')}"


def card_image(card, w, h, t):
    """Number card on the brand navy: title, then stats that count up one after another."""
    img = Image.new("RGB", (w, h), nr.BRAND_NAVY)
    d = ImageDraw.Draw(img)
    s = max(w / 1320, 0.78)  # layout was designed at full-screen size; the small box beside the hosts keeps readable text
    if card.get("title"):
        d.text((w / 2, 70 * s), card["title"], font=nr.font(int(40 * s)), fill=nr.YELLOW, anchor="mm")
    stats = card["stats"]
    top, bottom = (140 if card.get("title") else 60) * s, h - 50 * s
    row = (bottom - top) / len(stats)
    for k, st in enumerate(stats):
        u = ease((t - 0.25 - 0.45 * k) / 1.1)
        if u <= 0:
            continue
        cy = top + row * (k + 0.5)
        big = int(min(row * 0.55, 150 * s))
        value = st["value"] * u if isinstance(st["value"], (int, float)) else st["value"]
        text = fmt_number(value, st) if isinstance(value, (int, float)) else value
        d.text((w / 2, cy - row * 0.12), text, font=nr.font(big), fill=nr.WHITE, anchor="mm")
        if st.get("label"):
            d.text((w / 2, cy + big * 0.55), st["label"], font=nr.font(int(34 * s)), fill=(190, 200, 225),
                   anchor="mm")
    return img


def screen_content(scr, w, h, t_local):
    if "chart" in scr:
        return charts.draw(scr["chart"], w, h, t_local)
    if "card" in scr:
        return card_image(scr["card"], w, h, t_local)
    return ken_burns(scr["img"], w, h, t_local / KB_SECONDS, scr["kb"])


def screen_piece(content, rect, alpha, label, credit):
    """Explainer box (white frame, label bar, credit line) as one RGBA piece and its position."""
    x0, y0, x1, y1 = (int(round(v)) for v in rect)
    w, h = x1 - x0, y1 - y0
    top = 60 if (label and y0 > 200) else 8  # the label bar would cover the top tags when full size
    piece = Image.new("RGBA", (w + 16 + 400, h + 16 + top - 8 + 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(piece)
    ox, oy = 8, top
    d.rectangle((0, oy - 8, w + 16, oy + h + 8), fill=nr.WHITE)
    piece.paste(content.resize((w, h), Image.BILINEAR) if content.size != (w, h) else content, (ox, oy))
    if top > 8:
        f = nr.font(28)
        d.rectangle((0, 0, d.textlength(label, font=f) + 38, 44), fill=nr.YELLOW)
        d.text((18, 22), label, font=f, fill=nr.BLACK, anchor="lm")
    if credit:
        d.text((ox, oy + h + 30), credit, font=nr.font(22), fill=(190, 200, 225), anchor="lm")
    if alpha < 0.999:
        a = np.asarray(piece).copy()
        a[..., 3] = (a[..., 3] * alpha).astype(np.uint8)
        piece = Image.fromarray(a)
    return piece, (x0 - 8, y0 - top)


def box_goal(ln):
    if ln["shot"] == "screen_full":
        return SCREEN_FULL
    if ln["shot"] == "host_screen":
        return SCREEN_OTS if ln.get("side", "right") == "right" else SCREEN_LEFT
    if ln.get("box") == "small":
        return SCREEN_OTS
    return SCREEN_K if ln["shot"] == "k_screen" else SCREEN_OTS


def one_key(ln):
    k = ln.get("screen")
    if isinstance(k, list):
        return k[0] if len(k) == 1 else None
    return k


def screen_at(ln, t):
    """(current screen key, seconds it has been up, previous key, crossfade progress) inside one line.
    A line's "screen" is one key or a list; "screen_split" gives the switch points as fractions."""
    keys = ln["screen"] if isinstance(ln["screen"], list) else [ln["screen"]]
    span = max(ln["end"] - ln["start"], 0.1)
    cuts = ln.get("screen_split") or [k / len(keys) for k in range(1, len(keys))]
    base = ln.get("_run", ln["start"]) if len(keys) == 1 else ln["start"]  # one picture over several lines keeps running
    starts = [base - 0.15] + [ln["start"] + c * span for c in cuts]
    k = max(i for i, s0 in enumerate(starts) if t >= s0 or i == 0)
    since = t - starts[k]
    prev = keys[k - 1] if k > 0 and since < FADE else None
    return keys[k], since, prev, since / FADE


TAG_X_LONG = 80  # EP/category tag at the long form's left edge, mirroring the logo on the right
TAG_X_SHORT = (W - SHORT_W) // 2 + 30  # inside the Short's crop


def broadcast_overlay(scene, tag_x=TAG_X_LONG):
    """Graphics that stay fixed while the camera moves; the Short gets its own copy with the tag
    moved inside its crop."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    category = scene.get("category", "hidden_korea")
    label, color = dg.CATEGORIES[category]
    right = nr.episode_tag(d, tag_x, 50, scene.get("episode", 1))
    dg.category_badge(d, right + 16, 50, category)
    d.rectangle((240, 930, 1680, 1030), fill=nr.WHITE)
    d.rectangle((240, 930, 520, 1030), fill=color)
    topic = scene.get("topic")
    if topic:
        d.text((380, 965), f"TOPIC {topic[0]}/{topic[1]}", font=nr.font(34), fill=nr.WHITE, anchor="mm")
        d.text((380, 1003), scene.get("desk", label.split(" ")[0]), font=nr.font(24), fill=nr.WHITE, anchor="mm")
    else:  # a stand-alone clip has no topic count: the desk name alone fills the colored chip
        d.text((380, 980), scene.get("desk", label.split(" ")[0]), font=nr.font(30), fill=nr.WHITE, anchor="mm")
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


def estimate_words(lines):
    """Caption timing. A line with "words" (recognized timings, seconds from the line's start, as
    [word, start, end]) uses them; otherwise its script words are spread over its audio by length."""
    words = []
    for ln in lines:
        if ln.get("words"):
            words += [{"w": w, "s": ln["start"] + s0, "e": ln["start"] + e0} for w, s0, e0 in ln["words"]]
            continue
        toks = ln["text"].split()
        if not toks:
            continue
        span = ln["end"] - ln["start"]
        weights = [len(w) + 2 for w in toks]
        total, acc = sum(weights), 0
        for w, wt in zip(toks, weights):
            s0 = ln["start"] + span * acc / total
            acc += wt
            words.append({"w": w, "s": s0, "e": ln["start"] + span * acc / total})
    return words


def main():
    scene = json.load(open(sys.argv[1]))
    puppets = {k: dg.Puppet(v) for k, v in scene["characters"].items()}
    anchor_key = scene.get("anchor", "anchor")
    screens = {k: prepare_screen(k, v) for k, v in scene.get("screens", {}).items()}

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
    # The 16 kHz copy above only drives timing and mouth shapes; the soundtrack keeps full quality.
    track = np.zeros(int(duration * OUT_SR) + OUT_SR, np.float32)
    for ln in lines:
        s = load_audio_hq(ln["audio"])
        i0 = int(round(ln["start"] * OUT_SR))
        track[i0:i0 + len(s)] += s[:len(track) - i0]
    wav = scene["out_long"].rsplit(".", 1)[0] + ".wav"  # one per segment, so segments can render side by side
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(OUT_SR), "-ac", "1", "-i", "-",
                    wav], input=track[:int(duration * OUT_SR)].tobytes(), check=True)
    n = int(duration * FPS)

    shots = plan_shots(lines, anchor_key)
    for ln, shot in zip(lines, shots):
        ln["shot"] = shot

    envs = {k: np.zeros(n) for k in puppets}
    for ln in lines:
        i0 = int(ln["start"] * FPS)
        e = nr.envelope(ln["samples"], int(len(ln["samples"]) / 16000 * FPS))
        envs[ln["who"]][i0:i0 + len(e)] = e[: max(0, n - i0)]

    words = scene.get("words") or estimate_words(lines)
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or re.search(r"[.?!,…]$", w["w"]):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)

    bg = world_background(scene)
    chips_on = bool(scene.get("name_chips"))
    desks = {"all": bands(desk_layer(puppets.values(), not chips_on)),
             "anchor": bands(desk_layer([puppets[anchor_key]], not chips_on))}
    chip_font = nr.font(30)
    over = bands(broadcast_overlay(scene))
    over_short = bands(broadcast_overlay(scene, TAG_X_SHORT))
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
    hook_size = 72  # shrink until the widest hook line fits with a margin
    while hook_size > 36 and max(sd.textlength(t, font=nr.font(hook_size)) for t in scene["hook"].split("\n")) > SW - 100:
        hook_size -= 2
    sd.multiline_text((SW / 2, 300), scene["hook"], font=nr.font(hook_size), fill=nr.WHITE, anchor="mm",
                      align="center", spacing=18)
    where = scene.get("full_episode_where")  # e.g. "on YouTube" for a Reels / TikTok copy
    card = scene.get("end_card")  # a video with no full episode behind it (the channel intro) says what to do instead
    nr.shorts_promo(short_static, sd, where or "on the channel",
                    f"{nr.HANDLE}  |  {card['line']}  >" if card else None)

    still_img = None  # a picture for "still" shots (bigger than the frame, room for the slow push)
    if scene.get("still"):
        still_img = fit_cover(Image.open(scene["still"]).convert("RGB"), int(W * 1.2), int(H * 1.2))
        if scene.get("still_credit"):
            sd_ = ImageDraw.Draw(still_img)
            sd_.text((36, still_img.height - 30), scene["still_credit"], font=nr.font(26), fill=(230, 235, 245),
                     anchor="lm", stroke_width=3, stroke_fill=(0, 0, 0))

    def still_frames(ln, t, tags):
        """(long view, Short crop) of the still at t: slow push, name tags popped in so far."""
        img = still_img
        if tags:
            img = still_img.copy()
            td = ImageDraw.Draw(img)
            tf = nr.font(44)  # big enough to read in a Short, where the picture is only 1080 px wide
            for at, tg in tags:
                if t >= at:
                    tx_, ty_ = tg["x"] * img.width, tg["y"] * img.height
                    tw_ = td.textlength(tg["text"], font=tf)
                    td.rounded_rectangle((tx_ - tw_ / 2 - 16, ty_ - 32, tx_ + tw_ / 2 + 16, ty_ + 32), 11,
                                         fill=nr.YELLOW, outline=nr.BLACK, width=3)
                    td.text((tx_, ty_), tg["text"], font=tf, fill=nr.BLACK, anchor="mm")
        z = 1.0 + min(0.06, 0.012 * max(0.0, t - (ln["start"] - 0.15)))
        cw_, ch_ = img.width / z, img.height / z
        box = ((img.width - cw_) / 2, (img.height - ch_) / 2, (img.width + cw_) / 2, (img.height + ch_) / 2)
        long_view = img.resize((W, H), Image.BILINEAR, box=box)
        fit = img.resize((SHORT_W, SHORT_W * H // W), Image.BILINEAR, box=box)  # whole picture, not cropped
        crop = Image.new("RGB", (SHORT_W, 1080), nr.BRAND_NAVY)
        crop.paste(fit, (0, (1080 - fit.height) // 2))
        return long_view, crop

    still_tags, tags_line = [], None
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
        if shot == "cam":
            target = [ln["cam"][0] + OX, ln["cam"][1], ln["cam"][2]]
        elif shot == "anchor_solo":
            target = [ax, 480, 1.25]
        elif shot == "anchor_screen":
            target = [ax - ANCHOR_VIEW_X + W / 2, 540, 1.0]
        elif shot == "k_screen":  # the speaker (anchor or a guest) on the left, the screen on the right, 1.5x zoom
            target = [p.x + OX + 350, 470, 1.5]
        elif shot == "host_screen":  # two hosts side by side, the box beside them: hosts on the right of the box ("left") or on the left ("right")
            left = min(puppets.values(), key=lambda q: q.x)
            target = [left.x + OX + (730 if ln.get("side", "right") == "right" else -60), 540, 1.0]
        elif shot == "screen_full":  # desk center, so the big screen covers everyone instead of cutting a face
            target = [WORLD_W / 2, 540, 1.0]
        elif shot == "two_shot":
            others = [q.x + OX for k, q in puppets.items()]
            target = [(min(others) + max(others)) / 2, 520, 1.1]
        elif shot == "speaker_close":
            target = [p.x + OX, 470, 1.32]
        else:  # wide
            target = [WORLD_W / 2, 540, 1.0]
        held = t - (ln["start"] - 0.15)
        if held > 4 and shot not in SCREEN_SHOTS and ln.get("push", True):  # the side screen is laid out for this exact framing  # slow push so a long shot doesn't sit still
            target[2] += min(0.06, 0.015 * (held - 4))
        return target

    def ff(path, w, h, start=0.0, audio_len=None):
        # audio_len: keep that much of the track, then silence (a Short's end card must not play the next line)
        af = ["-af", f"atrim=0:{audio_len:.3f},apad"] if audio_len is not None else []
        return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                                 "-r", str(FPS), "-i", "-", "-ss", f"{start:.3f}", "-i", wav, "-c:v", "libx264",
                                 "-preset", "superfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac",
                                 "-ar", str(OUT_SR), "-b:a", "192k", "-shortest", *af, path], stdin=subprocess.PIPE)

    lp = ff(scene["out_long"], W, H)
    sp = ff(scene["out_short"], SW, SH, s_from, s_to - s_from) if s_from is not None else None
    last_short = None
    cam = cam_target(lines[0], 0)
    rect, alpha = list(SCREEN_OTS), 0.0
    short_x = (W - SHORT_W) / 2
    shown_screen, prev_line, run_t0 = None, None, 0.0
    base_gaze = {k: (0.0, 0.0) for k in puppets}
    for i in range(n):
        t = i / FPS
        ln = line_at(t)
        if ln is not prev_line:  # same picture, same box position as the previous line: it keeps running (no flicker on a speaker change)
            cont = bool(prev_line is not None and one_key(ln) and one_key(prev_line) == one_key(ln) and ln["shot"] in SCREEN_SHOTS
                        and prev_line["shot"] in SCREEN_SHOTS and box_goal(prev_line) == box_goal(ln))
            run_t0 = run_t0 if cont else ln["start"]
            ln["_cont"], ln["_run"] = cont, run_t0
        spk = speaking(t)
        anchor_cam = ln["shot"] in ANCHOR_CAMERA
        visible = [anchor_key] if anchor_cam else [ln["who"]] if ln["shot"] == "k_screen" else list(puppets)
        # k_screen: only the speaker is drawn (left of the box); a listener behind the box would peek out around it

        # camera: cut when switching between the anchor camera and the desk camera, otherwise ease
        tx, ty, tz = cam_target(ln, t)
        cut = prev_line is not None and ln is not prev_line and (prev_line["shot"] in ANCHOR_CAMERA) != anchor_cam
        if prev_line is not None and ln is not prev_line and ln.get("cam_id") and prev_line.get("cam_id"):
            cut = ln["cam_id"] != prev_line["cam_id"]  # a different "camera" is a hard cut, never a pan
        if cut:
            cam = [tx, ty, tz]
        a = ln.get("ease", 0.14)
        cam = [cam[0] + (tx - cam[0]) * a, cam[1] + (ty - cam[1]) * a, cam[2] + (tz - cam[2]) * a]
        prev_line = ln

        # explainer screen: slides between beside-anchor and full frame, fades when not used
        if ln.get("screen") and ln["shot"] in SCREEN_SHOTS:
            key, since, prev_key, fade = screen_at(ln, t)
            shown_screen = (key, since, prev_key, fade)
            goal, goal_a = box_goal(ln), 1.0
        else:
            goal, goal_a = rect, 0.0
            if shown_screen is not None:  # keep the last picture moving while it fades out
                key, since, prev_key, fade = shown_screen
                shown_screen = (key, since + 1 / FPS, None, 1.0)
        rect = [r + (g - r) * 0.2 for r, g in zip(rect, goal)]
        alpha += (goal_a - alpha) * (0.3 if goal_a else 0.5)
        if cut and not ln.get("_cont"):
            alpha = 0.0  # a camera cut takes the box with it (unless the same box continues over the cut)

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
            elif k == anchor_key and ln["shot"] in SCREEN_SHOTS and t - ln["start"] < 0.7:
                g = (0.8, 0.1)  # glance at the screen (to the anchor's right), then back to camera
            # a line can set expressions, e.g. "mood": {"chef": "neutral"} for the moment the food wins him over
            p.draw(world, t, g, dg.lid_at(t, blinks[k]), envs[k][i], nod, ox=OX, mood=(ln.get("mood") or {}).get(k))
        paste_bands(world, desks["anchor" if anchor_cam else "all"])

        cw, ch = W / cam[2], H / cam[2]
        cx = min(max(cam[0], cw / 2), WORLD_W - cw / 2)
        cy = min(max(cam[1], ch / 2), H - ch / 2)
        view = world.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize(
            (W, H), Image.BILINEAR)
        if shown_screen is not None and alpha > 0.02:
            key, since, prev_key, fade = shown_screen
            scr = screens[key]
            w_box, h_box = int(round(rect[2] - rect[0])), int(round(rect[3] - rect[1]))
            content = screen_content(scr, w_box, h_box, since)
            if prev_key is not None and fade < 1:
                old_scr = screens[prev_key]
                content = Image.blend(screen_content(old_scr, w_box, h_box, since + KB_SECONDS * 0.5), content,
                                      ease(fade))
            piece, xy = screen_piece(content, rect, alpha, scr.get("label", ""), scr.get("credit", ""))
            view.paste(piece, xy, piece)
        still_crop = None
        if ln["shot"] == "still" and still_img is not None:
            if ln.get("tags") and ln is not tags_line:  # a run of still lines keeps the tags that popped in
                still_tags = [(ln["start"] + tg.get("at", 0.0), tg) for tg in ln["tags"]]
                tags_line = ln
            view, still_crop = still_frames(ln, t, still_tags)
        else:
            still_tags, tags_line = [], None
        short_crop = None
        if sp is not None and s_from <= t <= s_to:
            goal_x = SHORT_X.get(ln["shot"], (W - SHORT_W) / 2)
            short_x = goal_x if cut else short_x + (goal_x - short_x) * 0.2  # pans with the screen box
            x0 = int(round(short_x))
            short_crop = still_crop if still_crop is not None else view.crop((x0, 0, x0 + SHORT_W, 1080))
            # tags and lower third are laid out for the centered crop; keep them fixed in the Short
            for piece, (px, py) in over_short:
                short_crop.paste(piece, (px - (W - SHORT_W) // 2, py), piece)
        if chips_on and ln["shot"] not in ("still", "screen_full"):
            # name chips just above the lower third, centered under whoever is in frame (never hidden by the bar)
            cd = ImageDraw.Draw(view)
            for k in visible:
                vx = (puppets[k].x + OX - (cx - cw / 2)) * cam[2]
                if not 150 < vx < 1770:
                    continue
                lab = puppets[k].label
                tw_ = cd.textlength(lab, font=chip_font)
                cd.rounded_rectangle((vx - tw_ / 2 - 18, 878, vx + tw_ / 2 + 18, 922), 10, fill=nr.YELLOW)
                cd.text((vx, 900), lab, font=chip_font, fill=nr.BLACK, anchor="mm")
        paste_bands(view, over)

        if short_crop is not None:
            crop = short_crop.resize((1080, 810), Image.BILINEAR)
            sframe = short_static.copy()
            sframe.paste(crop, (0, 600))
            grp = next((g for g in groups if g[0]["s"] <= t <= g[-1]["e"] + 0.15), None)
            if grp:
                nr.draw_caption(sframe, grp, t)
            sp.stdin.write(np.asarray(sframe).tobytes())
            last_short = sframe

        off = int(t * 110) % ticker_w
        view.paste(ticker.crop((off, 0, off + W - 190, 40)), (190, 1040))
        paste_bands(view, bug)
        lp.stdin.write(np.asarray(view).tobytes())

    if sp is not None and last_short is not None:
        for i in range(int(END_CARD * FPS)):
            sp.stdin.write(np.asarray(end_card(last_short, i / FPS, where or "on our channel",
                                               scene.get("end_card"))).tobytes())
    for p in (lp, sp):
        if p is not None:
            p.stdin.close()
            p.wait()
    print(json.dumps({"duration": round(duration, 2),
                      "shots": [(l["who"], l["shot"], round(l["start"], 2)) for l in lines]}))


if __name__ == "__main__":
    main()
