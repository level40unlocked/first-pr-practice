"""EP.3 sound effects: synthesized (no samples, so no licensing) and mixed under the speech.

    python3 make_sfx.py            # writes render/ep03_sfx.wav and render/ep03_long_sfx.mp4

Event times come from the audio lengths (same timeline episode.py uses: 0.5 s lead-in, 0.35 s gaps, 0.6 s tail).
"""
import json, os, re, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "render")
SR = 44100
ep = json.load(open(os.path.join(HERE, "ep03_episode.json")))
dur = {int(k): v for k, v in json.load(open(os.path.join(HERE, "audio", "durations_v1.json"))).items()}

def env_exp(n, k): return np.exp(-np.linspace(0, k, n))
def pop():
    n = int(SR * 0.14); t = np.arange(n) / SR
    f = 700 + 900 * (t / 0.14)
    return 0.55 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 7)
def whoosh():
    n = int(SR * 0.38); rng = np.random.default_rng(3)
    x = rng.standard_normal(n)
    k = np.ones(40) / 40; lo = np.convolve(x, k, "same"); x = x - lo  # high-passed noise
    sweep = np.sin(np.linspace(0, np.pi, n)) ** 2
    return 0.32 * x * sweep / np.abs(x).max() * 2.2
def stamp():
    n = int(SR * 0.35); t = np.arange(n) / SR
    th = np.sin(2 * np.pi * 85 * t) * env_exp(n, 9)
    rng = np.random.default_rng(5); ns = rng.standard_normal(n) * env_exp(n, 30) * 0.5
    return 0.9 * (th + ns) / 1.5
def fanfare():
    out = []
    for f, d in ((523.25, 0.11), (659.25, 0.11), (783.99, 0.28)):
        n = int(SR * d); t = np.arange(n) / SR
        out.append(0.4 * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * np.minimum(1, np.minimum(t * 200, (d - t) * 30 + 0.2)))
    return np.concatenate(out)
def thermo():
    n = int(SR * 1.5); t = np.arange(n) / SR
    f = 280 + 900 * (t / 1.5) ** 1.5
    return 0.18 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t * 8) * np.minimum(1, (1.5 - t) * 6)

events, off, idx = [], 0.0, 0
for si, seg in enumerate(ep["segments"]):
    t = 0.5
    if si > 0: events.append((off + 0.15, "whoosh"))
    for ln in seg["lines"]:
        idx += 1
        start, d = t, dur[idx]
        if ln.get("screen"): events.append((off + start + 0.05, "pop"))
        if idx == 3: events.append((off + start + 0.2, "thermo"))
        if idx == 80: events.append((off + start + 0.75, "stamp"))
        if idx == 50: events.append((off + start + d - 0.5, "fanfare"))
        if ln["who"] == "guest" and not ln.get("screen") and seg["lines"].index(ln) > 0 and seg["lines"][seg["lines"].index(ln) - 1]["who"] != "guest":
            events.append((off + start - 0.1, "whoosh"))
        t += d + 0.35
    off += t + 0.6 - 0.35 + 0.35 - 0.35 if False else t + 0.6
total = off + 1
buf = np.zeros(int(SR * total) + SR)
fn = {"pop": pop, "whoosh": whoosh, "stamp": stamp, "fanfare": fanfare, "thermo": thermo}
for tt, name in events:
    w = fn[name](); i0 = int(tt * SR)
    buf[i0:i0 + len(w)] += w[: len(buf) - i0]
buf = np.clip(buf, -1, 1)
import wave
with wave.open(os.path.join(R, "ep03_sfx.wav"), "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((buf * 32767).astype(np.int16).tobytes())
print(len(events), "effects,", round(total, 1), "s")
for tt, name in events[:12]: print(round(tt, 1), name)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(R, "ep03_long.mp4"), "-i", os.path.join(R, "ep03_sfx.wav"),
                "-filter_complex", "[1:a]volume=0.5[s];[0:a][s]amix=inputs=2:duration=first:normalize=0[a]", "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", os.path.join(R, "ep03_long_sfx.mp4")], check=True)
