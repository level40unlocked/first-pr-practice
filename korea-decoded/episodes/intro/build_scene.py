"""Builds intro_scene.json (input of prototypes/episode.py) for the channel intro reel from script.md's lines.

    cd episodes/intro && python3 build_scene.py && python3 ../../prototypes/episode.py intro_scene.json

Cut B (2026-09-30): lines 4, 16 and 21 of the 22 recorded are dropped (~10 s shorter). Word timings come from
audio/asr_words.json (faster-whisper on the generated voices), spelled like the script.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CUT = {4, 16, 21}

# (number in script.md, who, text)
LINES = [
    (1, "anchor", "Hello, world. I'm Master K, and this is the Four Eyes Report: Korea's stories, decoded for everyone who isn't in Korea."),
    (2, "panel", "I'm Dr. Kangfree, the co-host! I LOVE Korean food, so today we have a very special guest: Chef Garden Clamsay!"),
    (3, "chef", "Thanks for having me. Korean food is spicy."),
    (4, "panel", "Cry-your-eyes-out spicy! I love it!"),
    (5, "chef", "Koreans are obsessed with spicy."),
    (6, "anchor", "Technically, most Korean food isn't spicy."),
    (7, "chef", "Then explain last night. Three of us boiled fire noodles."),
    (8, "anchor", "And?"),
    (9, "chef", "One of us died. Nobody noticed for an hour."),
    (10, "panel", "WHAT?!"),
    (11, "chef", "So I looked it up. Koreans say, \"Two people eat, one drops dead, the other won't notice.\""),
    (12, "anchor", "It's a compliment. It means the food is that good."),
    (13, "chef", "Then it was the best noodles of my life."),
    (14, "panel", "Wait. WAIT. Who died?!"),
    (15, "chef", "...Great question."),
    (16, "anchor", "Noted. Korean food comes with a warning label."),
    (17, "panel", "And Korea has a lot of hot news!"),
    (18, "anchor", "Maybe the three of us aren't enough. We explain Korea's news and culture, with charts."),
    (19, "panel", "Curious about the rest of the desk?"),
    (20, "anchor", "Then visit our YouTube channel. New episodes every Friday."),
    (21, "panel", "Or whenever you suddenly miss us!"),
    (22, "anchor", "Stay curious. Keep your lenses clean."),
]
STILL_LINES = {1, 19, 20, 22}  # over the picture of the whole cast
# name tags that pop onto the cast picture during line 19 (x, y = share of the picture)
TAGS = [("PROF. INDOOR", 0.085, 0.50), ("BILL DUSK", 0.178, 0.56), ("MAX RISE", 0.275, 0.50),
        ("MS. NONFIC", 0.36, 0.56), ("DR. H", 0.42, 0.50), ("WHISTLE JOE", 0.70, 0.56), ("OFFBEAT", 0.91, 0.50)]

CAST = "../../cast/"
CHARACTERS = {
    "panel": {"head": CAST + "kangfree_head.png", "body": CAST + "kangfree_body.png", "ref": CAST + "kangfree_ref.png",
              "x": 520, "label": "DR. KANGFREE", "energy": 1.8, "head_ratio": 0.74, "shoulders": 500, "chin_drop": 0.12},
    "chef": {"head": CAST + "chef_head.png", "body": CAST + "chef_body.png", "ref": CAST + "chef_ref.png",
             "x": 960, "label": "CHEF CLAMSAY", "shoulders": 520, "white_lens": True, "head_ratio": 0.74,
             "chin_drop": 0.16, "mood": "frown"},
    "anchor": {"head": CAST + "k_head.png", "body": CAST + "k_body.png", "ref": CAST + "k_ref.png",
               "x": 1400, "label": "MASTER K"},
}


def build():
    asr = json.load(open(os.path.join(HERE, "audio", "asr_words.json")))
    lines = []
    for n, who, text in LINES:
        if n in CUT:
            continue
        ln = {"who": who, "text": text, "audio": f"audio/intro_{n:02d}.mp3",
              "words": asr[str(n)]["words"]}
        if n in STILL_LINES:
            ln["shot"] = "still"
        if n == 13:
            ln["mood"] = {"chef": "neutral"}  # the noodles win him over, for one line
        if n == 19:
            ln["tags"] = [{"text": t, "x": x, "y": y, "at": 0.15 + 0.3 * i} for i, (t, x, y) in enumerate(TAGS)]
        lines.append(ln)
    scene = {
        "episode": "INTRO", "anchor": "anchor", "category": "food_life", "desk": "MEET THE CREW",
        "headline": "Meet the Four Eyes Report crew",
        "hook": "Korean food is spicy.\nOne of us died.",
        "characters": CHARACTERS,
        "background": {"image": "../../assets/studio/seoul_dusk.jpg", "dim": 0.8, "blur": 1.5},
        "still": "../../assets/group/cast_debate.jpg", "still_credit": "AI-generated illustration",
        "end_card": {"title": "FOLLOW FOR MORE", "line": "New episodes every Friday on YouTube"},
        "full_episode_where": "on YouTube",
        "up_next": ["Stay curious. Keep your lenses clean."],
        "lines": lines,
        "out_long": "render/intro_long.mp4", "out_short": "render/intro_reel.mp4",
    }
    json.dump(scene, open(os.path.join(HERE, "intro_scene.json"), "w"), ensure_ascii=False, indent=1)
    print(len(lines), "lines")


if __name__ == "__main__":
    build()
