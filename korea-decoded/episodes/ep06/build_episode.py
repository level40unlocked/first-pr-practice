"""Builds ep06_episode.json (input of prototypes/render_episode.py) from audio/lines_v1.json and screens.py.

    cd episodes/ep06 && python3 build_episode.py && ./run_segments.sh 1 2 3

Two segments (the AI hacking story was cut 2026-10-09): 1 = hypersonic test (with the intro; guest Ms. Nonfic), 2 = Hangul Day at 100 (guest Dr. H). Lines come from audio/lines_v2.json (old EP.6 lines reused + 4 new).
Picture lines use "k_screen" (speaker on the left, picture on the right); a speaker change is a hard cut, the picture stays put.
"""
import json
import os
from screens import SCREENS

HERE = os.path.dirname(os.path.abspath(__file__))
CAST = "../../cast/"
WHO = {"K": "anchor", "Kangfree": "panel", "Dusk": "guest", "Nonfic": "guest", "Dr. H": "guest"}
SEAT = {"panel": 630, "anchor": 1290, "guest": 2560}
SEG_EDGES = [(1, 40), (41, 73)]  # positions in audio/lines_v2.json (the hacking story was cut)
SEGS = [
    {"category": "current_affairs", "desk": "DEFENSE", "headline": "Korea's first hypersonic glide vehicle test"},
    {"category": "hidden_korea", "desk": "HANGUL", "headline": "Hangul Day turns 100"},
]
GUESTS = [
    {"head": CAST + "news_head.png", "body": CAST + "news_body.png", "ref": CAST + "news_ref.png", "label": "MS. NONFIC", "shoulders": 520, "white_lens": True},
    {"head": CAST + "hidden_head.png", "body": CAST + "hidden_body.png", "ref": CAST + "hidden_ref.png", "label": "DR. H", "shoulders": 520, "white_lens": True, "chin_drop": 0.10},
]
BASE = {
    "panel": {"head": CAST + "kangfree_head.png", "body": CAST + "kangfree_body.png", "ref": CAST + "kangfree_ref.png",
              "x": 630, "label": "DR. KANGFREE", "energy": 1.8, "head_ratio": 0.74, "shoulders": 500, "chin_drop": 0.12},
    "anchor": {"head": CAST + "k_head.png", "body": CAST + "k_body.png", "ref": CAST + "k_ref.png", "x": 1290, "label": "MASTER K"},
}
# global line index -> screen key (a list = pictures shown one after another within the line)
SCREEN_AT = {
    1: "three", 6: "firms7", 7: "banks", 10: "n25000", 12: "hana89", 15: "scan", 22: "ips", 25: "alert", 26: "alert", 28: "income", 32: "coupang",
    36: "launch", 38: "mach5", 40: "paths", 41: "paths", 42: "flight", 43: "flight", 46: "low", 47: "course", 48: "time", 52: "heat", 53: "plasma",
    55: "checks", 56: "flight", 59: "president", 61: "hyunmoo", 63: "kmbars", 67: "compare", 69: "scramjet", 70: "hycore_time",
    74: "y100", 76: ["haerye", "t1926"], 78: "gagya", 81: "tstatus", 83: ["sejong_poster", "n357"], 84: "n181", 86: ["speech", "ratio"], 88: "award_group",
    89: "scholar", 91: "pct534", 96: "study", 98: ["statue", "night"],
}


def build():
    lines = json.load(open(os.path.join(HERE, "audio", "lines_v2.json")))
    segments = []
    for (a, b), meta, guest in zip(SEG_EDGES, SEGS, GUESTS):
        chars = {**{k: dict(v) for k, v in BASE.items()}, "guest": {**guest, "x": SEAT["guest"]}}
        seg_lines, used = [], set()
        for l in [x for x in lines if a <= x["pos"] <= b]:
            who = WHO[l["who"]]
            ln = {"who": who, "text": l["text"], "audio": l["audio"]}
            key = SCREEN_AT.get(l["key"])
            if key:
                ln["shot"], ln["cam_id"] = "k_screen", f"screen_{who}"
                if who == "panel":
                    ln["side"] = "left"
                ln["push"], ln["screen"] = False, key
                used.update(key if isinstance(key, list) else [key])
            elif who == "guest":
                ln["shot"], ln["cam"], ln["ease"], ln["cam_id"], ln["push"] = "cam", [SEAT["guest"], 470, 1.30], 0.12, "guest", False
            else:
                ln["shot"], ln["cam"], ln["ease"], ln["cam_id"], ln["push"] = "cam", [960, 500, 1.1], 0.14, "two", False
            seg_lines.append(ln)
        segments.append({**meta, "characters": chars, "screens": {k: SCREENS[k] for k in sorted(used)},
                         "short": False, "hook": meta["headline"], "name_chips": True, "lines": seg_lines})
    ep = {"episode": 6, "name": "render/ep06", "anchor": "anchor", "characters": {**BASE, "guest": {**GUESTS[0], "x": SEAT["guest"]}},
          "background": {"image": "../../assets/studio/seoul_dusk.jpg", "dim": 0.8, "blur": 1.5},
          "outro_ticker": "Stay curious. Keep your lenses clean.", "segments": segments}
    json.dump(ep, open(os.path.join(HERE, "ep06_episode.json"), "w"), ensure_ascii=False, indent=1)
    print(sum(len(s["lines"]) for s in segments), "lines in", len(segments), "segments; screens:", len({k for s in segments for k in s["screens"]}))


if __name__ == "__main__":
    build()
