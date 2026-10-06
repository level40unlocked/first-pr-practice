"""Builds audio/lines_v1.json for EP.4 (Fin.K.L = 1..N, comeback = 101..) with TTS spellings."""
import re, json
V={"K":"e18664a7-ee4f-5273-acf8-533eb24cd366","Kangfree":"e9cfbbf0-4476-46be-b396-596eb774b165","Offbeat":"549ff70a-3ee7-4f04-a4d9-89a24fab7709"}
TTS=[("Fin.K.L","Finkle"),("FIN.K.L","FINKLE"),("S.E.S","S E S"),("Cyworld","Sigh-world"),("Hyori","Hyo-ri"),("Ock Joo-hyun","Ok Joo-hyun"),("Sung Yuri","Sung Yoo-ri"),
("ONEW","Oh-new"),("ZICO","Zee-ko"),("Yesung","Yeh-sung"),("X:IN","X-in"),("N.Flying","N Flying"),("YUQI","Yoo-chee"),("i-dle","eye-dle"),("ZEROBASEONE","Zero Base One"),
("DEAD:ALIVE","Dead Alive"),("Xdinary","Extraordinary"),("LISA","Lisa"),("BLACKPINK","Blackpink"),("ILLIT","Ill-it"),("IVE","Eye-v"),("SHINee","Shiny"),("KickFlip","Kick Flip")]
def tts(t):
    for a,b in TTS: t=t.replace(a,b)
    t=t.replace(" [VERIFY]","").replace("[VERIFY]","")
    return t
def rows(p):
    out=[]
    for r in open(p).read().splitlines():
        if re.match(r"\| \d+ \|",r):
            c=r.split("|"); out.append((c[2].strip(),c[3].strip().replace("🆕 ","")))
    return out
lines=[]
for base,p in ((0,"../script_finkl.md"),(100,"../script_comeback.md")):
    for i,(w,e) in enumerate(rows(p),1):
        lines.append({"index":base+i,"who":w,"text":e,"tts_text":tts(e),"voice_id":V[w]})
json.dump(lines,open("lines_v1.json","w"),ensure_ascii=False,indent=1)
print(len(lines))
for l in lines: print(l["index"],l["who"][0],l["tts_text"])
