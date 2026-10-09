"""Gangnam Festival parade route on OpenStreetMap tiles (© OpenStreetMap contributors, ODbL)."""
import math, os, time, requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
UA = {"User-Agent": "FourEyesReport/0.1 (+https://github.com/level40unlocked/first-pr-practice)"}
Z = 17
START = (37.5242012, 127.0473766)   # Cheongdam Intersection (Nominatim)
END = (37.5219687, 127.0348096)     # Dosan Park Intersection (Nominatim)
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "assets", "fonts", "Poppins-Bold.ttf")
def px(lat, lon):
    n = 2 ** Z; x = (lon + 180) / 360 * n * 256
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n * 256
    return x, y
cx, cy = px((START[0] + END[0]) / 2, (START[1] + END[1]) / 2)
W, H = 1920, 1080
x0, y0 = cx - W / 2, cy - H / 2
canvas = Image.new("RGB", (W, H))
for tx in range(int(x0 // 256), int((x0 + W) // 256) + 1):
    for ty in range(int(y0 // 256), int((y0 + H) // 256) + 1):
        cache = f"tile_{Z}_{tx}_{ty}.png"
        if not os.path.exists(cache):
            r = requests.get(f"https://tile.openstreetmap.org/{Z}/{tx}/{ty}.png", headers=UA, timeout=30); r.raise_for_status()
            open(cache, "wb").write(r.content); time.sleep(0.3)
        canvas.paste(Image.open(cache).convert("RGB"), (int(tx * 256 - x0), int(ty * 256 - y0)))
# soften the map so the route stands out
canvas = Image.blend(canvas, Image.new("RGB", (W, H), (9, 28, 58)), 0.35)
d = ImageDraw.Draw(canvas)
# Dosan-daero centreline between the two intersections: OSM ways 218723443 and 988283554, fetched from
# Nominatim (polygon_geojson) and saved in dosan.json next to this script.
import json
ways = {r["osm_id"]: r["geojson"]["coordinates"] for r in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dosan.json")))
        if r.get("geojson", {}).get("type") == "LineString"}
road = sorted({(lon, lat) for w in (218723443, 988283554) for lon, lat in ways[w] if END[1] - 1e-4 <= lon <= START[1] + 1e-4}, reverse=True)
pts = [(px(*START)[0] - x0, px(*START)[1] - y0)] + [(px(lat, lon)[0] - x0, px(lat, lon)[1] - y0) for lon, lat in road] + [(px(*END)[0] - x0, px(*END)[1] - y0)]
d.line(pts, fill=(15, 15, 20), width=26, joint="curve"); d.line(pts, fill=(255, 212, 0), width=16, joint="curve")
F = lambda s: ImageFont.truetype(FONT, s)
for (x, y), label, dy in ((pts[0], "Cheongdam Intersection", -75), (pts[-1], "Dosan Park Intersection", 80)):
    d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=(235, 70, 70), outline="white", width=5)
    d.text((x, y + dy), label, font=F(40), fill="white", anchor="mm", stroke_width=6, stroke_fill=(9, 28, 58))
mx, my = pts[len(pts) // 2]
d.text((mx + 60, my - 90), "about 1 km of parade", font=F(50), fill=(255, 212, 0), anchor="mm", stroke_width=7, stroke_fill=(9, 28, 58))
d.text((W - 30, H - 30), "Map © OpenStreetMap contributors", font=F(26), fill="white", anchor="rs", stroke_width=4, stroke_fill=(9, 28, 58))
canvas.save("gangnam_route.png"); print("ok")
