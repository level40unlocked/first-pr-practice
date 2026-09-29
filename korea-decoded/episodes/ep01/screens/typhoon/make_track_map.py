"""2026 West Pacific typhoon tracks with Korea highlighted (EP.1 typhoon segment, line 4).

Data: IBTrACS West Pacific best tracks (NOAA NCEI, public domain) and Natural Earth coastlines
(public domain). Both are downloaded next to this script on first run. Output: track_map.png
"""
import os, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
SOURCES = {
    "ib.csv": "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.WP.list.v04r01.csv",
    "land.geojson": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_land.geojson",
    "countries.geojson": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson",
}
for name, url in SOURCES.items():
    if not os.path.exists(name):
        urllib.request.urlretrieve(url, name)
import csv, json
from PIL import Image, ImageDraw, ImageFont
W,H=1920,1080; LON0,LON1,LAT0,LAT1=100,180,0,45
def xy(lo,la): return ((lo-LON0)/(LON1-LON0)*W, (LAT1-la)/(LAT1-LAT0)*H)
F=lambda s: ImageFont.truetype(os.path.join(HERE, "..", "..", "..", "..", "assets", "fonts", "Poppins-Bold.ttf"), s)
SEA,LAND,KOR,TRACK,DOL=(9,28,58),(38,62,96),(255,212,0),(150,175,210),(235,70,70)
def polys(g):
    t=g["type"]; c=g["coordinates"]
    return [p[0] for p in c] if t=="MultiPolygon" else [c[0]]
def base():
    im=Image.new("RGB",(W,H),SEA); d=ImageDraw.Draw(im)
    for f in json.load(open("land.geojson"))["features"]:
        for ring in polys(f["geometry"]):
            if any(LON0-5<lo<LON1+5 and LAT0-5<la<LAT1+5 for lo,la in ring): d.polygon([xy(lo,la) for lo,la in ring],fill=LAND)
    for f in json.load(open("countries.geojson"))["features"]:
        if f["properties"].get("ADM0_A3")=="KOR":
            for ring in polys(f["geometry"]): d.polygon([xy(lo,la) for lo,la in ring],fill=KOR)
    return im
rows=list(csv.reader(open("ib.csv"))); i={h:k for k,h in enumerate(rows[0])}
tracks={}
for r in rows[2:]:
    if r[i['SEASON']]=='2026': tracks.setdefault((r[i['SID']],r[i['NAME']]),[]).append((float(r[i['LON']]),float(r[i['LAT']])))
im=base(); d=ImageDraw.Draw(im)
for (sid,n),pts in tracks.items():
    if n=="DOLPHIN": continue
    d.line([xy(*p) for p in pts],fill=TRACK,width=3)
dol=[p for (s,n),pts in tracks.items() if n=="DOLPHIN" for p in pts]
d.line([xy(*p) for p in dol],fill=DOL,width=7)
ex,ey=xy(*dol[-1]); d.ellipse((ex-12,ey-12,ex+12,ey+12),fill=DOL)
sx,sy=xy(121.5,31.2); d.ellipse((sx-8,sy-8,sx+8,sy+8),fill="white"); d.text((sx-10,sy-58),"Shanghai",font=F(34),fill="white",anchor="ra")
kx,ky=xy(127.8,36.3); d.text((kx+40,ky-20),"KOREA",font=F(40),fill=KOR)
dx,dy=xy(*dol[len(dol)//3]); d.text((dx-60,dy-70),"Typhoon Dolphin",font=F(38),fill=DOL)
# Title and source go on the screen's label bar and credit line, where a slow zoom can't crop them.
im.save("track_map.png"); print("ok", len(tracks))
