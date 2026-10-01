"""Builds ep02_episode.json (input of prototypes/render_episode.py) from audio/lines_v5.json.

    cd episodes/ep02 && python3 build_episode.py && python3 ../../prototypes/render_episode.py ep02_episode.json --jobs 4

Four segments (the operator's drinking and bunsik segments first). Photos come from assets/stock/ep02 (CC BY 2.0,
credit lines from credits.json); the AI pictures are marked as such. Number cards show the statistics.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STOCK = "../../assets/stock/ep02/"
CAST = "../../cast/"
WHO = {"K": "anchor", "Kangfree": "panel", "Chef": "chef", "Clamsay": "chef"}
SEG_EDGES = [(1, 20), (21, 42), (43, 69), (70, 96)]  # line numbers (v5) per segment
SEGS = [
    {"category": "food_life", "desk": "DRINKING", "headline": "Korea's drinking culture is changing",
     "hook": "Korea used to drink like champions.\nNow?"},
    {"category": "food_life", "desk": "STREET FOOD", "headline": "Bunsik: the street snack that went global",
     "hook": "Koreans are shocked\nthis street food went global."},
    {"category": "hidden_korea", "desk": "YOUNG KOREA", "headline": "Young Koreans are bored (so they squeeze things)",
     "hook": "Korea has a word for\nwhen a hobby stops being fun."},
    {"category": "hidden_korea", "desk": "HOLIDAYS", "headline": "Chuseok is changing",
     "hook": "Fewer rites. More hotels.\nThe Chuseok shake-up."},
]


def photo(file, label):
    cr = {c["file"]: c for c in json.load(open(os.path.join(HERE, "../../assets/stock/ep02/credits.json")))}[file]
    return {"image": STOCK + file, "label": label, "credit": f"Photo: {cr['author']} ({cr['license']})"}


def ai(file, label):
    return {"image": STOCK + file, "label": label, "credit": "AI-generated illustration"}


def card(title, stats, credit):
    return {"card": {"title": title, "stats": stats}, "label": "", "credit": credit}


SCREENS = {
    "oecd": card("ALCOHOL PER PERSON: OECD RANK", [{"value": "10th", "label": "1981"}, {"value": "21st", "label": "2021"}],
                 "Source: OECD data, via Korean press reports"),
    "street": photo("street_food.jpg", "KOREAN STREET FOOD"),
    "kimbap": photo("kimbap_2.jpg", "KIMBAP"),
    "tteok_chilli": photo("rice_cake_chilli.jpg", "TTEOK ON A STICK"),
    "tteok_street": photo("tteokbokki_street.jpg", "TTEOKBOKKI"),
    "tteok_after": photo("tteokbokki_after.jpg", "TTEOKBOKKI"),
    "boredom": card("TREND KOREA 2027", [{"value": "BOREDOM", "label": "trend #1: \"the age of boredom\""}],
                    "Source: Seoul Economic Daily, 2026"),
    "squish_ai": ai("ai_squish.jpg", "MALLANG-I"),
    "squish": card("ONE MONTH, MID-2026", [{"value": 774, "suffix": "%", "label": "squishy toy sales"},
                                           {"value": 500, "suffix": "%", "label": "wax-crushing balls"}],
                   "Source: Korea Herald"),
    "tactile": card("TACTILE ITEMS", [{"value": 51.9, "decimals": 1, "suffix": "%",
                                       "label": "of Koreans aged 13-59 have tried them"}], "Source: Korea Herald"),
    "turtle_ai": ai("ai_turtle.jpg", "LUCKY TURTLES"),
    "run_ai": ai("ai_run.jpg", "MY PACE MORNING"),
    "rites": card("HOUSEHOLDS PLANNING ANCESTRAL RITES", [{"value": 74.4, "decimals": 1, "suffix": "%", "label": "2016"},
                                                         {"value": 27.3, "decimals": 1, "suffix": "%", "label": "2026"}],
                  "Source: Seoul Economic Daily, 2026"),
    "family": card("CHUSEOK 2026", [{"value": 43, "suffix": "%", "label": "family gathering only, no rites"}],
                   "Source: Seoul Economic Daily, 2026"),
    "hotel_ai": ai("ai_hotel.jpg", "HOTEL CHUSEOK"),
    "jeon": photo("pa_jeon.jpg", "JEON (PAN-FRIED PANCAKE)"),
}
# a line (found by the start of its text) -> screen key(s); a list switches inside the line
SCREEN_AT = {  # only the anchor presents pictures, so every key sits on a Master K line
    "But that's changing. In OECD data": "oecd",
    "Because bunsik is classic street food": ["street", "kimbap"],
    "Every corner. And it's cheap": "tteok_chilli",
    "So Koreans see a corner-stand snack": ["tteok_street", "tteok_after"],
    "A Seoul trend forecaster": "boredom",
    "They squeeze things": ["squish_ai", "squish"],
    "About half of the people surveyed": "tactile",
    "Tiny turtles": "turtle_ai",
    "True. Seoul held a run": "run_ai",
    "Less and less. In 2016": "rites",
    "And forty-three percent": "family",
    "Because the stress isn't the food": "hotel_ai",
    "Jeon. Pan-fried treats": "jeon",
}
# Seats (scene x): about 1000 px between neighbours, so a close-up (+-740 px) never catches the next person: Dr. Kangfree
# is centered when she is alone in frame, the explainer-screen view (Master K and the screen, zoom 1.5, ends at
# K+990) never shows the chef, and the chef's close-up never shows Master K.
SEAT_HOSTS = {"panel": 330, "anchor": 900}
SEAT_CHEF = {"panel": -350, "anchor": 650, "chef": 2080}
CHARACTERS = {
    "panel": {"head": CAST + "kangfree_head.png", "body": CAST + "kangfree_body.png", "ref": CAST + "kangfree_ref.png",
              "x": 330, "label": "DR. KANGFREE", "energy": 1.8, "head_ratio": 0.74, "shoulders": 500, "chin_drop": 0.12},
    "chef": {"head": CAST + "chef_head.png", "body": CAST + "chef_body.png", "ref": CAST + "chef_ref.png",
             "x": 1560, "label": "CHEF CLAMSAY", "shoulders": 520, "white_lens": True, "head_ratio": 0.74,
             "chin_drop": 0.16, "mood": "frown"},
    "anchor": {"head": CAST + "k_head.png", "body": CAST + "k_body.png", "ref": CAST + "k_ref.png",
               "x": 900, "label": "MASTER K"},
}


def seats_for(has_chef):
    return SEAT_CHEF  # same seats in every segment so nobody jumps at a cut (the chef's seat stays empty when he is absent)


def screen_for(text):
    for start, key in SCREEN_AT.items():
        if text.startswith(start):
            return key
    return None


def build():
    lines = json.load(open(os.path.join(HERE, "audio", "lines_v5.json")))
    segments = []
    for (a, b), meta in zip(SEG_EDGES, SEGS):
        seg_lines, prev_key = [], None
        seg_in = [x for x in lines if a <= x["index"] <= b]
        has_chef = any(WHO[x["who"]] == "chef" for x in seg_in)
        SEAT = seats_for(has_chef)
        PAIR = ((SEAT["panel"] + SEAT["anchor"]) // 2, 500, 1.22)
        chars = {k: {**CHARACTERS[k], "x": SEAT[k]} for k in ("anchor", "panel", "chef")
                 if k in ("anchor", "panel") or has_chef}
        for l in seg_in:
            who = WHO[l["who"]]
            ln = {"who": who, "text": l["text"], "audio": f"audio/v5/ep02_{l['index']:02d}.mp3"}
            key = screen_for(l["text"])
            assert not key or who == "anchor", f"line {l['index']}: a picture on a non-anchor line"
            if key:
                ln["shot"] = "k_screen"  # Master K and the screen, nobody else in frame
                ln["screen"] = key
                if isinstance(key, list):
                    ln["screen_split"] = [0.45]
            else:
                cx = SEAT[who]
                zoom = 1.30 + (0.06 if l["index"] % 3 == 0 else 0.0)
                if prev_key is None and not seg_lines and who != "chef":  # open on the two hosts (unless the chef speaks first)
                    ln["shot"], ln["cam"], ln["ease"] = "cam", list(PAIR), 0.14
                else:
                    ln["shot"], ln["cam"], ln["ease"] = "cam", [cx, 470, round(zoom, 2)], 0.12
            seg_lines.append(ln)
            prev_key = key
        # a screen needs its own screens dict entry
        used = set()
        for ln in seg_lines:
            if ln.get("screen"):
                used.update(ln["screen"] if isinstance(ln["screen"], list) else [ln["screen"]])
        segments.append({**meta, "characters": chars, "screens": {k: SCREENS[k] for k in sorted(used)}, "short": False, "name_chips": True, "lines": seg_lines})
    ep = {"episode": 2, "name": "render/ep02", "anchor": "anchor", "characters": CHARACTERS,
          "background": {"image": "../../assets/studio/seoul_dusk.jpg", "dim": 0.8, "blur": 1.5},
          "outro_ticker": "Stay curious. Keep your lenses clean.", "segments": segments}
    json.dump(ep, open(os.path.join(HERE, "ep02_episode.json"), "w"), ensure_ascii=False, indent=1)
    print(sum(len(s["lines"]) for s in segments), "lines in", len(segments), "segments;",
          "screens:", sorted({k for s in segments for k in s["screens"]}))


if __name__ == "__main__":
    build()
