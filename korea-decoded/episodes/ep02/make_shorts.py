"""EP.2 Shorts: one cut per segment. Writes render/short_<n>.json and renders them (the segment's long output goes to scratch)."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = {  # segment number: (first line, last line, hook, file)
    1: (11, 19, "Korea has bars where\nyou drink alone. On purpose.", "ep02_short_honsul.mp4"),
    2: (0, 7, "Koreans are shocked\nthis street food went global.", "ep02_short_bunsik.mp4"),
    3: (0, 9, "Korea has a word for\nwhen a hobby stops being fun.", "ep02_short_boredom.mp4"),
    4: (5, 16, "Why some Koreans\nbook a hotel for Chuseok.", "ep02_short_chuseok.mp4"),
}
ep = json.load(open(os.path.join(HERE, "render", "ep02_s1.json")))
procs = []
for n, (a, b, hook, out) in PLAN.items():
    sc = json.load(open(os.path.join(HERE, "render", f"ep02_s{n}.json")))
    sc.update({"short": {"from": a, "to": b}, "hook": hook, "out_short": f"render/{out}", "out_long": f"render/_scratch_s{n}.mp4"})
    p = os.path.join(HERE, "render", f"short_{n}.json")
    json.dump(sc, open(p, "w"), ensure_ascii=False, indent=1)
    procs.append(subprocess.Popen([sys.executable, os.path.join(HERE, "../../prototypes/episode.py"), p],
                                  cwd=HERE, stdout=open(os.path.join(HERE, "render", f"short_{n}.log"), "w"), stderr=subprocess.STDOUT))
for p in procs: p.wait()
print("done", [p.returncode for p in procs])
