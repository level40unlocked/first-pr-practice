"""EP.4 screens (explainer box pictures): photo cards from make_cards.py and charts. Used by preview_screens.py and, later, build_episode.py."""
import os
CARDS = "../../assets/stock/ep04/cards/"
AG = "Photo: courtesy of the agency"


def card(name, label="", credit=AG):
    return {"image": CARDS + name + ".png", "label": label, "credit": credit, "kb": "in"}


def chart(spec, credit="", label=""):
    return {"chart": spec, "label": label, "credit": credit}


SCREENS = {
    "title": chart({"type": "bigtext", "lines": ["FIN.K.L"], "size": 150, "sub": "FOUR MEMBERS · DEBUTED 1998"}),
    "debut_1998": card("debut_1998", credit="Photo: as supplied"),
    "name_hyori": card("name_hyori", credit="Photo: as supplied"),
    "name_ock": card("name_ock", credit="Photo: as supplied"),
    "name_jin": card("name_jin", credit="Photo: Starnews"),
    "name_yuri": card("name_yuri", credit="Photo: as supplied"),
    "recent": card("recent", credit="Photo: as supplied"),
    "cover_2005": card("cover_2005", credit="Image: single cover, as supplied"),
    "years21": chart({"type": "bigtext", "lines": ["21 YEARS"], "size": 170, "sub": "FROM 2005 TO 2026"}),
    "timeline": chart({"type": "timeline", "title": "FIN.K.L, A TIMELINE", "events": [
        {"year": "1998", "label": "Debut"}, {"year": "2005", "label": "Last single"},
        {"year": "2019", "label": "Camping Club"}, {"year": "2026", "label": "Full-group return", "hl": True}]}),
    "camping": card("camping", credit="Image: JTBC \"Camping Club\" promo"),
    "plans": chart({"type": "icons", "cols": 4, "title": "THE NEXT TWO YEARS", "items": [
        ["🎬", "Documentary"], ["📺", "Variety shows"], ["🖼️", "Exhibitions"], ["☕", "Merch"],
        ["🤝", "Brand collabs"], ["📣", "Ads"], ["💛", "Fan projects"]]}, "Source: Gemstone E&M, via Kyunghyang"),
}
