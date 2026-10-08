"""Downloads EP.5 voice lines listed in urls.txt (lines: index timestamp jobid) into v1/ep05_NNN.mp3 and records durations."""
import subprocess, os, re, json
B = "https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_%s_%s.mp3"
dur = json.load(open("durations_v1.json")) if os.path.exists("durations_v1.json") else {}
for l in open("urls.txt"):
    p = l.split()
    if len(p) != 3: continue
    i = int(p[0]); f = f"v1/ep05_{i:03d}.mp3"
    if os.path.exists(f) and os.path.getsize(f) > 2000: continue
    r = subprocess.run(["curl", "-sS", "-f", "-o", f, B % ("20261008_" + p[1], p[2])], capture_output=True)
    if r.returncode != 0: print("FAILED", i, r.stderr.decode()[:80]); continue
    out = subprocess.run(["ffmpeg", "-i", f, "-f", "null", "-"], capture_output=True, text=True).stderr
    h, m, s = re.findall(r"time=(\d+):(\d+):([\d.]+)", out)[-1]
    dur[str(i)] = round(int(h) * 3600 + int(m) * 60 + float(s), 2)
json.dump(dur, open("durations_v1.json", "w")); print(len(dur), "durations")
