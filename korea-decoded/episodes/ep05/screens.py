"""EP.5 event screens (explainer box pictures): cards from make_cards.py. Credits are on the card box."""
CARDS = "../../assets/stock/ep05/cards/"


def card(name, credit=""):
    return {"image": CARDS + name + ".png", "label": "", "credit": credit, "kb": "in"}


def chart(spec, credit="", label=""):
    return {"chart": spec, "label": label, "credit": credit}


SCREENS = {
    "two_fest": chart({"type": "icons", "cols": 2, "title": "TWO FESTIVALS, RIGHT NOW", "items": [["🎷", "Jarasum Jazz Festival"], ["🎬", "Busan Int'l Film Festival"]]}),
    "y2004": chart({"type": "bigtext", "lines": ["2004"], "size": 170, "sub": "FIRST FESTIVAL: 30 TEAMS FROM 12 COUNTRIES"}, "Source: Jarasum Jazz Festival (via Wikipedia)"),
    "jarasum_time": chart({"type": "timeline", "title": "JARASUM JAZZ, A TIMELINE", "events": [
        {"year": "2004", "label": "First festival"}, {"year": "2016", "label": "Representative festival"},
        {"year": "2023", "label": "Europe Jazz Network"}, {"year": "2026", "label": "23rd, France focus", "hl": True}]}, "Source: Wikipedia, festival site"),
    "france": chart({"type": "bigtext", "lines": ["FRANCE"], "size": 170, "sub": "COUNTRY IN FOCUS · 140 YEARS OF KOREA-FRANCE TIES"}),
    "years17": chart({"type": "bigtext", "lines": ["17 YEARS"], "size": 160, "sub": "NATE SMITH IS BACK AT JARASUM"}, "Source: Korea JoongAng Daily"),
    "days": chart({"type": "timeline", "title": "THE WEEKEND LINEUP", "events": [
        {"year": "FRI", "label": "Nate Smith"}, {"year": "SAT", "label": "Alfredo Rodriguez"}, {"year": "SUN", "label": "Tigran Hamasyan", "hl": True}]}, "Source: Korea JoongAng Daily"),
    "route": chart({"type": "icons", "cols": 3, "title": "HOW TO GET TO JARASUM", "items": [["🚆", "ITX · 55 min"], ["🚶", "Walk · 20 min"], ["🚌", "Shuttle bus"]]}, "Source: festival site"),
    "kids": chart({"type": "bigtext", "lines": ["KIDS FREE"], "size": 130, "sub": "ELEMENTARY AGE AND UNDER"}, "Source: Korea JoongAng Daily"),
    "y1996": chart({"type": "bigtext", "lines": ["1996"], "size": 170, "sub": "173 FILMS FROM 31 COUNTRIES"}, "Source: Wikipedia"),
    "biff_time": chart({"type": "timeline", "title": "BIFF, A TIMELINE", "events": [
        {"year": "1996", "label": "First festival"}, {"year": "2011", "label": "Busan Cinema Center"},
        {"year": "2014", "label": "UNESCO City of Film"}, {"year": "2026", "label": "31st edition", "hl": True}]}, "Source: Wikipedia"),
    "films316": chart({"type": "bigtext", "lines": ["316 FILMS"], "size": 150, "sub": "59 COUNTRIES · 93 WORLD PREMIERES"}, "Source: Korea Times, Oct 6, 2026"),
    "yeoh": chart({"type": "bigtext", "lines": ["MICHELLE YEOH"], "size": 110, "sub": "ASIAN FILMMAKER OF THE YEAR"}, "Source: Korea Times, Oct 6, 2026"),
    "michelle_prog": chart({"type": "bigtext", "lines": ["EVERYTHING EVERYWHERE", "ALL FOR MICHELLE"], "size": 78, "sub": "A SPECIAL PROGRAM FOR MICHELLE YEOH"}, "Source: Wikipedia, Korea Times"),
    "tickets": chart({"type": "icons", "cols": 2, "title": "HOW TO GET TICKETS", "items": [["💻", "Book on the festival site"], ["🎫", "Box office on site"]]}, "Source: Korea Times, festival site"),
    "jarasum_poster": card("jarasum_poster", "Poster: Jarasum Jazz Festival"),
    "jarasum_autumn": card("jarasum_autumn", "Photo: Katsujiro Maekawa (CC0)"),
    "biff_poster": card("biff_poster", "Poster: Busan International Film Festival"),
    "biff_center": card("biff_center", "Photo: 399scout (CC BY-SA 4.0)"),
    "biff_sign": card("biff_sign", "Photo: Bapputtegi (CC BY-SA 4.0)"),
    "biff_building": card("biff_building", "Photo: 399scout (CC BY-SA 4.0)"),
    "drone_poster": card("drone_poster", "Poster: Seoul Metropolitan Government"),
    "drone_show": card("drone_show", "Photo: KOREA.NET (CC BY-SA 2.0)"),
    "drone_heart": card("drone_heart", "Photo: KOREA.NET (CC BY-SA 2.0)"),
    "drone_roses": card("drone_roses", "Photo: KOREA.NET (CC BY-SA 2.0)"),
    "nate_smith": card("nate_smith", ""),
    "michelle": card("michelle", ""),
    "zhang": card("zhang", ""),
    "two_posters": card("two_posters", "Posters: Jarasum Jazz Festival, Busan International Film Festival"),
    "gapyeong_river": card("gapyeong_river", "Photo: Katsujiro Maekawa (CC0)"),
    "gapyeong_dusk": card("gapyeong_dusk", "Photo: Katsujiro Maekawa (CC0)"),
    "gapyeong_grass": card("gapyeong_grass", "Photo: Katsujiro Maekawa (CC0)"),
    "turtle": card("turtle", "Photo: 2ndPeter (CC BY 2.0)"),
    "france_flag": card("france_flag", "Photo: Acediscovery (CC BY 4.0)"),
    "rodriguez": card("rodriguez", "Photo: Withmany30 (CC BY-SA 3.0)"),
    "hamasyan": card("hamasyan", "Photo: Vahan Stepanyan (CC BY 3.0)"),
    "itx": card("itx", "Photo: Takeshi Aida (CC BY-SA 2.0)"),
    "piff2007": card("piff2007", "Photo: Jens-Olaf (CC BY-SA 2.0)"),
    "biff1996": card("biff1996", "Photo: Jens-Olaf (CC BY-SA 2.0)"),
    "bcc_night": card("bcc_night", "Photo: Raja Syazwina RS (CC BY 2.0)"),
    "seats2020": card("seats2020", "Photo: Bapputtegi (CC BY-SA 4.0)"),
    "biff2025": card("biff2025", "Photo: Jennifer 8. Lee (CC BY-SA 4.0)"),
    "cuaron": card("cuaron", "Photo: Adam Chitayat (CC BY-SA 4.0)"),
    "ahn": card("ahn", "Photo: LG Electronics (CC BY 2.0)"),
    "outdoor": card("outdoor", "Photo: Raja Syazwina RS (CC BY 2.0)"),
    "ktx": card("ktx", "Photo: Minseong Kim (CC BY-SA 4.0)"),
    "jamsu_night": card("jamsu_night", "Photo: Shiwon Cho (public domain)"),
    "jamsu_fountain": card("jamsu_fountain", "Photo: Wvdp (CC0)"),
    "jamsu_fountain2": card("jamsu_fountain2", "Photo: Photo and Share CC (public domain)"),
}
