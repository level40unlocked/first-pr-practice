from korea_decoded.config import load_config
from korea_decoded.models import RawTopic
from korea_decoded.scoring import detect_countries, detect_pillar

CONFIG = load_config()


def countries(title):
    return detect_countries(RawTopic(source="t", title=title, url="u"), CONFIG)


def test_detects_countries_in_english_and_korean():
    assert countries("Why Americans are shocked by Korean restaurants") == ["US"]
    assert countries("한국과 일본의 편의점 비교") == ["JP"]
    assert countries("Korean dramas are huge in the Philippines and Brazil") == ["BR", "PH"]


def test_longer_country_names_win_over_substrings():
    # "인도네시아" (Indonesia) contains "인도" (India).
    assert countries("인도네시아에서 인기인 한국 라면") == ["ID"]


def test_korea_alone_is_not_a_comparison():
    assert countries("Why Korean convenience stores are so good") == []


def test_plain_topics_keep_their_pillar():
    pillar = detect_pillar(RawTopic(source="t", title="How Samsung makes chips", url="u"), CONFIG)
    assert pillar.key == "business_tech"
