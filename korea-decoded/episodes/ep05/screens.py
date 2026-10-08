"""EP.5 event screens (explainer box pictures): cards from make_cards.py. Credits are on the card box."""
CARDS = "../../assets/stock/ep05/cards/"


def card(name, credit=""):
    return {"image": CARDS + name + ".png", "label": "", "credit": credit, "kb": "in"}


SCREENS = {
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
    "jamsu_night": card("jamsu_night", "Photo: Shiwon Cho (public domain)"),
    "jamsu_fountain": card("jamsu_fountain", "Photo: Wvdp (CC0)"),
    "jamsu_fountain2": card("jamsu_fountain2", "Photo: Photo and Share CC (public domain)"),
}
