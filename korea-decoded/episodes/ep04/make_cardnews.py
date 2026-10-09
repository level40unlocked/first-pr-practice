"""EP.4 Instagram carousel (1080x1350, 9 slides): October K-pop comebacks, photo-first. English only.
    cd episodes/ep04 && python3 make_cardnews.py     # writes cardnews/slide_01..09.png and cardnews/caption.md
"""
import os, sys
sys.path.insert(0, "../../prototypes")
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import newsrig as nr
import thumbnail as tb

S = "../../assets/stock/ep04/"
W, H = 1080, 1350
PINK = (236, 72, 153)
NAVY, WHITE, YELLOW = nr.BRAND_NAVY, nr.WHITE, nr.YELLOW
OFFBEAT = {"head": "../../cast/kpop_head.png", "body": "../../cast/kpop_body.png", "ref": "../../cast/kpop_ref.png", "label": "OFFBEAT",
           "shoulders": 520, "white_lens": True, "mouth": "open", "gaze": [0.8, 0.0]}
N = 10


def backdrop(path):
    im = Image.open(path).convert("RGB")
    im = ImageOps.fit(im, (W, H), centering=(0.5, 0.3)).filter(ImageFilter.GaussianBlur(28))
    ov = Image.new("RGB", (W, H), NAVY)
    return Image.blend(im, ov, 0.78)


def framed(path, bw, bh, border=14, centering=(0.5, 0.25)):
    im = Image.open(path).convert("RGB")
    s = min(bw / im.width, bh / im.height)  # whole photo, never upscaled past its box
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    out = Image.new("RGB", (im.width + 2 * border, im.height + 2 * border), WHITE)
    out.paste(im, (border, border))
    return out


def shadow_paste(canvas, piece, xy, ang=0):
    p = piece.convert("RGBA")
    if ang: p = p.rotate(ang, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", p.size, (0, 0, 0, 150)), (xy[0] + 10, xy[1] + 14), p.getchannel("A"))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    canvas.alpha_composite(p, xy)
    return p.size


def chip(d, xy, text, fill, size=40, color=WHITE):
    f = nr.font(size); w = int(d.textlength(text, font=f)) + 44
    d.rounded_rectangle((xy[0], xy[1], xy[0] + w, xy[1] + size + 26), 18, fill=fill)
    d.text((xy[0] + 22, xy[1] + (size + 26) / 2), text, font=f, fill=color, anchor="lm")
    return w


def text_fit(d, xy, text, size, maxw, fill=WHITE, anchor="la", stroke=6):
    f = nr.font(size)
    while d.textlength(text, font=f) > maxw and size > 40:
        size -= 4; f = nr.font(size)
    d.text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=nr.BLACK)
    return size


def footer(canvas, n, credit=""):
    d = ImageDraw.Draw(canvas)
    d.rectangle((0, H - 84, W, H), fill=NAVY)
    d.rectangle((0, H - 84, W, H - 78), fill=YELLOW)
    d.text((40, H - 42), credit, font=nr.font(26), fill=(190, 200, 225), anchor="lm")
    d.text((W - 40, H - 42), f"@FourEyesReport   {n}/{N}", font=nr.font(28), fill=WHITE, anchor="rm")
    nr.logo_mark(canvas, W - 70, 70, 64)


def photo_slide(n, photo, date, name, release, credit, backdrop_photo=None, bw=860, bh=780, y0=150):
    canvas = backdrop(S + (backdrop_photo or photo)).convert("RGBA")
    d = ImageDraw.Draw(canvas)
    chip(d, (40, 40), "K-POP COMEBACKS · OCTOBER 2026", PINK, 30)
    f = framed(S + photo, bw, bh)
    x = (W - f.width) // 2; y = y0
    shadow_paste(canvas, f, (x, y), ang=-1.5)
    d = ImageDraw.Draw(canvas)
    chip(d, (x - 10, y - 18), date, YELLOW, 54, color=nr.BLACK)
    ty = y + f.height + 56
    text_fit(d, (W // 2, ty), name, 104, W - 100, anchor="ma")
    d.text((W // 2, ty + 128), release, font=nr.font(52), fill=YELLOW, anchor="ma", stroke_width=4, stroke_fill=nr.BLACK)
    footer(canvas, n, credit)
    return canvas.convert("RGB")


def cover():
    canvas = backdrop(S + "ive_poster.jpg").convert("RGBA")
    d = ImageDraw.Draw(canvas)
    chip(d, (40, 40), "FOUR EYES REPORT · K-CULTURE", PINK, 30)
    cards = [("recent_4.jpg", 380, 280, -6, (60, 150)), ("onew_zico.jpg", 360, 400, 5, (540, 120)),
             ("ive_poster.jpg", 330, 410, -4, (80, 470)), ("lisa.jpg", 280, 400, 6, (470, 540)),
             ("yuqi.jpg", 270, 390, -5, (780, 540))]
    for p, bw, bh, ang, xy in cards:
        shadow_paste(canvas, framed(S + p, bw, bh, 10), xy, ang)
    d = ImageDraw.Draw(canvas)
    d.rectangle((0, 930, W, H), fill=NAVY)
    d.rectangle((0, 930, W, 940), fill=YELLOW)
    text_fit(d, (W // 2, 975), "OCTOBER IS", 110, W - 80, anchor="ma")
    text_fit(d, (W // 2, 1095), "K-POP COMEBACK SEASON", 80, W - 80, fill=YELLOW, anchor="ma")
    d.text((W // 2, 1200), "52 releases in one month (one tracker's count)", font=nr.font(36), fill=(210, 218, 238), anchor="ma")
    d.text((W // 2, 1262), "SWIPE  >>>", font=nr.font(44), fill=WHITE, anchor="ma")
    ch = tb.character(OFFBEAT); s = 360 / ch.height
    ch = ch.resize((round(ch.width * s), round(ch.height * s)), Image.LANCZOS)
    canvas.alpha_composite(ch, (W - ch.width - 20, 930 - ch.height + 70))
    nr.logo_mark(canvas, W - 70, 70, 64)
    return canvas.convert("RGB")


def fin():
    canvas = backdrop(S + "recent_4.jpg").convert("RGBA")
    d = ImageDraw.Draw(canvas)
    chip(d, (40, 40), "THE BIG ONE", PINK, 30)
    f = framed(S + "recent_4.jpg", 900, 700)
    f = f.resize((900, round(f.height * 900 / f.width)), Image.LANCZOS)
    shadow_paste(canvas, f, ((W - f.width) // 2, 150), -1.5)
    d = ImageDraw.Draw(canvas)
    chip(d, (60, 130), "SEPT 21", YELLOW, 54, color=nr.BLACK)
    ty = 150 + f.height + 70
    text_fit(d, (W // 2, ty), "FIN.K.L IS BACK", 118, W - 80, anchor="ma")
    d.text((W // 2, ty + 138), "All four members. 21 years after their last single.", font=nr.font(46), fill=YELLOW, anchor="ma", stroke_width=4, stroke_fill=nr.BLACK)
    d.text((W // 2, ty + 214), "Two years of music, shows, and more.", font=nr.font(40), fill=WHITE, anchor="ma", stroke_width=3, stroke_fill=nr.BLACK)
    footer(canvas, 2, "")
    return canvas.convert("RGB")


def count():
    canvas = backdrop(S + "onew_zico.jpg").convert("RGBA")
    d = ImageDraw.Draw(canvas)
    chip(d, (40, 40), "K-POP COMEBACKS · OCTOBER 2026", PINK, 30)
    text_fit(d, (W // 2, 330), "52", 480, W - 80, fill=YELLOW, anchor="ma", stroke=10)
    text_fit(d, (W // 2, 840), "NEW RELEASES", 120, W - 80, anchor="ma")
    d.text((W // 2, 990), "in one month. That is more than one", font=nr.font(48), fill=WHITE, anchor="ma", stroke_width=3, stroke_fill=nr.BLACK)
    d.text((W // 2, 1054), "new K-pop release every single day.", font=nr.font(48), fill=WHITE, anchor="ma", stroke_width=3, stroke_fill=nr.BLACK)
    d.text((W // 2, 1150), "(one release tracker's count: albums, mini albums, EPs)", font=nr.font(32), fill=(190, 200, 225), anchor="ma")
    footer(canvas, 3, "Source: KpopComebacks, Oct 2026")
    return canvas.convert("RGB")


def ive_members():
    canvas = backdrop(S + "ive_poster.jpg").convert("RGBA")
    d = ImageDraw.Draw(canvas)
    chip(d, (40, 40), "K-POP COMEBACKS · OCTOBER 2026", PINK, 30)
    chip(d, (40, 128), "OCT 26", YELLOW, 54, color=nr.BLACK)
    members = [("ive_yujin.jpg", "AN YUJIN"), ("ive_5.jpg", "GAEUL"), ("ive_2.jpg", "REI"),
               ("ive_4.jpg", "JANG WONYOUNG"), ("ive_3.jpg", "LIZ"), ("ive_1.jpg", "LEESEO")]
    cw, ch_ = 290, 330
    for i, (p, name) in enumerate(members):
        c, r = i % 3, i // 3
        x, y = 40 + c * (cw + 30 + 12), 240 + r * (ch_ + 96)
        im = Image.open(S + p).convert("RGB")
        im = ImageOps.fit(im, (cw, ch_), centering=(0.5, 0.3)).convert("RGB")
        fr = Image.new("RGB", (cw + 16, ch_ + 16), WHITE); fr.paste(im, (8, 8))
        shadow_paste(canvas, fr, (x, y), (-2, 2, -1, 1, -2, 2)[i])
        d = ImageDraw.Draw(canvas)
        text_fit(d, (x + cw // 2 + 8, y + ch_ + 28), name, 36, cw, anchor="ma", stroke=3)
    d = ImageDraw.Draw(canvas)
    text_fit(d, (W // 2, 1085), "IVE", 100, W - 80, anchor="ma")
    d.text((W // 2, 1210), '"Looks Can Kill"  ·  pre-release Oct 19', font=nr.font(46), fill=YELLOW, anchor="ma", stroke_width=4, stroke_fill=nr.BLACK)
    footer(canvas, 9, "Images: Starship Entertainment")
    return canvas.convert("RGB")


def last():
    canvas = backdrop(S + "illit.jpg").convert("RGBA")
    d = ImageDraw.Draw(canvas)
    chip(d, (40, 40), "YOUR TURN", PINK, 30)
    text_fit(d, (W // 2, 230), "WHO ARE YOU", 120, W - 80, anchor="ma")
    text_fit(d, (W // 2, 370), "STREAMING FIRST?", 120, W - 80, fill=YELLOW, anchor="ma")
    d.text((W // 2, 560), "Tell us your pick in the comments.", font=nr.font(52), fill=WHITE, anchor="ma", stroke_width=4, stroke_fill=nr.BLACK)
    d.text((W // 2, 660), "Offbeat says he loves them all equally.", font=nr.font(40), fill=(210, 218, 238), anchor="ma")
    ch = tb.character(OFFBEAT); s = 560 / ch.height
    ch = ch.resize((round(ch.width * s), round(ch.height * s)), Image.LANCZOS)
    canvas.alpha_composite(ch, ((W - ch.width) // 2, H - 84 - ch.height + 120))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((120, 730, W - 120, 820), 26, fill=YELLOW)
    d.text((W // 2, 775), "Full episode on YouTube  (link in bio)", font=nr.font(40), fill=nr.BLACK, anchor="mm")
    footer(canvas, 10, "")
    return canvas.convert("RGB")


SLIDES = [
    cover,
    fin,
    count,
    lambda: photo_slide(4, "onew_zico.jpg", "OCT 7", "ONEW & ZICO", '"Tic Tac Toe"', "Photo: Griffin Entertainment"),
    lambda: photo_slide(5, "yuqi.jpg", "OCT 8", "YUQI (i-dle)", 'Mini album "27"', "Photo: Seoul Economic Daily", bw=620, bh=780),
    lambda: photo_slide(6, "sunghanbin.jpg", "OCT 12", "SUNG HAN-BIN", 'Solo EP "DEAD:ALIVE"', "Photo: Sports Chosun", bw=620, bh=780),
    lambda: photo_slide(7, "lisa.jpg", "OCT 23", "LISA", 'EP "PRESS PLAY"', "Photo: Ilgan Sports", bw=600, bh=780),
    lambda: photo_slide(8, "illit.jpg", "OCT 26", "ILLIT", '"BREAK EVEN"', "Image: courtesy of the agency", bw=900, bh=780, y0=290),
    ive_members,
    last,
]

if __name__ == "__main__":
    os.makedirs("cardnews", exist_ok=True)
    for i, fn in enumerate(SLIDES, 1):
        fn().save(f"cardnews/slide_{i:02d}.png"); print(i)
