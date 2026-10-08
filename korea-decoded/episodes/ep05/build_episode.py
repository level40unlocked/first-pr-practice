"""Builds ep05_episode.json (input of prototypes/render_episode.py) from audio/lines_v1.json and screens.py.

    cd episodes/ep05 && python3 build_episode.py && ./run_segments.sh 1 2

Two segments: 1 = Jarasum Jazz Festival (lines 1-33, with the intro), 2 = Busan International Film Festival (34-64). Guest: Professor Indoor.
Photo/graphic lines use "k_screen" (speaker on the left, picture on the right); a speaker change is a hard cut, the picture stays put.
"""
import json
import os
from screens import SCREENS

HERE = os.path.dirname(os.path.abspath(__file__))
CAST = "../../cast/"
WHO = {"K": "anchor", "Kangfree": "panel", "Indoor": "guest"}
SEAT = {"panel": 630, "anchor": 1290, "guest": 2560}
SEG_EDGES = [(1, 33), (34, 64)]
SEGS = [
    {"category": "travel", "desk": "TRAVEL", "headline": "Jarasum Jazz Festival: jazz on Turtle Island"},
    {"category": "travel", "desk": "TRAVEL", "headline": "Busan International Film Festival: 31st edition"},
]
INDOOR = {"head": CAST + "travel_head.png", "body": CAST + "travel_body.png", "ref": CAST + "travel_ref.png", "label": "PROF. INDOOR", "shoulders": 520, "white_lens": True}
CHARACTERS = {
    "panel": {"head": CAST + "kangfree_head.png", "body": CAST + "kangfree_body.png", "ref": CAST + "kangfree_ref.png",
              "x": 630, "label": "DR. KANGFREE", "energy": 1.8, "head_ratio": 0.74, "shoulders": 500, "chin_drop": 0.12},
    "anchor": {"head": CAST + "k_head.png", "body": CAST + "k_body.png", "ref": CAST + "k_ref.png", "x": 1290, "label": "MASTER K"},
    "guest": {**INDOOR, "x": SEAT["guest"]},
}
# global line index -> screen key
SCREEN_AT = {
    1: "two_posters", 2: "two_posters",
    8: "gapyeong_river", 9: "turtle", 10: "turtle", 11: "turtle", 12: "gapyeong_dusk", 13: "gapyeong_dusk",
    14: "y2004", 15: "y2004", 16: "jarasum_time", 17: "jarasum_time", 18: "jarasum_time", 19: "france_flag", 20: "france_flag", 21: "france_flag",
    22: "jarasum_poster", 23: "jarasum_poster", 24: ["nate_smith", "years17"], 25: "years17", 26: ["rodriguez", "hamasyan"], 27: "hamasyan", 28: "itx", 29: "itx", 30: "kids",
    31: "gapyeong_grass", 32: "jarasum_autumn", 33: "jarasum_autumn",
    34: "biff_poster", 35: "biff_poster", 36: "piff2007", 37: "piff2007", 38: "biff1996", 39: "biff1996", 42: "biff_center", 43: "bcc_night",
    44: "biff_time", 45: "seats2020", 46: "biff2025", 47: "biff2025", 48: "films316", 49: "films316", 50: "michelle", 51: "michelle_prog", 52: "michelle_prog",
    53: ["zhang", "cuaron"], 54: "ahn", 55: "ahn", 56: "outdoor", 57: "outdoor", 58: "tickets", 59: "tickets", 60: "ktx", 61: "ktx",
}


def build():
    lines = json.load(open(os.path.join(HERE, "audio", "lines_v1.json")))
    segments = []
    for (a, b), meta in zip(SEG_EDGES, SEGS):
        seg_lines, used = [], set()
        seg_in = [x for x in lines if a <= x["index"] <= b and True]
        for l in seg_in:
            who = WHO[l["who"]]
            ln = {"who": who, "text": l["text"], "audio": f"audio/v1/ep05_{l['index']:03d}.mp3"}
            key = SCREEN_AT.get(l["index"])
            if key:
                # the speaker alone on the left, the box on the right (never a two-shot with a box); a speaker change = hard cut, box stays put
                ln["shot"], ln["cam_id"] = "k_screen", f"screen_{who}"
                if who == "panel":  # Kangfree sits on the left: she is framed on the right and the box goes to her left
                    ln["side"] = "left"
                ln["push"], ln["screen"] = False, key
                used.update(key if isinstance(key, list) else [key])
            elif who == "guest":
                ln["shot"], ln["cam"], ln["ease"], ln["cam_id"], ln["push"] = "cam", [SEAT["guest"], 470, 1.30], 0.12, "guest", False
            else:
                ln["shot"], ln["cam"], ln["ease"], ln["cam_id"], ln["push"] = "cam", [960, 500, 1.1], 0.14, "two", False
            seg_lines.append(ln)
        segments.append({**meta, "characters": {k: dict(v) for k, v in CHARACTERS.items()}, "screens": {k: SCREENS[k] for k in sorted(used)},
                         "short": False, "hook": meta["headline"], "name_chips": True, "lines": seg_lines})
    ep = {"episode": 5, "name": "render/ep05", "anchor": "anchor", "characters": CHARACTERS,
          "background": {"image": "../../assets/studio/seoul_dusk.jpg", "dim": 0.8, "blur": 1.5},
          "outro_ticker": "Stay curious. Keep your lenses clean.", "segments": segments}
    json.dump(ep, open(os.path.join(HERE, "ep05_episode.json"), "w"), ensure_ascii=False, indent=1)
    print(sum(len(s["lines"]) for s in segments), "lines in", len(segments), "segments; screens:", len({k for s in segments for k in s["screens"]}))


if __name__ == "__main__":
    build()
