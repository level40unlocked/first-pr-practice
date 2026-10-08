"""EP.5 Shorts (~30 s each): a run of consecutive lines cut out of a segment; photo lines use the big screen (screen_full) so the picture
carries the Short and the voice explains it.

    cd episodes/ep05 && ./run_segments.sh 1 2 >/dev/null   # (or just python3 build_episode.py) so render/ep05_s*.json are current
    python3 make_shorts.py            # YouTube Shorts -> render/ep05_short_*.mp4
    python3 make_shorts.py --reels    # Instagram Reels copy
"""
import json, os, subprocess, sys
REELS = "--reels" in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))
# name: (segment, first global line, last global line, hook)
PLAN = {
    "turtle": (1, 9, 13, "A jazz festival on\nTurtle Island?"),
    "nate": (1, 24, 27, "17 years later,\na Grammy winner returns."),
    "biff": (2, 35, 39, "It used to be PIFF.\nOne letter changed."),
    "michelle": (2, 50, 53, "Everything Everywhere\nAll for Michelle."),
}
from screens import SCREENS
PLAIN = {"turtle", "gapyeong_dusk", "nate_smith", "rodriguez", "biff1996"}  # caption-bar cards -> plain variants (the Short burns its own captions there)
BASE = {1: 1, 2: 34}  # global index of a segment's first line
procs = []
for name, (n, a, b, hook) in PLAN.items():
    sc = json.load(open(os.path.join(HERE, "render", f"ep05_s{n}.json")))
    lines = sc["lines"][a - BASE[n]: b - BASE[n] + 1]
    for ln in lines:
        if ln.get("screen"):
            keys = ln["screen"] if isinstance(ln["screen"], list) else [ln["screen"]]
            keys = [k + "_p" if k in PLAIN else k for k in keys]
            ln["screen"] = keys if len(keys) > 1 else keys[0]
            for k in keys: sc["screens"][k] = SCREENS[k]
            ln["shot"], ln["cam_id"] = "screen_full", "screen_full"
            ln.pop("side", None); ln.pop("box", None)
    out = f"ep05_{'reel' if REELS else 'short'}_{name}.mp4"
    sc.update({"lines": lines, "short": {}, "hook": hook, "out_short": f"render/{out}", "out_long": f"render/_scratch_{name}.mp4"})
    if REELS: sc["full_episode_where"] = "on YouTube (link in bio)"
    p = os.path.join(HERE, "render", f"short_{name}.json")
    json.dump(sc, open(p, "w"), ensure_ascii=False, indent=1)
    procs.append(subprocess.Popen([sys.executable, os.path.join(HERE, "../../prototypes/episode.py"), p], cwd=HERE,
                                  stdout=open(os.path.join(HERE, "render", f"short_{name}.log"), "w"), stderr=subprocess.STDOUT))
for p in procs: p.wait()
print("done", [p.returncode for p in procs])
