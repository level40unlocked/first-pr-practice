"""EP.6 thumbnails (1280x720): Ms. Nonfic on the left, a missile illustration + the Sejong statue on the right, big text.
    cd episodes/ep06 && python3 make_thumbs.py
"""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
sys.path.insert(0, "../../prototypes")
spec = importlib.util.spec_from_file_location("t5", "../ep05/make_thumbs.py")
t5 = importlib.util.module_from_spec(spec); spec.loader.exec_module(t5)
CAST = "../../cast/"
t5.OFFBEAT = {"head": CAST + "news_head.png", "body": CAST + "news_body.png", "ref": CAST + "news_ref.png", "label": "MS. NONFIC",
              "shoulders": 520, "white_lens": True, "mouth": "open", "gaze": [0.8, 0.0]}
S = "../../assets/stock/ep06/"
os.makedirs("thumbs", exist_ok=True)
A, B = S + "missile_2_separation_glide.png", S + "sejong_statue_98_cropped.jpg"
t5.thumb(A, B, ["AMAZING", "K-DEFENSE?!"], "thumbs/thumb_A.jpg", size=112)
t5.thumb(A, B, ["KOREA'S", "NEW MISSILE?!"], "thumbs/thumb_B.jpg", size=104)
t5.thumb(A, B, ["MISSILE", "OR ALPHABET?!"], "thumbs/thumb_C.jpg", size=104)
