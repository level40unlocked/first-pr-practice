from korea_decoded.config import load_config
from korea_decoded.sensitivity import classify, stricter

KEYWORDS = load_config().negative_keywords


def test_negative_english_topic_goes_to_review():
    result = classify("Thousands lose deposits in Seoul jeonse fraud", KEYWORDS)
    assert result.level == "review"
    assert "fraud" in result.matched


def test_negative_korean_topic_goes_to_review():
    assert classify("빌라 전세사기 피해 확산", KEYWORDS).level == "review"


def test_neutral_topic_is_go():
    assert classify("Why Korean convenience stores are so good", KEYWORDS).level == "go"


def test_english_keywords_need_word_boundaries():
    # "war" must not match inside "software" or "award".
    assert classify("Samsung software team wins design award", KEYWORDS).level == "go"


def test_korean_core_word_is_not_nuclear():
    # "핵심" (core) must not trip the nuclear keywords.
    assert classify("반도체 산업의 핵심 기술", KEYWORDS).level == "go"


def test_stricter_prefers_review():
    assert stricter("go", "review") == "review"
    assert stricter("go", "go") == "go"


def test_keywords_ending_in_punctuation_still_match():
    from korea_decoded import textmatch
    assert textmatch.contains("prices in the u.s. are higher", "u.s.")
    assert not textmatch.contains("a ukulele lesson", "uk")
