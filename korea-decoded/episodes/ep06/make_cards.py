"""EP.6 photo cards (1920x1080 PNGs into assets/stock/ep06/cards/). Reuses the EP.4/EP.5 card layouts.

    cd episodes/ep06 && python3 make_cards.py
"""
import importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mc5", os.path.join(HERE, "../ep05/make_cards.py"))
m5 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m5)
mc = m5.mc
mc.STOCK = os.path.join(HERE, "../../assets/stock/ep06")
mc.OUT = os.path.join(mc.STOCK, "cards")
from PIL import Image


def night_crop():  # the Gwanghwamun night photo is a tall portrait: keep a wide middle band
    im = Image.open(os.path.join(mc.STOCK, "gwanghwamun_night_98.jpg")).convert("RGB")
    w, h = im.size
    band = im.crop((0, int(h * 0.30), w, int(h * 0.30) + int(w * 9 / 16)))
    p = os.path.join(mc.STOCK, "gwanghwamun_night_wide.jpg"); band.save(p, quality=95)
    return mc.caption_card("gwanghwamun_night_wide.jpg", "GWANGHWAMUN SQUARE", "SEOUL AT NIGHT")


CARDS = {
    "haerye": lambda: mc.caption_card("hangul_haerye_76.jpg", "HUNMINJEONGEUM HAERYE", "THE 1446 TEXT ON HANGUL · A NATIONAL TREASURE"),
    "sejong_poster": lambda: mc.name_card("sejong_poster_83.jpg", "KING SEJONG INSTITUTE", "2026 INVITATION PROGRAM"),
    "speech": lambda: mc.caption_card("speech_finalist_88.jpg", "SPEAKING CONTEST FINALIST", "KING SEJONG INSTITUTE · 2026"),
    "award_group": lambda: mc.caption_card("award_group_88.jpg", "CONTEST WINNERS", "KING SEJONG INSTITUTE · 2026"),
    "scholar": lambda: mc.caption_card("scholar_robe_writing_89.jpg", "WRITING IN SCHOLAR ROBES", "A WRITING CONTEST FINALIST"),
    "statue": lambda: mc.caption_card("sejong_statue_98_cropped.jpg", "KING SEJONG THE GREAT", "GWANGHWAMUN, SEOUL"),
    "night": night_crop,
}

if __name__ == "__main__":
    os.makedirs(mc.OUT, exist_ok=True)
    for k, fn in CARDS.items():
        fn().save(os.path.join(mc.OUT, k + ".png")); print(k)
