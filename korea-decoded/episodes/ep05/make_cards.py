"""EP.5 event cards (1920x1080 PNGs into assets/stock/ep05/cards/, gitignored with the photos). Reuses the EP.4 card layouts.

    cd episodes/ep05 && python3 make_cards.py
"""
import importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mc4", os.path.join(HERE, "../ep04/make_cards.py"))
mc = importlib.util.module_from_spec(spec); spec.loader.exec_module(mc)
mc.STOCK = os.path.join(HERE, "../../assets/stock/ep05")
mc.OUT = os.path.join(mc.STOCK, "cards")

CARDS = {
    "jarasum_poster": lambda: mc.name_card("poster_jarasum.jpg", "JARASUM JAZZ", "THE 23RD · OCT 9-11"),
    "jarasum_autumn": lambda: mc.caption_card("jarasum_free_01.jpg", "GAPYEONG IN AUTUMN", "ABOUT 70 KM NORTHEAST OF SEOUL"),
    "biff_poster": lambda: mc.name_card("poster_biff.jpg", "BUSAN FILM FESTIVAL", "THE 31ST · OCT 6-15"),
    "biff_center": lambda: mc.caption_card("biff_free_07.jpg", "BUSAN CINEMA CENTER", "BUSAN INTERNATIONAL FILM FESTIVAL"),
    "biff_sign": lambda: mc.caption_card("biff_free_02.jpg", "BIFF AT THE CINEMA CENTER", "A SIGN FROM THE 2020 FESTIVAL"),
    "biff_building": lambda: mc.caption_card("biff_free_06.jpg", "THE RED CARPET ENTRANCE", "BUSAN CINEMA CENTER"),
    "drone_poster": lambda: mc.name_card("poster_drone_series.jpg", "HANGANG DRONE SHOW", "OCT 31 · TTUKSEOM PARK"),
    "drone_show": lambda: mc.caption_card("drone_free_01.jpg", "HANGANG DRONE LIGHT SHOW", "A 2025 SHOW OVER THE RIVER"),
    "drone_heart": lambda: mc.caption_card("drone_free_03.jpg", "1,500 DRONES, ONE SKY", "SEOUL MY SOUL"),
    "drone_roses": lambda: mc.caption_card("drone_free_06.jpg", "FREE TO WATCH", "BUT THE WEATHER GETS A VOTE"),
    "jamsu_night": lambda: mc.caption_card("jamsu_free_02.jpg", "JAMSU BRIDGE AT NIGHT", "CLOSED TO CARS ON SUNDAYS"),
    "jamsu_fountain": lambda: mc.caption_card("jamsu_free_04.jpg", "MOONLIGHT RAINBOW FOUNTAIN", "BANPO BRIDGE, SEOUL"),
    "jamsu_fountain2": lambda: mc.caption_card("jamsu_free_01.jpg", "WALKING THE BRIDGE", "NO CARS, JUST THE RIVER"),
}

if __name__ == "__main__":
    os.makedirs(mc.OUT, exist_ok=True)
    for k, fn in CARDS.items():
        fn().save(os.path.join(mc.OUT, k + ".png")); print(k)
