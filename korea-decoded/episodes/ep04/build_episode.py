"""Builds ep04_episode.json (input of prototypes/render_episode.py) from audio/lines_v1.json and screens.py.

    cd episodes/ep04 && python3 build_episode.py && ./run_segments.sh 1 2

Two segments: 1 = Fin.K.L (lines 1-90), 2 = October comebacks (lines 101-162). Offbeat (the K-pop desk expert) is the guest of both.
Seats and shots as in EP.3: Master K 1290, Dr. Kangfree 630, the guest far right at 2560; a line with a screen uses "k_screen".
"""
import json
import os
from screens import SCREENS

HERE = os.path.dirname(os.path.abspath(__file__))
CAST = "../../cast/"
WHO = {"K": "anchor", "Kangfree": "panel", "Offbeat": "guest"}
SEAT = {"panel": 630, "anchor": 1290, "guest": 2560}
SEG_EDGES = [(1, 90), (101, 165)]
SEGS = [
    {"category": "kpop", "desk": "K-POP", "headline": "Fin.K.L is back after 21 years"},
    {"category": "kpop", "desk": "COMEBACKS", "headline": "October: a new K-pop release every day"},
]
OFFBEAT = {"head": CAST + "kpop_head.png", "body": CAST + "kpop_body.png", "ref": CAST + "kpop_ref.png", "label": "OFFBEAT", "shoulders": 520, "white_lens": True}
CHARACTERS = {
    "panel": {"head": CAST + "kangfree_head.png", "body": CAST + "kangfree_body.png", "ref": CAST + "kangfree_ref.png",
              "x": 630, "label": "DR. KANGFREE", "energy": 1.8, "head_ratio": 0.74, "shoulders": 500, "chin_drop": 0.12},
    "anchor": {"head": CAST + "k_head.png", "body": CAST + "k_body.png", "ref": CAST + "k_ref.png", "x": 1290, "label": "MASTER K"},
    "guest": {**OFFBEAT, "x": SEAT["guest"]},
}
# global line index -> screen key
SCREEN_AT = {
    2: "title", 11: "debut_1998", 12: "debut_1998",
    17: "name_hyori", 18: "name_hyori", 19: "name_ock", 20: "name_ock", 21: "name_ock", 22: "name_jin", 23: "name_jin", 24: "name_yuri", 25: "name_yuri",
    29: "recent", 30: "recent", 32: "cover_2005", 33: "years21", 38: "timeline", 39: "camping", 40: "camping", 41: "camping", 46: "plans", 47: "plans",
    110: "c_count", 111: "c_count", 112: "c_count",
    116: "c_onew_zico", 117: "c_onew_zico", 118: "c_onew_zico", 119: "c_onew_zico", 120: "c_onew_zico",
    121: "c_yuqi", 122: "c_yuqi", 123: "c_yuqi", 124: "c_yuqi", 129: "c_hanbin", 130: "c_hanbin", 134: "c_lisa", 135: "c_lisa",
    136: "c_illit", 137: "c_illit", 138: "c_illit", 139: "c_ive", 140: "c_ive", 141: "c_ive", 142: "c_ive",
}


def build():
    lines = json.load(open(os.path.join(HERE, "audio", "lines_v1.json")))
    segments = []
    for (a, b), meta in zip(SEG_EDGES, SEGS):
        seg_lines, used = [], set()
        seg_in = [x for x in lines if a <= x["index"] <= b]
        # runs of consecutive lines with the same picture: the box side is fixed per run (right if the guest speaks in it, else by who speaks first)
        side_of = {}
        i = 0
        while i < len(seg_in):
            key = SCREEN_AT.get(seg_in[i]["index"])
            if not key:
                i += 1
                continue
            j = i
            while j + 1 < len(seg_in) and SCREEN_AT.get(seg_in[j + 1]["index"]) == key:
                j += 1
            run = seg_in[i:j + 1]
            side = "right" if any(WHO[x["who"]] == "guest" for x in run) or WHO[run[0]["who"]] != "panel" else "left"
            for x in run:
                side_of[x["index"]] = side
            i = j + 1
        for l in seg_in:
            who = WHO[l["who"]]
            ln = {"who": who, "text": l["text"], "audio": f"audio/v1/ep04_{l['index']:03d}.mp3"}
            key = SCREEN_AT.get(l["index"])
            if key:
                # the speaker alone on the left, the box on the right (never a two-shot with a box); a speaker change = hard cut, box stays put
                ln["shot"], ln["cam_id"] = "k_screen", f"screen_{who}"
                if who == "panel":  # Kangfree sits on the left: she is framed on the right and the box goes to her left
                    ln["side"] = "left"
                ln["push"], ln["screen"] = False, key
                used.add(key)
            elif who == "guest":
                ln["shot"], ln["cam"], ln["ease"], ln["cam_id"], ln["push"] = "cam", [SEAT["guest"], 470, 1.30], 0.12, "guest", False
            else:
                ln["shot"], ln["cam"], ln["ease"], ln["cam_id"], ln["push"] = "cam", [960, 500, 1.1], 0.14, "two", False
            seg_lines.append(ln)
        segments.append({**meta, "characters": {k: dict(v) for k, v in CHARACTERS.items()}, "screens": {k: SCREENS[k] for k in sorted(used)},
                         "short": False, "hook": meta["headline"], "name_chips": True, "lines": seg_lines})
    ep = {"episode": 4, "name": "render/ep04", "anchor": "anchor", "characters": CHARACTERS,
          "background": {"image": "../../assets/studio/seoul_dusk.jpg", "dim": 0.8, "blur": 1.5},
          "outro_ticker": "Stay curious. Keep your lenses clean.", "segments": segments}
    json.dump(ep, open(os.path.join(HERE, "ep04_episode.json"), "w"), ensure_ascii=False, indent=1)
    print(sum(len(s["lines"]) for s in segments), "lines in", len(segments), "segments; screens:", len({k for s in segments for k in s["screens"]}))


if __name__ == "__main__":
    build()
