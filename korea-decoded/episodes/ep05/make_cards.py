"""EP.5 event cards (1920x1080 PNGs into assets/stock/ep05/cards/, gitignored with the photos). Reuses the EP.4 card layouts.

    cd episodes/ep05 && python3 make_cards.py
"""
import importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mc4", os.path.join(HERE, "../ep04/make_cards.py"))
mc = importlib.util.module_from_spec(spec); spec.loader.exec_module(mc)
mc.STOCK = os.path.join(HERE, "../../assets/stock/ep05")
mc.OUT = os.path.join(mc.STOCK, "cards")

from PIL import Image, ImageDraw


def framed_capped(photo, box_w, box_h):  # never blow a small photo up more than 3x
    r = min(box_w / photo.width, box_h / photo.height, 3.0)
    p = photo.resize((int(photo.width * r), int(photo.height * r)), Image.LANCZOS)
    f = Image.new("RGB", (p.width + 24, p.height + 24), (255, 255, 255)); f.paste(p, (12, 12))
    return f


def caption_card_safe(photo_path, big, small):  # same look, text block higher: the box zoom crops the bottom edge
    photo = Image.open(os.path.join(mc.STOCK, photo_path)).convert("RGB")
    img = mc.backdrop(photo)
    f = framed_capped(photo, 1700, 800)
    img.paste(f, ((mc.W - f.width) // 2, 40))
    d = ImageDraw.Draw(img)
    d.rectangle((0, mc.H - 215, mc.W, mc.H), fill=mc.nr.BRAND_NAVY)
    d.rectangle((0, mc.H - 215, mc.W, mc.H - 207), fill=mc.nr.YELLOW)
    d.text((mc.W / 2, mc.H - 150), big, font=mc.nr.font(72), fill=mc.nr.WHITE, anchor="mm")
    d.text((mc.W / 2, mc.H - 82), small, font=mc.nr.font(40), fill=(190, 200, 225), anchor="mm")
    return img


mc.framed = framed_capped
mc.caption_card = caption_card_safe

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
    "nate_smith": lambda: mc.caption_card("nate_smith.jpg", "NATE SMITH", "DRUMMER · TWO-TIME GRAMMY WINNER"),
    "michelle": lambda: mc.name_card("michelle.jpg", "MICHELLE YEOH", "ASIAN FILMMAKER OF THE YEAR"),
    "zhang": lambda: mc.name_card("zhang.jpg", "ZHANG YIMOU", "COMPETITION JURY PRESIDENT"),
    "turtle": lambda: mc.caption_card("turtle.jpg", "A SOFTSHELL TURTLE", "\"JARA\" IN JARASUM: A TURTLE ISLAND"),
    "france_flag": lambda: mc.name_card("france_flag.jpg", "FRANCE", "COUNTRY IN FOCUS · 140 YEARS OF TIES"),
    "rodriguez": lambda: mc.caption_card("rodriguez.jpg", "ALFREDO RODRIGUEZ", "CUBAN PIANIST · SATURDAY"),
    "hamasyan": lambda: mc.name_card("hamasyan.jpg", "TIGRAN HAMASYAN", "ARMENIAN PIANIST · CLOSING DAY"),
    "itx": lambda: mc.caption_card("itx.jpg", "ITX: YONGSAN TO GAPYEONG", "ABOUT 55 MINUTES"),
    "piff2007": lambda: mc.caption_card("piff2007.jpg", "PIFF, 2007", "THE 12TH EDITION, UNDER THE OLD NAME"),
    "biff1996": lambda: mc.caption_card("biff1996.jpg", "BUSAN, 1996: THE FIRST FESTIVAL", "173 FILMS FROM 31 COUNTRIES"),
    "bcc_night": lambda: mc.caption_card("bcc_night.jpg", "BUSAN CINEMA CENTER AT NIGHT", "THE FESTIVAL'S HOME SINCE 2011"),
    "seats2020": lambda: mc.caption_card("seats2020.jpg", "BIFF 2020: THE PANDEMIC EDITION", "192 FILMS · ABOUT 20,000 VIEWERS"),
    "biff2025": lambda: mc.caption_card("biff2025.jpg", "BIFF 2025: THE 30TH EDITION", "HELD IN SEPTEMBER"),
    "cuaron": lambda: mc.name_card("cuaron.jpg", "ALFONSO CUARON", "GUEST AT THE 31ST BIFF"),
    "ahn": lambda: mc.name_card("ahn.jpg", "AHN SUNG-KI", "TRIBUTE PROGRAM: SIX FILMS"),
    "outdoor": lambda: mc.caption_card("outdoor_theater.jpg", "THE OUTDOOR THEATER", "OPEN CINEMA SCREENINGS"),
    "ktx": lambda: mc.caption_card("ktx.jpg", "KTX: SEOUL TO BUSAN", "ABOUT TWO AND A HALF HOURS"),
    "jamsu_night": lambda: mc.caption_card("jamsu_free_02.jpg", "JAMSU BRIDGE AT NIGHT", "CLOSED TO CARS ON SUNDAYS"),
    "jamsu_fountain": lambda: mc.caption_card("jamsu_free_04.jpg", "MOONLIGHT RAINBOW FOUNTAIN", "BANPO BRIDGE, SEOUL"),
    "jamsu_fountain2": lambda: mc.caption_card("jamsu_free_01.jpg", "WALKING THE BRIDGE", "NO CARS, JUST THE RIVER"),
}

if __name__ == "__main__":
    os.makedirs(mc.OUT, exist_ok=True)
    for k, fn in CARDS.items():
        fn().save(os.path.join(mc.OUT, k + ".png")); print(k)
