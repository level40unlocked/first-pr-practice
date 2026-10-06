"""Builds the EP.4 photo cards (1920x1080 PNGs into assets/stock/ep04/cards/, gitignored with the photos).

    cd episodes/ep04 && python3 make_cards.py

A card = the brand-navy backdrop (the photo, blurred and dimmed) + the sharp photo in a white frame + big text.
Portrait photos sit on the left with the name on the right; wide photos sit centered with a caption bar.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../prototypes"))
import newsrig as nr

HERE = os.path.dirname(os.path.abspath(__file__))
STOCK = os.path.join(HERE, "../../assets/stock/ep04")
OUT = os.path.join(STOCK, "cards")
W, H = 1920, 1080


def backdrop(photo):
    bg = photo.copy()
    r = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * r) + 1, int(bg.height * r) + 1), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.35)
    navy = Image.new("RGB", (W, H), nr.BRAND_NAVY)
    return Image.blend(bg, navy, 0.45)


def framed(photo, box_w, box_h):
    r = min(box_w / photo.width, box_h / photo.height)
    p = photo.resize((int(photo.width * r), int(photo.height * r)), Image.LANCZOS)
    f = Image.new("RGB", (p.width + 24, p.height + 24), (255, 255, 255))
    f.paste(p, (12, 12))
    return f


def wrap_text(d, text, font, width):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else: out.append(cur); cur = w
    return out + [cur]


def name_card(photo_path, name, role, crop=None):
    photo = Image.open(os.path.join(STOCK, photo_path)).convert("RGB")
    if crop: photo = photo.crop(crop)
    img = backdrop(photo)
    f = framed(photo, 800, 940)
    img.paste(f, (140, (H - f.height) // 2))
    d = ImageDraw.Draw(img)
    x = 140 + f.width + 90
    d.rectangle((x, 380, x + 18, 700), fill=nr.YELLOW)
    nf = nr.font(112)
    while d.textlength(name, font=nf) > W - x - 50 - 190 and nf.size > 40: nf = nr.font(nf.size - 4)
    d.text((x + 50, 440), name, font=nf, fill=nr.WHITE, anchor="lm", stroke_width=4, stroke_fill=nr.BRAND_NAVY)
    for k, ln in enumerate(wrap_text(d, role, nr.font(54), W - x - 120)):
        d.text((x + 50, 560 + 66 * k), ln, font=nr.font(54), fill=nr.YELLOW, anchor="lm")
    return img


def caption_card(photo_path, big, small):
    photo = Image.open(os.path.join(STOCK, photo_path)).convert("RGB")
    img = backdrop(photo)
    f = framed(photo, 1700, 850)
    img.paste(f, ((W - f.width) // 2, 40))
    d = ImageDraw.Draw(img)
    d.rectangle((0, H - 160, W, H), fill=nr.BRAND_NAVY)
    d.rectangle((0, H - 160, W, H - 152), fill=nr.YELLOW)
    d.text((W / 2, H - 100), big, font=nr.font(72), fill=nr.WHITE, anchor="mm")
    d.text((W / 2, H - 42), small, font=nr.font(36), fill=nr.PALE if hasattr(nr, "PALE") else (190, 200, 225), anchor="mm")
    return img


CARDS = {
    "name_hyori": lambda: name_card("hyori_face_crop.png", "LEE HYORI", "SOLO SUPERSTAR AND VARIETY FAVORITE"),
    "name_ock": lambda: name_card("img_3.jpg", "OCK JOO-HYUN", "MUSICAL THEATER STAR"),
    "name_jin": lambda: name_card("img_1.jpg", "LEE JIN", "ACTRESS"),
    "name_yuri": lambda: name_card("img_2.jpg", "SUNG YURI", "DRAMA LEAD"),
    "debut_1998": lambda: caption_card("img_7.jpg", "1998: THE DEBUT", "FIN.K.L, FOUR MEMBERS, FIRST-GENERATION K-POP"),
    "cover_2005": lambda: caption_card("img_6.webp", "2005: \"FOREVER FIN.K.L\"", "THE LAST FULL-GROUP RELEASE"),
    "camping": lambda: caption_card("img_5.jpg", "CAMPING CLUB (JTBC, 2019)", "FOUR FRIENDS, ONE CAMPER VAN, ONE ROAD TRIP"),
    "c_onew_zico": lambda: name_card("onew_zico.jpg", "ONEW & ZICO", "\"TIC TAC TOE\" · OCT 7"),
    "c_yuqi": lambda: name_card("yuqi.jpg", "YUQI (I-DLE)", "MINI ALBUM \"27\" · OCT 8"),
    "c_hanbin": lambda: name_card("sunghanbin.jpg", "SUNG HAN-BIN", "SOLO EP \"DEAD:ALIVE\" · OCT 12"),
    "c_lisa": lambda: name_card("lisa.jpg", "LISA", "EP \"PRESS PLAY\" · OCT 23"),
    "c_illit": lambda: caption_card("illit.jpg", "ILLIT: \"BREAK EVEN\"", "OCT 26"),
    "c_ive": lambda: name_card("ive_poster.jpg", "IVE", "\"LOOKS CAN KILL\" · PRE-RELEASE OCT 19 · ALBUM OCT 26"),
    "recent": lambda: caption_card("recent_4.jpg", "SEPTEMBER 21, 2026", "ALL FOUR MEMBERS ANNOUNCED AS RETURNING"),
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k, fn in CARDS.items():
        fn().save(os.path.join(OUT, k + ".png")); print(k)
