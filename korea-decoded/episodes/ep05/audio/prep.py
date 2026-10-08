"""Builds audio/lines_v1.json for EP.5 (events segment) from ../script_events_v2.py with TTS spellings."""
import importlib.util, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("s", os.path.join(HERE, "../script_events_v2.py")); s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
V = {"K": "e18664a7-ee4f-5273-acf8-533eb24cd366", "Kangfree": "e9cfbbf0-4476-46be-b396-596eb774b165", "Indoor": "f2801b0f-e345-598e-86f5-8364d886d96b"}
TTS = [("Jarasum", "Jah-rah-sum"), ("Gapyeong", "Gah-pyung"), ("Bukhan", "Book-han"), ("Yongsan", "Yong-san"), ("ITX", "I T X"), ("KTX", "K T X"),
       ("Yes24", "Yes twenty-four"), ("Tigran Hamasyan", "Tee-gran Ha-ma-see-an"), ("Agathe Briot", "Ah-gat Bree-oh"), ("BIFF", "Biff"), ("PIFF", "Piff"),
       ("Pusan", "Poo-san"), ("Busan", "Boo-san"), ("Zhang Yimou", "Jahng Yee-moh"), ("Cuaron", "Kwah-rohn"), ("Gainsbourg", "Gains-boor"),
       ("Michelle Yeoh", "Michelle Yoh"), ("Ahn Sung-ki", "Ahn Sung-gee"), ("Hangul", "Hahn-gul"), ("Alfredo Rodriguez", "Alfredo Rod-ree-gez")]
def tts(t):
    for a, b in TTS: t = t.replace(a, b)
    return t
lines = [{"index": i, "who": w, "text": e, "tts_text": tts(e), "voice_id": V[w]} for i, (w, e, k, sc) in enumerate(s.L, 1)]
json.dump(lines, open(os.path.join(HERE, "lines_v1.json"), "w"), ensure_ascii=False, indent=1)
print(len(lines))
