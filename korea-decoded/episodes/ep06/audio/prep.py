"""Builds audio/lines_v1.json for EP.6 from ../script.md with TTS spellings."""
import importlib.util, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("s", os.path.join(HERE, "../parse_script.py")); s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
V = {"K": "e18664a7-ee4f-5273-acf8-533eb24cd366", "Kangfree": "e9cfbbf0-4476-46be-b396-596eb774b165",
     "Dusk": "6f98d3dd-324f-4845-8c28-c1d1647a06cd", "Nonfic": "3c2b83c0-2e0a-5ae8-998a-a5fe71b7eccd", "Dr. H": "032386ec-491b-5bdc-81ac-49e9a6a2c89d"}
TTS = [("ga, gya, geo, gyeo", "gah, gyah, guh, gyuh"), ("NH Nonghyup", "N H Nong-hyup"), ("BNK Busan", "B N K Boo-san"), ("Hyundai Capital", "Hyun-day Capital"),
       ("Hyundai Rotem", "Hyun-day Row-tem"), ("KB Kookmin", "K B Kook-min"), ("Shinhan", "Shin-han"), ("Yegaram", "Yeh-gah-ram"), ("Woori", "Woo-ree"),
       ("Hana", "Hah-na"), ("Coupang", "Koo-pang"), ("Kimbot", "Kim-bot"), ("Hyunmoo-5", "Hyun-moo five"), ("HyCore", "High-Core"), ("Gagya", "Gah-gya"),
       ("Hangul", "Hahn-gul"), ("Sejong", "Say-jong"), ("Joseon", "Joe-sun"), ("Marjan Haghi", "Mar-jahn Hah-ghee"), ("Nguyen Bao Chau", "Nwin Bow Chow"),
       ("Amira Kamal Mohamed", "Ah-mee-rah Kah-mal Mo-ha-med"), ("EXO", "Ex-oh"), ("Taean", "Teh-ahn"), ("Yonhap", "Yon-hap"), ("Jae Myung", "Jay Myung"),
       ("Ms. Nonfic", "Miss Nonfic"), ("Dr. H", "Doctor H")]
RE = [(r"\bADD\b", "A D D"), (r"\bAI\b", "A I"), (r"\bIP\b", "I P")]
def tts(t):
    for a, b in TTS: t = t.replace(a, b)
    for a, b in RE: t = re.sub(a, b, t)
    return t
lines = [{"index": i, "who": w, "text": e, "tts_text": tts(e), "voice_id": V[w]} for i, (w, e, k, sc) in enumerate(s.L, 1)]
json.dump(lines, open(os.path.join(HERE, "lines_v1.json"), "w"), ensure_ascii=False, indent=1)
print(len(lines))
