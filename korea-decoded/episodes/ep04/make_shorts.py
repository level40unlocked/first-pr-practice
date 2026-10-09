"""EP.4 Shorts (~30 s each): a run of consecutive lines cut out of a segment; photo lines use the big screen (screen_full) so the picture
carries the Short and the voice explains it.

    cd episodes/ep04 && ./run_segments.sh 1 2 >/dev/null   # (or just python3 build_episode.py) so render/ep04_s*.json are current
    python3 make_shorts.py            # YouTube Shorts -> render/ep04_short_*.mp4
    python3 make_shorts.py --reels    # Instagram Reels copy
"""
import json, os, subprocess, sys
REELS = "--reels" in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))
# name: (segment, first global line, last global line, hook)
PLAN = {
    "meet": (1, 17, 25, "Meet the four women\nbehind Fin.K.L."),
    "years": (1, 31, 35, "Fin.K.L waited\n21 years for this."),
    "onewzico": (2, 116, 120, "ONEW & ZICO:\na duet or a negotiation?"),
    "ive": (2, 139, 143, "IVE is going full\nsuperhero movie."),
}
BASE = {1: 1, 2: 101}  # global index of a segment's first line
procs = []
for name, (n, a, b, hook) in PLAN.items():
    sc = json.load(open(os.path.join(HERE, "render", f"ep04_s{n}.json")))
    lines = sc["lines"][a - BASE[n]: b - BASE[n] + 1]
    for ln in lines:
        if ln.get("screen"):
            ln["shot"], ln["cam_id"] = "screen_full", "screen_full"
            ln.pop("side", None); ln.pop("box", None)
    out = f"ep04_{'reel' if REELS else 'short'}_{name}.mp4"
    sc.update({"lines": lines, "short": {}, "hook": hook, "out_short": f"render/{out}", "out_long": f"render/_scratch_{name}.mp4"})
    if REELS: sc["full_episode_where"] = "on YouTube (link in bio)"
    p = os.path.join(HERE, "render", f"short_{name}.json")
    json.dump(sc, open(p, "w"), ensure_ascii=False, indent=1)
    procs.append(subprocess.Popen([sys.executable, os.path.join(HERE, "../../prototypes/episode.py"), p], cwd=HERE,
                                  stdout=open(os.path.join(HERE, "render", f"short_{name}.log"), "w"), stderr=subprocess.STDOUT))
for p in procs: p.wait()
print("done", [p.returncode for p in procs])
