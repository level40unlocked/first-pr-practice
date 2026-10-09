"""EP.6 screens (explainer box pictures): photo cards from make_cards.py, charts from prototypes/charts.py, illustrations. Credits are on the box."""
CARDS = "../../assets/stock/ep06/cards/"
STOCK = "../../assets/stock/ep06/"


def card(name, credit=""):
    return {"image": CARDS + name + ".png", "label": "", "credit": credit, "kb": "in"}


def illo(name, kb="in"):
    return {"image": STOCK + name, "label": "", "credit": "AI-generated concept illustration", "kb": kb}


def chart(spec, credit="", label=""):
    return {"chart": spec, "label": label, "credit": credit}


KT = "Source: Korea Times"
SCREENS = {
    "three": chart({"type": "bigtext", "lines": ["3 STORIES"], "size": 150, "sub": "HACKERS · A MISSILE · AN ALPHABET"}),
    "firms7": chart({"type": "bigtext", "lines": ["7 FIRMS"], "size": 170, "sub": "REPORTED DATA BREACHES THIS MONTH"}, KT + ", Oct 6, 2026"),
    "banks": chart({"type": "words", "title": "THE SEVEN FIRMS", "words": ["SHINHAN BANK", "KB KOOKMIN", "HANA BANK", "BNK BUSAN", "YEGARAM SAVINGS", "WELCOME SAVINGS", "HYUNDAI CAPITAL"]}, KT + ", Oct 6, 2026"),
    "n25000": chart({"type": "bigtext", "lines": ["25,000"], "size": 170, "sub": "SHINHAN BANK CUSTOMERS EXPOSED"}, KT + "/Yonhap, Oct 6, 2026"),
    "hana89": chart({"type": "bigtext", "lines": ["HANA: 89"], "size": 130, "sub": "WOORI AND NH NONGHYUP BLOCKED THE ATTEMPTS"}, KT + "/Yonhap, Oct 6, 2026"),
    "scan": chart({"type": "icons", "cols": 3, "title": "HOW AN AI-ASSISTED ATTACK WORKS", "items": [["🔍", "SCAN MANY FIRMS"], ["🔓", "FIND A WEAK SPOT"], ["🚪", "GO IN"]]}, "Source: Korea Times, Oct 6, 2026"),
    "ips": chart({"type": "bigtext", "lines": ["~30 IP ADDRESSES"], "size": 96, "sub": "12 COUNTRIES · LOCATION DOES NOT PROVE THE CULPRIT"}, KT + ", Oct 6, 2026"),
    "alert": chart({"type": "timeline", "title": "THE RESPONSE", "events": [{"year": "OCT 6", "label": "Caution alert"}, {"year": "1 MONTH", "label": "Month-long response", "hl": True}]}, KT + ", Oct 6, 2026"),
    "income": chart({"type": "bigtext", "lines": ["KNOWS YOUR INCOME?", "STILL MIGHT BE A SCAM"], "size": 78, "sub": "LEAKED DETAILS MAKE SCAMMERS SOUND REAL"}, KT + ", Oct 6, 2026"),
    "coupang": chart({"type": "bigtext", "lines": ["COUPANG OUTAGE"], "size": 110, "sub": "OCT 9 · ~2 HOURS · CAUSE NOT CONFIRMED"}, KT + ", Oct 9, 2026"),
    "launch": illo("missile_1_launch.png"),
    "mach5": chart({"type": "bigtext", "lines": ["MACH 5+"], "size": 190, "sub": "5X THE SPEED OF SOUND · ~6,100 KM/H"}, "Source: Korea Times"),
    "paths": chart({"type": "paths", "title": "TWO WAYS TO FLY"}),
    "flight": chart({"type": "flight"}),
    "low": chart({"type": "bigtext", "lines": ["1  FLIES LOW"], "size": 110, "sub": "THE EARTH'S CURVE HIDES IT FROM GROUND RADAR"}),
    "course": chart({"type": "bigtext", "lines": ["2  CHANGES COURSE"], "size": 100, "sub": "THE PREDICTED TARGET KEEPS MOVING"}),
    "time": chart({"type": "bigtext", "lines": ["3  LESS TIME"], "size": 120, "sub": "THE WINDOW TO RESPOND CAN BE MINUTES"}),
    "heat": chart({"type": "bigtext", "lines": ["1,000°C+"], "size": 150, "thermo": True, "sub": "AIR FRICTION HEATS THE SURFACE"}),
    "plasma": chart({"type": "bigtext", "lines": ["PLASMA"], "size": 160, "sub": "CAN BLOCK RADIO SIGNALS"}),
    "checks": chart({"type": "icons", "cols": 2, "title": "WHAT THE TEST CHECKED", "items": [["📈", "PATH AND SPEED"], ["🔥", "HEAT PROTECTION"], ["🎯", "GUIDANCE AND CONTROL"], ["🌊", "LOW-ALTITUDE MANEUVERS"]]}, KT + ", Oct 8, 2026"),
    "president": chart({"type": "bigtext", "lines": ["PRESIDENT LEE"], "size": 120, "sub": "ATTENDED THE TEST · OCT 8"}, KT + ", Oct 8, 2026"),
    "hyunmoo": chart({"type": "bigtext", "lines": ["HYUNMOO-5"], "size": 140, "sub": "INSPECTED THE SAME DAY · 'MONSTER MISSILE'"}, KT + ", Oct 8, 2026"),
    "kmbars": chart({"type": "bars", "title": "NORTH KOREA'S OCT 3 LAUNCH: RANGE", "bars": [{"label": "SEOUL'S ASSESSMENT", "value": 700, "text": "700 KM"}, {"label": "PYONGYANG'S CLAIM", "value": 1000, "text": "1,000 KM", "hl": True}], "suffix": " km"}, KT + ", Oct 8, 2026"),
    "compare": chart({"type": "icons", "cols": 2, "title": "TWO KINDS OF HYPERSONIC WEAPON", "items": [["🪂", "HGV: GLIDES"], ["🚀", "HYCORE: ENGINE ON"]]}, KT + ", Mar 9, 2026"),
    "scramjet": illo("missile_4_scramjet.png"),
    "hycore_time": chart({"type": "timeline", "title": "HYCORE", "events": [{"year": "2018", "label": "Work begins"}, {"year": "2024", "label": "Mach 6+ at 23 km"}, {"year": "2035", "label": "Mass production goal", "hl": True}]}, KT + ", Mar 9, 2026"),
    "y100": chart({"type": "bigtext", "lines": ["100 YEARS"], "size": 160, "sub": "HANGUL DAY, 1926-2026"}, "Source: Wikipedia, Korea Times"),
    "t1926": chart({"type": "timeline", "title": "HANGUL DAY", "events": [{"year": "1446", "label": "The text"}, {"year": "1926", "label": "First celebration"}, {"year": "2026", "label": "100 years", "hl": True}]}, "Source: Wikipedia"),
    "gagya": chart({"type": "letters", "title": "GAGYA DAY: THE FIRST SYLLABLES", "items": [["가", "GA"], ["갸", "GYA"], ["거", "GEO"], ["겨", "GYEO"]]}),
    "tstatus": chart({"type": "timeline", "title": "THE DAY OFF", "events": [{"year": "1990s", "label": "No day off"}, {"year": "2000s", "label": "National day"}, {"year": "2013", "label": "Day off is back", "hl": True}]}, "Source: Korean press, Wikipedia"),
    "n357": chart({"type": "bigtext", "lines": ["357"], "size": 190, "sub": "LEARNERS INVITED TO KOREA, A RECORD"}, KT + ", Oct 8, 2026"),
    "n181": chart({"type": "bigtext", "lines": ["181"], "size": 190, "sub": "LEARNERS FROM 71 COUNTRIES"}, KT + ", Oct 8, 2026"),
    "ratio": chart({"type": "bigtext", "lines": ["284 : 1"], "size": 170, "sub": "SPEAKING CONTEST, PER FINALIST SPOT"}, KT + ", Oct 8, 2026"),
    "pct534": chart({"type": "bigtext", "lines": ["53.4%"], "size": 190, "sub": "K-CONTENT IS THE #1 REASON TO LEARN KOREAN"}, "Source: King Sejong Institute survey (press reports)"),
    "study": chart({"type": "bars", "title": "WHY FOREIGNERS LEARN KOREAN (2025)", "bars": [{"label": "STUDY IN KOREA", "value": 50.9, "text": "50.9%", "hl": True}, {"label": "CAREER", "value": 37.0, "text": "37%"}], "suffix": "%", "decimals": 1}, "Source: King Sejong Institute Foundation survey"),
    "haerye": card("haerye", "Photo: Wikimedia Commons (public domain)"),
    "sejong_poster": card("sejong_poster", "Poster: Ministry of Culture, Sports and Tourism / King Sejong Institute Foundation"),
    "speech": card("speech", "Photo: King Sejong Institute Foundation"),
    "award_group": card("award_group", "Photo: King Sejong Institute Foundation"),
    "scholar": card("scholar", "Photo: King Sejong Institute Foundation"),
    "statue": card("statue", "Photo: Wikimedia Commons (credit in description)"),
    "night": card("night", "Photo: Wikimedia Commons (credit in description)"),
}
