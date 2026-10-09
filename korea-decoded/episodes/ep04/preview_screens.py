"""Renders every EP.4 screen as it looks in the explainer box (k_screen: box (880,210)-(1840,750) of the 1920x1080 frame).

    python3 preview_screens.py            -> render/screens/<key>.png + render/screens/_contact.png
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
sys.path.insert(0, os.path.join(HERE, "../../prototypes"))
from PIL import Image, ImageDraw
import episode as ep
import newsrig as nr
from screens import SCREENS

os.makedirs("render/screens", exist_ok=True)
bg = Image.open("../../assets/studio/seoul_dusk.jpg").convert("RGB").resize((1920, 1080))
KEYS = list(SCREENS)
sheet = Image.new("RGB", (1920, 540 * ((len(KEYS) + 1) // 2) // 2 * 1), (10, 14, 30))
tiles = []
for k in KEYS:
    scr = ep.prepare_screen(k, SCREENS[k])
    t = 3.0 if "chart" in scr or "card" in scr else 1.0
    content = ep.screen_content(scr, 960, 540, t if "img" not in scr else 1.0)
    piece, xy = ep.screen_piece(content, ep.SCREEN_K, 1.0, scr.get("label", ""), scr.get("credit", ""))
    frame = bg.copy().convert("RGBA"); frame.alpha_composite(piece, (int(xy[0]), int(xy[1])))
    frame = frame.convert("RGB"); frame.save(f"render/screens/{k}.png")
    tiles.append(frame.crop((780, 130, 1900, 830)).resize((560, 350)))
cols = 2; rows = (len(tiles) + 1) // 2
sheet = Image.new("RGB", (cols * 570, rows * 360), (10, 14, 30))
for i, im in enumerate(tiles): sheet.paste(im, ((i % cols) * 570 + 5, (i // cols) * 360 + 5))
sheet.save("render/screens/_contact.png"); print(len(KEYS), sheet.size)
