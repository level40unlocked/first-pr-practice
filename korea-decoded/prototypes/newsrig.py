"""News-show puppet prototype: AI-drawn head (no eyes/mouth) + body, code-drawn face.

usage: python3 newsrig.py --head head.png --body body.png --ref ref.png --audio a.wav
                          --screens s1.png s2.png ... --out-long long.mp4 --out-short short.mp4
                          [--words words.json] [--max-seconds 15] [--debug debug.png]
"""
import argparse
import json
import math
import random
import re
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
SW, SH = 1080, 1920
NAVY, NAVY2 = (12, 20, 42), (28, 44, 86)
YELLOW, WHITE, BLACK, RED = (255, 212, 0), (255, 255, 255), (15, 15, 20), (220, 38, 38)
FONT = "/usr/share/fonts/truetype/higgsfield/Montserrat-ExtraBold.ttf"
CHANNEL = "CHANNEL NAME"
HEADLINE = "Korean convenience stores are NOT boring"
SCREEN_LABEL = "CONVENIENCE STORES"
HOOK = "Korea's convenience stores\nare on another level"


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default(size)


# ── asset prep ────────────────────────────────────────────────────────────
def remove_bg(img, tol=28):
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    near = (np.abs(a - bg).max(axis=2) < tol).astype(np.uint8)
    _, lab = cv2.connectedComponents(near, connectivity=4)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgmask = np.isin(lab, list(edge)) & (near == 1)
    alpha = cv2.erode(np.where(bgmask, 0, 255).astype(np.uint8), np.ones((3, 3), np.uint8))
    out = Image.fromarray(np.dstack([a.astype(np.uint8), alpha]))
    return out.crop(out.getbbox())


def fg_widths(rgba):
    alpha = np.asarray(rgba)[..., 3] > 0
    cols = [np.nonzero(r)[0] for r in alpha]
    return [(c.max() - c.min()) if len(c) else 0 for c in cols]


def analyze_head(head):
    a = np.asarray(head)
    rgb, alpha = a[..., :3].astype(int), a[..., 3] > 0
    h, w = alpha.shape
    dark = (rgb.sum(2) < 220) & alpha
    light = (~dark & alpha).astype(np.uint8)
    n, _, stats, cent = cv2.connectedComponentsWithStats(light, connectivity=4)
    cands = []
    for i in range(1, n):
        x, y, bw, bh, area = stats[i]
        cx, cy = cent[i]
        if not (0.002 * h * w < area < 0.08 * h * w):
            continue
        if not (0.65 < bw / bh < 1.5 and area / (bw * bh) > 0.55):
            continue
        if not (0.2 * h < cy < 0.75 * h and abs(cx - w / 2) < 0.32 * w):
            continue
        cands.append((cx, cy, (bw + bh) / 4, area))
    best = None
    for p in cands:
        for q in cands:
            if p[0] >= q[0]:
                continue
            score = (abs(p[3] - q[3]) / max(p[3], q[3]) + 5 * abs(p[1] - q[1]) / h
                     + 3 * abs((p[0] + q[0]) / 2 - w / 2) / w)
            if best is None or score < best[0]:
                best = (score, p, q)
    if best is None:
        raise SystemExit(f"could not find the two empty lenses ({len(cands)} candidates)")
    (lx, ly, lr, _), (rx, ry, rr, _) = best[1], best[2]
    r = (lr + rr) / 2
    mx, ey = (lx + rx) / 2, (ly + ry) / 2
    sep = rx - lx
    band = slice(int(mx - 0.15 * sep), int(mx + 0.15 * sep))
    lens_skin = np.median(rgb[int(ly) - 3:int(ly) + 3, int(lx) - 3:int(lx) + 3].reshape(-1, 3), axis=0)
    # Jawline: the lowest face-skin pixel under the nose line (the outline below it is the chin).
    is_skin = (np.abs(rgb - lens_skin).sum(axis=2) < 70) & alpha
    skin_rows = [y for y in range(int(ey + r), h) if is_skin[y, band].any()]
    chin = skin_rows[-1] if skin_rows else int(np.nonzero(alpha[:, band].any(axis=1))[0].max())
    # Nose: first dark run between the glasses and the lower part of the face (never the jawline).
    wide = slice(int(mx - 0.25 * sep), int(mx + 0.25 * sep))
    stop = int(chin - 0.25 * (chin - ey))
    rows = [y for y in range(int(ey + 1.25 * r), stop) if dark[y, wide].any()]
    nose_bottom = None
    if rows:
        nose_bottom = rows[0]
        for y in rows[1:]:
            if y - nose_bottom > 3:
                break
            nose_bottom = y
    if nose_bottom:
        mouth_y = nose_bottom + 0.45 * (chin - nose_bottom)
    else:  # faint or missing nose: same eye-to-chin proportion as the validated anchor
        mouth_y = ey + 0.66 * (chin - ey)
    mouth_y = min(mouth_y, chin - 0.12 * (chin - ey))
    return {"eyes": [(lx, ly), (rx, ry)], "r": r, "sep": sep, "mouth": (mx, mouth_y),
            "mouth_w": 0.42 * sep, "chin": chin, "nose_bottom": nose_bottom,
            "skin": tuple(int(v) for v in lens_skin)}


# ── face drawing ──────────────────────────────────────────────────────────
def draw_eye(d, img_size, cx, cy, r, gaze, lid, skin):
    rx, ry, lw = 0.52 * r, 0.40 * r, max(2, int(0.07 * r))
    box = (cx - rx, cy - ry, cx + rx, cy + ry)
    d.ellipse(box, fill=WHITE, outline=BLACK, width=lw)
    pr = 0.24 * r
    px = cx + max(-1, min(1, gaze[0])) * (rx - pr - lw)
    py = cy + max(-1, min(1, gaze[1])) * (ry - pr - lw) * 0.6
    d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=BLACK)
    d.ellipse((px - pr * 0.35 + pr * 0.3, py - pr * 0.6, px + pr * 0.05 + pr * 0.3, py - pr * 0.2), fill=WHITE)
    if lid > 0:
        edge = cy - ry + 2 * ry * lid
        mask = Image.new("L", img_size, 0)
        md = ImageDraw.Draw(mask)
        md.ellipse((box[0] - lw, box[1] - lw, box[2] + lw, box[3] + lw), fill=255)
        cover = Image.new("L", img_size, 0)
        ImageDraw.Draw(cover).rectangle((box[0] - lw, box[1] - lw, box[2] + lw, edge), fill=255)
        m = np.minimum(np.asarray(mask), np.asarray(cover))
        return Image.fromarray(m), (box, edge, lw)
    return None, None


def face_layer(head, rig, gaze, lid, mouth):
    img = head.copy()
    d = ImageDraw.Draw(img)
    lids = []
    for (ex, ey) in rig["eyes"]:
        m, info = draw_eye(d, img.size, ex, ey, rig["r"], gaze, lid, rig["skin"])
        if m is not None:
            lids.append((m, info))
    for m, (box, edge, lw) in lids:
        skin = Image.new("RGBA", img.size, rig["skin"] + (255,))
        img.paste(skin, (0, 0), m)
        d = ImageDraw.Draw(img)
        # lid edge: a chord across the eye at `edge`
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        rx, ry = (box[2] - box[0]) / 2, (box[3] - box[1]) / 2
        t = max(-1, min(1, (edge - cy) / ry))
        half = rx * math.sqrt(max(0, 1 - t * t))
        d.line((cx - half - lw, edge, cx + half + lw, edge), fill=BLACK, width=lw)
    d = ImageDraw.Draw(img)
    mx, my = rig["mouth"]
    mw, lw = rig["mouth_w"], max(3, int(0.06 * rig["r"]))
    if mouth == "closed":
        d.arc((mx - mw / 2, my - mw * 0.25, mx + mw / 2, my + mw * 0.12), 20, 160, fill=BLACK, width=lw)
    else:
        oh = mw * (0.26 if mouth == "mid" else 0.46)
        ow = mw * (0.72 if mouth == "mid" else 0.8)
        box = (mx - ow / 2, my - oh / 2, mx + ow / 2, my + oh / 2)
        d.ellipse(box, fill=(110, 20, 30), outline=BLACK, width=lw)
        d.chord((box[0] + lw, box[1] + lw, box[2] - lw, box[1] + oh * 0.9), 200, 340, fill=WHITE)
        if mouth == "open":
            d.chord((box[0] + ow * 0.2, box[1] + oh * 0.45, box[2] - ow * 0.2, box[3] - lw), 0, 180,
                    fill=(230, 110, 120))
    return img


# ── audio ─────────────────────────────────────────────────────────────────
def load_audio(path, max_seconds):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-t", str(max_seconds), "-ac", "1",
                          "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def envelope(samples, n_frames):
    hop = 16000 / FPS
    chunks = [samples[int(i * hop):int((i + 1) * hop)] for i in range(n_frames)]
    rms = np.array([np.sqrt(np.mean(c ** 2)) if len(c) else 0.0 for c in chunks])
    rms /= np.percentile(rms, 95) + 1e-9
    env, out = 0.0, []
    for v in rms:
        env += (v - env) * (0.85 if v > env else 0.45)
        out.append(env)
    return np.clip(out, 0, 1.2)


def transcribe(path):
    from faster_whisper import WhisperModel
    segs, _ = WhisperModel("base.en", device="cpu", compute_type="int8").transcribe(path, word_timestamps=True)
    return [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in s.words]


# ── static layers ─────────────────────────────────────────────────────────
def studio_background():
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=tuple(int(a + (b - a) * t) for a, b in zip(NAVY, NAVY2)))
    for x in range(0, W, 120):  # faint grid
        d.line((x, 0, x, 780), fill=(40, 58, 100), width=1)
    for y in range(60, 780, 120):
        d.line((0, y, W, y), fill=(40, 58, 100), width=1)
    d.ellipse((1080, 90, 1720, 730), outline=(60, 84, 140), width=6)  # halo behind anchor
    return bg


def desk_layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(960, 800), (1800, 800), (1860, 1080), (900, 1080)], fill=(22, 26, 36))
    d.rectangle((960, 800, 1800, 812), fill=YELLOW)
    f = font(34)
    d.text((1380, 870), CHANNEL, font=f, fill=WHITE, anchor="mm")
    return img


def overlay_layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((270, 50, 420, 100), 12, fill=RED)
    d.ellipse((288, 66, 306, 84), fill=WHITE)
    d.text((316, 75), "LIVE", font=font(30), fill=WHITE, anchor="lm")
    d.text((1650, 75), "12:34 KST", font=font(30), fill=WHITE, anchor="rm")
    d.rectangle((240, 930, 1680, 1030), fill=(255, 255, 255))
    d.rectangle((240, 930, 520, 1030), fill=YELLOW)
    d.text((380, 980), "BREAKING", font=font(40), fill=BLACK, anchor="mm")
    f = font(40)
    while d.textlength(HEADLINE, font=f) > 1110:
        f = font(f.size - 2)
    d.text((550, 980), HEADLINE, font=f, fill=BLACK, anchor="lm")
    return img


def screen_frames(paths, size=(760, 428)):
    out = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        tw, th = size
        s = max(tw / im.width, th / im.height)
        im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
        l, t = (im.width - tw) // 2, (im.height - th) // 2
        out.append(im.crop((l, t, l + tw, t + th)))
    return out


# ── main ──────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head"), ap.add_argument("--body"), ap.add_argument("--ref")
    ap.add_argument("--audio"), ap.add_argument("--screens", nargs="+")
    ap.add_argument("--out-long"), ap.add_argument("--out-short")
    ap.add_argument("--words"), ap.add_argument("--debug")
    ap.add_argument("--max-seconds", type=float, default=15)
    args = ap.parse_args()
    random.seed(7)

    head, body = remove_bg(Image.open(args.head)), remove_bg(Image.open(args.body))
    rig = analyze_head(head)

    # Scale: body shoulders to 640px; head width relative to shoulders as in the reference sheet.
    bw = max(fg_widths(body)[-40:])
    ratio = 0.48
    if args.ref:
        ref = remove_bg(Image.open(args.ref))
        widths = fg_widths(ref)
        top = widths[: int(len(widths) * 0.4)]
        ratio = max(top) / max(widths[-40:])
    sb = 640 / bw
    body = body.resize((int(body.width * sb), int(body.height * sb)), Image.LANCZOS)
    head_w_target = ratio * 640
    sh = head_w_target / head.width
    rig_scaled = {**rig, "eyes": [(x * sh, y * sh) for x, y in rig["eyes"]], "r": rig["r"] * sh,
                  "sep": rig["sep"] * sh, "mouth": (rig["mouth"][0] * sh, rig["mouth"][1] * sh),
                  "mouth_w": rig["mouth_w"] * sh, "chin": rig["chin"] * sh}
    head = head.resize((int(head.width * sh), int(head.height * sh)), Image.LANCZOS)

    body_alpha = np.asarray(body)[..., 3] > 0
    collar_top = int(np.nonzero(body_alpha.any(axis=1))[0].min())
    # Collar sits at y=500 so the head fills roughly y 150-500 and the desk hides the lower body.
    body_x, body_y = 1380 - body.width // 2, 500 - collar_top
    pivot = (1380, body_y + collar_top + int(0.03 * head.height))  # chin sits just into the collar

    if args.debug:
        dbg = face_layer(head, rig_scaled, (0, 0), 0, "open").convert("RGB")
        dd = ImageDraw.Draw(dbg)
        for ex, ey in rig_scaled["eyes"]:
            dd.ellipse((ex - rig_scaled["r"], ey - rig_scaled["r"], ex + rig_scaled["r"], ey + rig_scaled["r"]),
                       outline=(0, 200, 0), width=3)
        dbg.save(args.debug)

    samples = load_audio(args.audio, args.max_seconds)
    duration = len(samples) / 16000
    words = json.load(open(args.words)) if args.words else transcribe(args.audio)
    words = [w for w in words if w["e"] <= duration]
    # End on a sentence boundary when trimming.
    ends = [w["e"] for w in words if re.search(r"[.?!]$", w["w"])]
    if ends and duration >= args.max_seconds - 0.05:
        duration = min(duration, ends[-1] + 0.35)
    n = int(duration * FPS)
    env = envelope(samples, n)

    blinks, t = [], 1.2
    while t < duration:
        blinks.append(t)
        t += random.uniform(2.2, 4.8)
    glances = [(duration * 0.22, duration * 0.34), (duration * 0.62, duration * 0.72)]
    sacc = {}
    t, g = 0, (0.0, 0.0)
    while t < duration:
        sacc[int(t * FPS)] = (random.uniform(-0.25, 0.25), random.uniform(-0.2, 0.2))
        t += random.uniform(0.6, 1.8)

    bg, desk, over = studio_background(), desk_layer(), overlay_layer()
    screens = screen_frames(args.screens)
    sx, sy = 300, 190
    f_label = font(28)

    caption_groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or re.search(r"[.?!,…]$", w["w"]):
            caption_groups.append(cur)
            cur = []
    if cur:
        caption_groups.append(cur)

    short_static = Image.new("RGB", (SW, SH), NAVY)
    sd = ImageDraw.Draw(short_static)
    sd.text((SW / 2, 140), CHANNEL, font=font(44), fill=YELLOW, anchor="mm")
    sd.multiline_text((SW / 2, 380), HOOK, font=font(72), fill=WHITE, anchor="mm", align="center", spacing=18)
    sd.ellipse((110, 1640, 250, 1780), fill=YELLOW)
    sd.text((180, 1710), "CN", font=font(56), fill=NAVY, anchor="mm")
    sd.text((290, 1670), CHANNEL, font=font(48), fill=WHITE, anchor="lm")
    sd.text((290, 1740), "Full episode on the channel  >", font=font(34), fill=(190, 200, 225), anchor="lm")
    sd.rounded_rectangle((300, 1800, 780, 1870), 35, fill=RED)
    sd.text((540, 1835), "SUBSCRIBE", font=font(36), fill=WHITE, anchor="mm")

    def ff(path, w, h):
        return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                 "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-i", args.audio, "-t", f"{duration:.2f}",
                                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                                 "-c:a", "aac", "-shortest", path], stdin=subprocess.PIPE)

    long_p, short_p = ff(args.out_long, W, H), ff(args.out_short, SW, SH)
    gaze = (0.0, 0.0)
    for i in range(n):
        t = i / FPS
        if i in sacc:
            gaze = sacc[i]
        g = gaze
        for a, b in glances:
            if a <= t <= b:
                g = (-0.9, 0.1)
        lid = 0.0
        for bt in blinks:
            k = (t - bt) * FPS
            if 0 <= k < 5:
                lid = [0.5, 1.0, 1.0, 0.6, 0.2][int(k)]
        e = env[i]
        mouth = "closed" if e < 0.15 else ("mid" if e < 0.45 else "open")
        face = face_layer(head, rig_scaled, g, lid, mouth)
        angle = 1.6 * math.sin(2 * math.pi * t / 3.7) + 2.2 * e * math.sin(2 * math.pi * t * 1.1)
        if any(a <= t <= b for a, b in glances):
            angle += 3.0  # tilt toward the screen
        dy = -8 * e
        cx_head, chin = face.width / 2, rig_scaled["chin"]
        canvas = Image.new("RGBA", (face.width * 2, face.height * 2), (0, 0, 0, 0))
        canvas.paste(face, (face.width // 2, face.height // 2))
        rot = canvas.rotate(angle, resample=Image.BICUBIC,
                            center=(face.width // 2 + cx_head, face.height // 2 + chin))
        frame = bg.copy()
        scr = screens[min(int(t / 3.2), len(screens) - 1) % len(screens)]
        frame.paste((255, 255, 255), (sx - 8, sy - 8, sx + scr.width + 8, sy + scr.height + 8))
        frame.paste(scr, (sx, sy))
        fd = ImageDraw.Draw(frame)
        fd.rectangle((sx - 8, sy - 52, sx + 360, sy - 8), fill=YELLOW)
        fd.text((sx + 10, sy - 30), SCREEN_LABEL, font=f_label, fill=BLACK, anchor="lm")
        frame.paste(body, (body_x, body_y), body)
        hx = int(pivot[0] - (face.width // 2 + cx_head))
        hy = int(pivot[1] - (face.height // 2 + chin) + dy)
        frame.paste(rot, (hx, hy), rot)
        frame.paste(desk, (0, 0), desk)
        frame.paste(over, (0, 0), over)
        long_p.stdin.write(np.asarray(frame).tobytes())

        crop = frame.crop((240, 0, 1680, 1080)).resize((1080, 810), Image.BILINEAR)
        sframe = short_static.copy()
        sframe.paste(crop, (0, 600))
        grp = next((g for g in caption_groups if g[0]["s"] <= t <= g[-1]["e"] + 0.15), None)
        if grp:
            sdraw = ImageDraw.Draw(sframe)
            f = font(58)
            parts = [(w["w"].upper(), YELLOW if w["s"] <= t <= w["e"] + 0.05 else WHITE) for w in grp]
            total = sum(sdraw.textlength(p, font=f) for p, _ in parts) + 20 * (len(parts) - 1)
            x = (SW - total) / 2
            for p, c in parts:
                sdraw.text((x, 1500), p, font=f, fill=c, anchor="lm", stroke_width=5, stroke_fill=BLACK)
                x += sdraw.textlength(p, font=f) + 20
        short_p.stdin.write(np.asarray(sframe).tobytes())

    for p in (long_p, short_p):
        p.stdin.close()
        p.wait()
    print(json.dumps({"duration": round(duration, 2), "frames": n, "rig": {k: v for k, v in rig.items() if k != "skin"},
                      "head_body_ratio": round(ratio, 3)}, default=lambda o: round(float(o), 1)))


if __name__ == "__main__":
    main()
