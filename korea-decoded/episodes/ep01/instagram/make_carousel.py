"""Instagram carousel (1080x1350 slides) for EP.1's shark story, from the episode's own pictures and numbers.

    cd episodes/ep01 && python3 instagram/make_carousel.py      # -> instagram/carousel_1.jpg ...
Facts match script.json (screens visitors / fifty / rescue); re-check the news before posting.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "prototypes"))
import newsrig as nr  # noqa: E402
import thumbnail as tb  # noqa: E402

CW, CH = 1080, 1350
M = 70  # side margin
BUKANG = "screens/bukang/"


def cover(path, w, h):
    img = Image.open(path).convert("RGB")
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0, y0 = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x0, y0, x0 + w, y0 + h))


def wrap(d, text, f, width):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            test = (cur + " " + word).strip()
            if d.textlength(test, font=f) <= width:
                cur = test
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def text_block(d, xy, text, size, fill=nr.WHITE, width=CW - 2 * M, spacing=1.18, stroke=0):
    f = nr.font(size)
    x, y = xy
    for ln in wrap(d, text, f, width):
        d.text((x, y), ln, font=f, fill=fill, stroke_width=stroke, stroke_fill=nr.BLACK)
        y += size * spacing
    return y


def frame(n, total, bg=None):
    """Navy slide (or a picture), logo top right, page counter top left."""
    img = Image.new("RGB", (CW, CH), nr.BRAND_NAVY) if bg is None else bg
    img = img.convert("RGBA")
    nr.logo_mark(img, CW - 70, 70, 70)
    d = ImageDraw.Draw(img)
    d.text((M, 70), f"{n}/{total}", font=nr.font(30), fill=(190, 200, 225), anchor="lm")
    return img, d


def credit(d, text, y=CH - 50):
    d.text((M, y), text, font=nr.font(24), fill=(190, 200, 225), anchor="lm")


def picture_card(img, path, box, tilt=-2):
    x, y, w, h = box
    card = tb.framed(path, w, h).rotate(tilt, expand=True, resample=Image.BICUBIC)
    tb.shadowed(img, card, (x, y))


def slides():
    total = 6
    out = []

    # 1. cover: the canal, headline at the bottom
    bg = ImageEnhance.Brightness(cover(BUKANG + "bukang_canal.png", CW, CH)).enhance(0.85)
    shade = Image.linear_gradient("L").resize((CW, CH)).point(lambda v: int(max(0, v - 90) * 1.5))
    bg = Image.composite(Image.new("RGB", (CW, CH), (0, 0, 0)), bg, shade)
    img, d = frame(1, total, bg)
    tb.shadowed(img, tb.badge("BUSAN, KOREA", 64), (M, 130), radius=8, offset=(4, 6))
    d = ImageDraw.Draw(img)
    y = text_block(d, (M, 1075), "A SHARK MOVED INTO\nA CITY CANAL.", 74, fill=nr.YELLOW, spacing=1.05, stroke=6)
    text_block(d, (M, y + 12), "It refused to leave.  Swipe  >", 48, stroke=4)
    credit(d, "AI-generated illustration", 225)
    out.append(img)

    # 2. arrival
    img, d = frame(2, total)
    d.text((M, 190), "SEPT. 18", font=nr.font(110), fill=nr.YELLOW, anchor="ls")
    picture_card(img, BUKANG + "requiem_shark_underwater.jpg", (M - 10, 250, 900, 560))
    d = ImageDraw.Draw(img)
    d.text((M + 20, 870), "FILE PHOTO", font=nr.font(26), fill=(190, 200, 225))
    text_block(d, (M, 950), "A 3.5-meter shark swims into a narrow canal at Busan's North Port.\nThen it just... stays.",
               52)
    credit(d, "Photo: laszlo-photo (CC BY 2.0)")
    out.append(img)

    # 3. the nickname
    img, d = frame(3, total)
    picture_card(img, BUKANG + "bukang_staycation.png", (M - 10, 150, 900, 560), tilt=2)
    tag = tb.name_tag("부캉이", "BUKANG-I", 110)
    tb.shadowed(img, tag, ((CW - tag.width) // 2, 700), radius=8, offset=(4, 6))
    d = ImageDraw.Draw(img)
    text_block(d, (M, 930), "Korea gave it a nickname within days:\nBukhang (\"North Port\") + \"-i\", "
               "the cute ending Koreans add to names.", 46)
    credit(d, "AI-generated illustration")
    out.append(img)

    # 4. the numbers
    img, d = frame(4, total)
    d.text((M, 200), "BY THE NUMBERS", font=nr.font(64), fill=nr.YELLOW, anchor="ls")
    stats = [("~600,000", "visitors, Sept. 18-28"), ("140,000", "in a single day over Chuseok"),
             ("~2,000", "on a normal holiday. Before the shark.")]
    y = 300
    for value, label in stats:
        d.text((M, y), value, font=nr.font(150), fill=nr.WHITE)
        d.text((M + 6, y + 185), label, font=nr.font(44), fill=(190, 200, 225))
        y += 310
    credit(d, "Source: Busan City; Busan Infrastructure Corp. via Yonhap")
    out.append(img)

    # 5. the rescue and the job
    img, d = frame(5, total)
    d.text((M, 200), "SEPT. 29: RESCUE ATTEMPT #1", font=nr.font(56), fill=nr.YELLOW, anchor="ls")
    for i, (value, label) in enumerate([("5", "boats with water cannons"), ("0", "sharks removed")]):
        y = 290 + i * 250
        d.text((M, y), value, font=nr.font(170), fill=nr.WHITE)
        d.text((M + 150, y + 95), label, font=nr.font(52), fill=nr.WHITE, anchor="lm")
    y = text_block(d, (M, 850), "So Busan made it an honorary ambassador.", 66, fill=nr.YELLOW, spacing=1.1)
    st = tb.stamp("REAL NEWS", 50)
    tb.shadowed(img, st, (CW - st.width - M + 20, 700), radius=6, offset=(3, 5))
    d = ImageDraw.Draw(img)
    text_block(d, (M, y + 30), "Next plan: a custom-made net.", 46, fill=(190, 200, 225))
    credit(d, "Source: Busan Coast Guard via Hankook Ilbo; Busan City")
    out.append(img)

    # 6. the show
    bg = tb.backdrop("../../assets/studio/seoul_dusk.jpg").resize((CW * 1350 // 720, CH))
    x0 = (bg.width - CW) // 2
    img, d = frame(6, total, bg.crop((x0, 0, x0 + CW, CH)))
    ep = json.load(open("script.json"))
    k = tb.character({**ep["characters"]["anchor"], "mouth": "mid", "gaze": (0.0, 0.0)})
    k = k.resize((760, round(k.height * 760 / k.width)), Image.LANCZOS)
    tb.shadowed(img, k, ((CW - k.width) // 2, CH - 560), radius=18, offset=(0, 0))
    d = ImageDraw.Draw(img)
    y = text_block(d, (M, 170), "The full story, animated.", 84, fill=nr.YELLOW, spacing=1.05, stroke=6)
    y = text_block(d, (M, y + 10), "Four Eyes Report on YouTube", 54, stroke=4)
    text_block(d, (M, y + 10), "Stay curious. Keep your lenses clean.", 40, fill=(220, 226, 240), stroke=3)
    out.append(img)
    return out


if __name__ == "__main__":
    for i, s in enumerate(slides(), 1):
        path = os.path.join(HERE, f"carousel_{i}.jpg")
        s.convert("RGB").save(path, quality=92)
        print(path)
