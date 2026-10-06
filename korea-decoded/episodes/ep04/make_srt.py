"""EP.4 English subtitles: timing rebuilt from the real audio lengths, same timeline episode.py uses (0.5 s lead-in, 0.35 s gaps, 0.6 s tail)."""
import json, re, subprocess, os
HERE = os.path.dirname(os.path.abspath(__file__))
ep = json.load(open(os.path.join(HERE, "ep04_episode.json")))

def dur(path):
    out = subprocess.run(["ffmpeg", "-i", path, "-f", "null", "-"], capture_output=True, text=True).stderr
    h, m, s = re.findall(r"time=(\d+):(\d+):([\d.]+)", out)[-1]
    return int(h) * 3600 + int(m) * 60 + float(s)

def ts(x):
    ms = round(x * 1000); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def chunks(text, limit=76):
    """Prefer breaks at sentence ends; only split inside a sentence (at commas, then at words) when it alone is too long."""
    if len(text) <= limit: return [text]
    sents = re.split(r"(?<!Dr\.)(?<=[.!?])\s+", text)
    flat = []
    for s_ in sents:
        if len(s_) <= limit: flat.append(s_); continue
        cur = ""
        for p in re.split(r"(?<=[,:;])\s+", s_):
            if cur and len(cur) + 1 + len(p) > limit: flat.append(cur); cur = p
            else: cur = (cur + " " + p).strip()
        flat.append(cur)
    out, cur = [], ""
    for p in flat:
        if cur and len(cur) + 1 + len(p) > limit: out.append(cur); cur = p
        else: cur = (cur + " " + p).strip()
    out.append(cur)
    return out

def wrap(s, width=42):
    if len(s) <= width: return s
    words, a = s.split(), ""
    best = None
    for i in range(1, len(words)):
        l1, l2 = " ".join(words[:i]), " ".join(words[i:])
        sc = abs(len(l1) - len(l2))
        if best is None or sc < best[0]: best = (sc, l1, l2)
    return best[1] + "\n" + best[2]

cues, off, n = [], 0.0, 0
for seg in ep["segments"]:
    t = 0.5
    for ln in seg["lines"]:
        d = dur(os.path.join(HERE, ln["audio"]))
        pieces = chunks(re.sub(r"\s*\[VERIFY\]", "", ln["text"]).strip())
        tot = sum(len(p) for p in pieces); acc = 0
        for p in pieces:
            a = t + d * acc / tot; acc += len(p); b = t + d * acc / tot
            n += 1; cues.append(f"{n}\n{ts(off + a)} --> {ts(off + b)}\n{wrap(p)}\n")
        t += d + 0.35
    seg_len = t + 0.6
    print("segment", round(seg_len, 2))
    off += seg_len
print("total", round(off, 2), "cues", n)
open(os.path.join(HERE, "ep04_en.srt"), "w", encoding="utf-8").write("\n".join(cues))
