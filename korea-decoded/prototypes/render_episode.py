"""Renders a whole episode: one episode.py run per segment, several at once, then joins the long form.

usage: python3 render_episode.py episode.json [--jobs N]

episode.json holds what the segments share (episode number, characters, anchor) and a "segments" list;
each segment is what episode.py takes (category, desk, headline, hook, screens, lines, short).
This script fills in TOPIC n/N, the UP NEXT ticker (the headlines still to come) and file names, so
every segment is rendered on its own (under the sandbox's 15-minute limit) and several run side by side.
Outputs: <name>_long.mp4 (all segments joined) and <name>_s<n>_short.mp4 per segment that has a Short.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))


def split_episode(ep, name):
    """Returns one episode.py scene per segment."""
    segs = ep["segments"]
    total = len(segs)
    scenes = []
    for i, seg in enumerate(segs):
        later = [s["headline"] for s in segs[i + 1:]] or [ep.get("outro_ticker", "Thanks for watching")]
        scenes.append({
            "episode": ep["episode"],
            "anchor": ep.get("anchor", "anchor"),
            "characters": {k: v for k, v in ep["characters"].items()
                           if k == ep.get("anchor", "anchor") or any(l["who"] == k for l in seg["lines"])},
            "topic": [i + 1, total],
            **({"background": ep["background"]} if ep.get("background") else {}),
            "up_next": later,
            **seg,
            "out_long": f"{name}_s{i + 1}_long.mp4",
            "out_short": f"{name}_s{i + 1}_short.mp4",
        })
    return scenes


def render(scene, path):
    with open(path, "w") as f:
        json.dump(scene, f, ensure_ascii=False, indent=1)
    t0 = time.time()
    done = subprocess.run([sys.executable, os.path.join(HERE, "episode.py"), path], capture_output=True, text=True)
    if done.returncode != 0:
        raise RuntimeError(f"{path} failed:\n{done.stderr[-2000:]}")
    info = json.loads(done.stdout.strip().splitlines()[-1])
    return {**info, "file": scene["out_long"], "seconds": round(time.time() - t0)}


def join(files, out):
    """Concatenates segment videos (same codec settings, so no re-encode)."""
    listing = out + ".txt"
    with open(listing, "w") as f:
        f.writelines(f"file '{os.path.abspath(p)}'\n" for p in files)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", out],
                   check=True)
    os.remove(listing)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    args = ap.parse_args()
    ep = json.load(open(args.episode))
    name = ep.get("name", f"ep{ep['episode']}")
    scenes = split_episode(ep, name)

    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = list(pool.map(lambda a: render(*a),
                                [(s, f"{name}_s{i + 1}.json") for i, s in enumerate(scenes)]))
    join([r["file"] for r in results], f"{name}_long.mp4")
    print(json.dumps({"long": f"{name}_long.mp4",
                      "shorts": [s["out_short"] for s in scenes if s.get("short", {}) is not False],
                      "segments": results}))


if __name__ == "__main__":
    main()
