"""EP.4 sound effects, synthesized (no samples, so no licensing). This file only builds the effects and a demo reel to listen to:

    python3 make_sfx.py      # writes render/sfx/<name>.wav and render/ep04_sfx_demo.mp3 (each effect with a gap, in the order printed)

Placing them under the episode comes after the operator has picked the ones to keep.
"""
import os, subprocess, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "render", "sfx")
os.makedirs(OUT, exist_ok=True)
SR = 44100


def env_exp(n, k): return np.exp(-np.linspace(0, k, n))
def tt(d): return np.arange(int(SR * d)) / SR
def adsr(n, a=0.005, r=0.05):
    e = np.ones(n); na, nr = max(1, int(SR * a)), max(1, int(SR * r))
    e[:na] = np.linspace(0, 1, na); e[-nr:] = np.minimum(e[-nr:], np.linspace(1, 0, nr)); return e


def pop():  # a card appears
    t = tt(0.14); f = 700 + 900 * (t / 0.14)
    return 0.55 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(len(t), 7)


def whoosh():
    n = int(SR * 0.38); x = np.random.default_rng(3).standard_normal(n)
    x = x - np.convolve(x, np.ones(40) / 40, "same")
    return 0.32 * x * np.sin(np.linspace(0, np.pi, n)) ** 2 / np.abs(x).max() * 2.2


def stamp():  # big number slams down
    t = tt(0.35); th = np.sin(2 * np.pi * 85 * t) * env_exp(len(t), 9)
    ns = np.random.default_rng(5).standard_normal(len(t)) * env_exp(len(t), 30) * 0.5
    return 0.9 * (th + ns) / 1.5


def fanfare():  # "FIN.K.L IS BACK!": airhorn-ish blast on a major chord with a short falling tail
    d = 1.1; t = tt(d); w = np.zeros(len(t))
    for f in (392.0, 493.9, 587.3, 783.99):
        for h in (1, 2, 3):
            w += np.sign(np.sin(2 * np.pi * f * h * t)) * 0.5 / h
    w += 0.4 * np.sin(2 * np.pi * np.cumsum(780 * (1 - 0.12 * np.clip(t - 0.8, 0, None) / 0.3)) / SR) * 0
    return 0.22 * w / 3 * adsr(len(t), 0.01, 0.35)


def heartbeat():  # "my heart doing choreography": lub-dub x3
    out = np.zeros(int(SR * 2.4))
    for k in range(3):
        for off, amp in ((0.0, 1.0), (0.22, 0.7)):
            t = tt(0.16); b = np.sin(2 * np.pi * 58 * t) * env_exp(len(t), 12) * amp
            i = int((k * 0.8 + off) * SR); out[i:i + len(b)] += b
    return 0.9 * out


def ding_dong():  # "Bingo."
    out = np.zeros(int(SR * 1.5))
    for off, f in ((0.0, 987.8), (0.45, 739.99)):
        t = tt(1.0); b = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2.76 * f * t) + 0.2 * np.sin(2 * np.pi * 5.4 * f * t)) * env_exp(len(t), 4.2)
        i = int(off * SR); out[i:i + len(b)] += 0.32 * b
    return out


def sparkle():  # glowing light sticks
    out = np.zeros(int(SR * 1.3)); rng = np.random.default_rng(11)
    for k in range(14):
        f = rng.choice([1568, 1976, 2349, 2637, 3136]); t = tt(0.18); b = np.sin(2 * np.pi * f * t) * env_exp(len(t), 9)
        i = int(rng.uniform(0, 1.05) * SR); out[i:i + len(b)] += 0.16 * b
    return out


def warn():  # "I'm calm!" gag: two short alarm beeps
    out = np.zeros(int(SR * 0.7))
    for off in (0.0, 0.3):
        t = tt(0.2); b = np.sign(np.sin(2 * np.pi * 880 * t)) * 0.14 * adsr(len(t), 0.004, 0.02)
        i = int(off * SR); out[i:i + len(b)] += b
    return out


def counter():  # 52 NEW RELEASES: ticks speeding up, then a hit
    out = np.zeros(int(SR * 1.8)); x = 0.0; gap = 0.16
    while x < 1.45:
        t = tt(0.03); b = np.sin(2 * np.pi * (1200 + 900 * x) * t) * env_exp(len(t), 8) * 0.35
        i = int(x * SR); out[i:i + len(b)] += b; x += gap; gap = max(0.035, gap * 0.9)
    i = int(1.5 * SR); h = stamp()[: int(SR * 0.3)]; out[i:i + len(h)] += 0.8 * h
    return out


def race_start():  # "a close race!": starting pistol and a short crowd swell
    out = np.zeros(int(SR * 1.8)); rng = np.random.default_rng(7)
    t = tt(0.12); out[: len(t)] += rng.standard_normal(len(t)) * env_exp(len(t), 25) * 0.6
    n = int(SR * 1.5); c = rng.standard_normal(n); c = np.convolve(c, np.ones(30) / 30, "same")
    out[int(0.25 * SR): int(0.25 * SR) + n] += c * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.9
    return out


def live_bleep():  # "I can't. It's live.": TV censor bleep
    t = tt(0.55); return 0.2 * np.sin(2 * np.pi * 1000 * t) * adsr(len(t), 0.005, 0.01)


def end_jingle():
    out = np.zeros(int(SR * 1.8))
    for off, f in ((0.0, 523.25), (0.14, 659.25), (0.28, 783.99), (0.42, 1046.5)):
        t = tt(0.5); b = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env_exp(len(t), 5) * 0.3
        i = int(off * SR); out[i:i + len(b)] += b
    t = tt(1.2)
    for f in (523.25, 659.25, 783.99, 1046.5):
        out[int(0.56 * SR): int(0.56 * SR) + len(t)] += 0.12 * np.sin(2 * np.pi * f * t) * env_exp(len(t), 2.6)
    return out


def tick():  # timeline step
    t = tt(0.05); return 0.4 * np.sin(2 * np.pi * 1500 * t) * env_exp(len(t), 9)


EFFECTS = [  # (name, what it is for)
    ("fanfare", "line 2: FIN.K.L IS BACK!"), ("heartbeat", "line 5: my heart doing choreography"), ("pop", "a photo card appears"),
    ("whoosh", "between shots"), ("stamp", "line 33: 21 YEARS slams down"), ("tick", "line 38: timeline steps"),
    ("ding_dong", "line 75: Bingo"), ("sparkle", "line 79: light sticks glow"), ("warn", "lines 88/159: I'm calm! gag"),
    ("counter", "lines 110-112: 52 NEW RELEASES"), ("race_start", "line 143: a close race"), ("live_bleep", "line 145: It's live"),
    ("end_jingle", "lines 163-165: sign-off"),
]


def save(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((x * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    demo, pos = [], 0.0
    for name, use in EFFECTS:
        w = globals()[name](); save(os.path.join(OUT, name + ".wav"), w)
        print(f"{pos:5.1f}s  {name:11s} {use}")
        demo.append(w); demo.append(np.zeros(int(SR * 1.0))); pos += len(w) / SR + 1.0
    d = os.path.join(HERE, "render", "ep04_sfx_demo.wav"); save(d, np.concatenate(demo))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", d, "-b:a", "128k", d.replace(".wav", ".mp3")], check=True)
