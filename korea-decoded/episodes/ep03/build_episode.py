"""Builds ep03_episode.json (input of prototypes/render_episode.py) from audio/lines_v1.json and script_data.py.

    cd episodes/ep03 && python3 build_episode.py && ./run_segments.sh 1 2 3 4 5 6 7

Seats (scene x): Master K 1290 and Dr. Kangfree 630 sit close (the EP.1 two-person look); the one guest of a segment sits far
right at 2560. K <-> Kangfree stays on one static two-shot; a guest or an explainer screen is a hard cut (cam_id changes).
A line that has a graphic gets the "k_screen" shot: its speaker on the left, the graphic on the right.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CAST = "../../cast/"
STOCK = "../../assets/stock/ep03/"
WHO = {"K": "anchor", "Kangfree": "panel", "Nonfic": "guest", "Indoor": "guest", "Rise": "guest", "Hidden": "guest"}
SEAT = {"panel": 630, "anchor": 1290, "guest": 2560}
GUEST_OF = {1: "Nonfic", 2: "Indoor", 3: "Rise", 4: "Hidden", 5: "Nonfic", 6: "Nonfic", 7: None}
SEG_EDGES = [(1, 23), (24, 39), (40, 55), (56, 72), (73, 81), (82, 94), (95, 98)]
SEGS = [
    {"category": "current_affairs", "desk": "VISITORS", "headline": "Seoul fever: a record year for visitors"},
    {"category": "travel", "desk": "TRAVEL", "headline": "What to see in Seoul right now"},
    {"category": "money_business", "desk": "EXPORTS", "headline": "Korea's exports just hit a record"},
    {"category": "hidden_korea", "desk": "HANGUL", "headline": "A holiday for an alphabet: Hangul Day"},
    {"category": "current_affairs", "desk": "IS THIS NORMAL?", "headline": "Is this normal in Korea? Ppalli-ppalli"},
    {"category": "current_affairs", "desk": "LANGUAGE", "headline": "Why Koreans ask your age"},
    {"category": "current_affairs", "desk": "K'S TAKE", "headline": "K's Take: the world is showing up"},
]
GUEST = {
    "Nonfic": {"head": CAST + "news_head.png", "body": CAST + "news_body.png", "ref": CAST + "news_ref.png", "label": "MS. NONFIC", "shoulders": 520, "white_lens": True},
    "Indoor": {"head": CAST + "travel_head.png", "body": CAST + "travel_body.png", "ref": CAST + "travel_ref.png", "label": "PROF. INDOOR", "shoulders": 520, "white_lens": True},
    "Rise": {"head": CAST + "money_head.png", "body": CAST + "money_body.png", "ref": CAST + "money_ref.png", "label": "MAX RISE", "shoulders": 520, "head_ratio": 0.68, "white_lens": True},
    "Hidden": {"head": CAST + "hidden_head.png", "body": CAST + "hidden_body.png", "ref": CAST + "hidden_ref.png", "label": "DR. H", "shoulders": 520, "white_lens": True, "chin_drop": 0.10},
}
CHARACTERS = {
    "panel": {"head": CAST + "kangfree_head.png", "body": CAST + "kangfree_body.png", "ref": CAST + "kangfree_ref.png",
              "x": 630, "label": "DR. KANGFREE", "energy": 1.8, "head_ratio": 0.74, "shoulders": 500, "chin_drop": 0.12},
    "anchor": {"head": CAST + "k_head.png", "body": CAST + "k_body.png", "ref": CAST + "k_ref.png", "x": 1290, "label": "MASTER K"},
}


def photo(file, label, credit_extra=""):
    cr = {c["file"]: c for c in json.load(open(os.path.join(HERE, "../../assets/stock/ep03/credits.json")))}[file]
    return {"image": STOCK + file, "label": label, "credit": f"Photo: {cr['author']} ({cr['license']}){credit_extra}"}


def chart(spec, credit="", label=""):
    return {"chart": spec, "label": label, "credit": credit}


SRC_SED = "Source: Seoul Economic Daily"
SCREENS = {
    "open_count": {"card": {"title": "FOREIGN VISITORS, JAN–AUG 2026", "stats": [{"value": 15.05, "decimals": 2, "suffix": " MILLION", "label": "a record"}]}, "label": "", "credit": "Source: Korea JoongAng Daily, Seoul Economic Daily"},
    "fever": chart({"type": "bigtext", "lines": ["SEOUL", "FEVER"], "thermo": True}),
    "vs_penn": chart({"type": "bars", "title": "FOREIGN VISITORS (MILLIONS)", "bars": [{"label": "Pennsylvania (people)", "value": 13.0, "text": "≈13M"}, {"label": "Korea visitors, Jan–Aug", "value": 15.05, "hl": True, "text": "15.05M"}], "suffix": "M", "decimals": 2},
                     "Source: Korea JoongAng Daily; U.S. Census Bureau"),
    "august": {"card": {"title": "AUGUST 2026", "stats": [{"value": 2.25, "decimals": 2, "suffix": " MILLION", "label": "visitors in one month: a record"}]}, "label": "", "credit": SRC_SED + ", Sep 28, 2026"},
    "fevers": chart({"type": "bigtext", "lines": ["SEOUL FEVER", "BUSAN FEVER"], "size": 90}),
    "repeat": chart({"type": "bigtext", "lines": ["REPEAT", "CUSTOMERS"]}),
    "puns": chart({"type": "words", "title": "DR. KANGFREE'S LIST", "words": ["SEOUL-SEARCHING", "SEOUL FOOD", "SEOUL MATE"]}),
    "rank": chart({"type": "hbars", "title": "ASIA'S MOST REVISITED CITIES, H1 2026", "bars": [{"label": "1 Tokyo", "value": 10}, {"label": "2 Bangkok", "value": 9}, {"label": "3 Bali", "value": 8}, {"label": "4 Seoul", "value": 7, "hl": True}, {"label": "5 Osaka", "value": 6}]},
                  "Source: Agoda booking data, via Korea Herald"),
    "why": chart({"type": "icons", "title": "WHY PEOPLE COME BACK", "items": [["🎤", "K-content"], ["🎪", "Festivals"], ["🍜", "Food"], ["💄", "Beauty"], ["🛍️", "Shopping"], ["🏪", "24h stores"]]}, "Source: Korea Herald"),
    "welcome": chart({"type": "bigtext", "lines": ["SEOUL", "WELCOME WEEK"], "sub": "Sep 19 – Oct 11", "size": 90}, "Source: Seoul Metropolitan Government"),
    "myeongdong": photo("myeongdong.jpg", "MYEONGDONG"),
    "palaces": photo("palace.jpg", "ROYAL PALACES"),
    "palaces2": photo("palace2.jpg", "GYEONGBOKGUNG"),
    "moonlight": chart({"type": "bigtext", "lines": ["MOONLIGHT TOUR", "ENGLISH SESSIONS"], "size": 80}, "Source: Seoul tourism notices"),
    "cap": {"card": {"title": "SEOUL SOUVENIR CAP", "stats": [{"value": 2.7, "decimals": 1, "suffix": "M", "label": "views on Japanese social media"}, {"value": "NO ADS", "label": ""}]}, "label": "", "credit": "Source: Korea Times, Sep 23, 2026"},
    "exports": chart({"type": "bars", "title": "KOREA'S EXPORTS ($ BILLION)", "bars": [{"label": "Sep 2025", "value": 65.95}, {"label": "Sep 2026", "value": 120.94, "hl": True}], "prefix": "$", "suffix": "B", "decimals": 1, "badge": "+83.5%"}, SRC_SED + ", Oct 1, 2026"),
    "chips": chart({"type": "donut", "title": "CHIPS: SHARE OF EXPORTS, SEP 2026", "value": 49.9, "center": "49.9%", "label": "ALMOST HALF", "legend": "$60.3B of $120.9B  (+263%)"}, SRC_SED + ", Oct 1, 2026"),
    "datacenter": photo("datacenter.jpg", "DATA CENTER (ILLUSTRATIVE)"),
    "ytd": chart({"type": "bars", "title": "EXPORTS ($ BILLION)", "bars": [{"label": "All of 2025", "value": 709.3}, {"label": "Jan–Sep 2026", "value": 814.5, "hl": True}], "prefix": "$", "suffix": "B", "decimals": 1}, SRC_SED + ", Oct 1, 2026"),
    "trillion": chart({"type": "bigtext", "lines": ["$1 TRILLION", "NEXT?"], "size": 100}),
    "hangul_day": chart({"type": "bigtext", "lines": ["HANGUL DAY", "OCT 9"], "size": 100}),
    "day_off": chart({"type": "bigtext", "lines": ["A DAY OFF FOR", "A WRITING SYSTEM"], "size": 80}),
    "hanja": chart({"type": "bigtext", "lines": ["CHINESE CHARACTERS", "YEARS TO LEARN"], "size": 80}),
    "sejong": photo("sejong_statue.jpg", "KING SEJONG THE GREAT"),
    "t1446": chart({"type": "timeline", "title": "HANGUL", "events": [{"year": "1446", "label": "created", "hl": True}, {"year": "2026", "label": "580 years later"}]}),
    "letters": chart({"type": "letters", "title": "HANGUL COPIES THE MOUTH", "items": [["ㄱ", "back of the tongue"], ["ㄴ", "tongue tip"], ["ㅁ", "the lips"]]}),
    "patch": chart({"type": "bigtext", "lines": ["580 YEARS", "0 PATCH NOTES"], "size": 90}),
    "twenty4": {"card": {"title": "HANGUL TODAY", "stats": [{"value": 14, "label": "consonants"}, {"value": 10, "label": "vowels"}, {"value": 24, "label": "letters in all"}]}, "label": "", "credit": ""},
    "kangfree_name": chart({"type": "bigtext", "lines": ["강프리"], "hangul": True, "size": 150}),
    "normal_q": chart({"type": "bigtext", "lines": ["IS THIS NORMAL", "IN KOREA?"], "size": 90}),
    "exhibit": chart({"type": "bigtext", "lines": ["EXHIBIT A:", "THE SIDEWALK"], "size": 90}),
    "ppalli": chart({"type": "bigtext", "lines": ["PPALLI-PPALLI", "= HURRY, HURRY"], "size": 90}),
    "os": chart({"type": "icons", "cols": 2, "title": "SPEED, KOREAN STYLE", "items": [["⏱️", "Food in minutes"], ["🛗", "Close button first"]]}),
    "normal": chart({"type": "bigtext", "lines": ["NORMAL"], "size": 130, "color": [80, 220, 120]}),
    "how_old": chart({"type": "bigtext", "lines": ["HOW OLD", "ARE YOU?"], "size": 110}),
    "levels": chart({"type": "steps", "title": "KOREAN SPEECH LEVELS", "items": ["Casual", "Polite", "Formal"], "caption": "pick one by who is older"}),
    "kage": chart({"type": "timeline", "title": "KOREAN AGE (UNTIL 2023)", "events": [{"year": "DEC 31", "label": "born: age 1"}, {"year": "JAN 1", "label": "age 2", "hl": True}]}),
    "june23": chart({"type": "bigtext", "lines": ["JUNE 2023", "INTERNATIONAL AGE"], "size": 90}),
    "anti": chart({"type": "bigtext", "lines": ["ANTI-AGING", "TREATMENT:", "LEGISLATION"], "size": 80}),
    "our": chart({"type": "words", "title": "KOREANS SAY…", "words": ["our mom", "our house", "our school", "our wife"]}),
}
# line number -> screen key (or list of keys with an optional split)
SCREEN_AT = {
    1: "open_count", 3: "fever", 7: "vs_penn", 9: "august", 11: "fevers", 12: "repeat", 15: "puns", 16: "rank", 18: "rank", 20: "why",
    28: ["welcome", "myeongdong"], 30: ["palaces", "palaces2"], 31: "moonlight", 35: ["cap"],
    42: "exports", 44: "chips", 48: "datacenter", 50: ["ytd", "trillion"],
    56: "hangul_day", 59: "day_off", 63: "hanja", 64: ["sejong", "t1446"], 65: "letters", 67: "patch", 68: "twenty4", 71: "kangfree_name",
    73: "normal_q", 74: "exhibit", 75: "ppalli", 76: "os", 80: "normal",
    83: "how_old", 85: "levels", 86: "kage", 88: "june23", 89: "anti", 91: "our",
}


def build():
    lines = json.load(open(os.path.join(HERE, "audio", "lines_v1.json")))
    segments = []
    for n, ((a, b), meta) in enumerate(zip(SEG_EDGES, SEGS), 1):
        guest_name = GUEST_OF[n]
        chars = {k: dict(v) for k, v in CHARACTERS.items()}
        if guest_name:
            chars["guest"] = {**GUEST[guest_name], "x": SEAT["guest"]}
        seg_lines, used = [], set()
        for l in [x for x in lines if a <= x["index"] <= b]:
            who = WHO[l["who"]]
            ln = {"who": who, "text": l["text"], "audio": f"audio/v1/ep03_{l['index']:02d}.mp3"}
            key = SCREEN_AT.get(l["index"])
            if key:
                ln["shot"], ln["cam_id"], ln["push"] = "k_screen", f"screen_{who}", False
                ln["screen"] = key
                if isinstance(key, list) and len(key) > 1:
                    ln["screen_split"] = [0.5]
            elif who == "guest":
                ln["shot"], ln["cam"], ln["ease"], ln["cam_id"], ln["push"] = "cam", [SEAT["guest"], 470, 1.30], 0.12, "guest", False
            else:
                ln["shot"], ln["cam"], ln["ease"], ln["cam_id"], ln["push"] = "cam", [960, 500, 1.1], 0.14, "two", False
            if key:
                used.update(key if isinstance(key, list) else [key])
            seg_lines.append(ln)
        segments.append({**meta, "characters": chars, "screens": {k: SCREENS[k] for k in sorted(used)}, "short": False, "hook": meta["headline"],
                         "name_chips": True, "lines": seg_lines})
    ep = {"episode": 3, "name": "render/ep03", "anchor": "anchor",
          "characters": {**CHARACTERS, "guest": {**GUEST["Nonfic"], "x": SEAT["guest"]}},
          "background": {"image": "../../assets/studio/seoul_dusk.jpg", "dim": 0.8, "blur": 1.5},
          "outro_ticker": "Stay curious. Keep your lenses clean.", "segments": segments}
    json.dump(ep, open(os.path.join(HERE, "ep03_episode.json"), "w"), ensure_ascii=False, indent=1)
    print(sum(len(s["lines"]) for s in segments), "lines in", len(segments), "segments; screens:", len({k for s in segments for k in s["screens"]}))


if __name__ == "__main__":
    build()
