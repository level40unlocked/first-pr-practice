"""EP.3 Shorts: one cut per segment. Writes render/short_<n>.json and renders them (the segment's long output goes to scratch)."""
import json, os, subprocess, sys
REELS = "--reels" in sys.argv  # Instagram Reels copy: the end card and footer point to YouTube instead of "the channel"
HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = {  # segment number: (first line, last line, hook, file)
    1: (10, 19, "Seoul fever is real.\nThe puns are worse.", "ep03_short_fever.mp4"),
    3: (1, 12, "Korea just sold $121 billion\nof stuff in one month.", "ep03_short_exports.mp4"),
    4: (3, 11, "Korea takes a day off\nfor its alphabet.", "ep03_short_hangul.mp4"),
    6: (0, 7, "Why Koreans ask\nyour age within 5 minutes.", "ep03_short_age.mp4"),
}
ep = json.load(open(os.path.join(HERE, "render", "ep03_s1.json")))
procs = []
for n, (a, b, hook, out) in PLAN.items():
    sc = json.load(open(os.path.join(HERE, "render", f"ep03_s{n}.json")))
    out = out.replace("short", "reel") if REELS else out
    sc.update({"short": {"from": a, "to": b}, "hook": hook, "out_short": f"render/{out}", "out_long": f"render/_scratch_s{n}.mp4"})
    if REELS: sc["full_episode_where"] = "on YouTube (link in bio)"
    p = os.path.join(HERE, "render", f"short_{n}.json")
    json.dump(sc, open(p, "w"), ensure_ascii=False, indent=1)
    procs.append(subprocess.Popen([sys.executable, os.path.join(HERE, "../../prototypes/episode.py"), p],
                                  cwd=HERE, stdout=open(os.path.join(HERE, "render", f"short_{n}.log"), "w"), stderr=subprocess.STDOUT))
for p in procs: p.wait()
print("done", [p.returncode for p in procs])
