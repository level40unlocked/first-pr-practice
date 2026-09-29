"""Shot planning and episode splitting for the prototype renderer (prototypes/episode.py, render_episode.py)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "prototypes"))
pytest.importorskip("cv2")

import episode  # noqa: E402
import render_episode  # noqa: E402


def test_shots_follow_news_grammar():
    lines = [{"who": "anchor"}, {"who": "anchor", "screen": "s1"}, {"who": "anchor", "screen": "s2", "big": True},
             {"who": "panel"}, {"who": "anchor"}, {"who": "panel"}]
    assert episode.plan_shots(lines) == ["anchor_solo", "anchor_screen", "screen_full",
                                         "two_shot", "speaker_close", "speaker_close"]


def test_a_line_can_force_its_shot():
    lines = [{"who": "anchor", "shot": "wide"}, {"who": "panel", "shot": "speaker_close"}]
    assert episode.plan_shots(lines) == ["wide", "speaker_close"]
    with pytest.raises(ValueError):
        episode.plan_shots([{"who": "anchor", "shot": "drone"}])


def test_split_fills_topic_ticker_and_cast():
    ep = {"episode": 3, "characters": {"anchor": {}, "panel": {}, "chef": {}},
          "segments": [{"headline": "A", "lines": [{"who": "anchor"}, {"who": "panel"}]},
                       {"headline": "B", "lines": [{"who": "anchor"}]},
                       {"headline": "C", "lines": [{"who": "chef"}]}]}
    scenes = render_episode.split_episode(ep, "ep3")
    assert [s["topic"] for s in scenes] == [[1, 3], [2, 3], [3, 3]]
    assert scenes[0]["up_next"] == ["B", "C"]
    assert scenes[2]["up_next"] == ["Thanks for watching"]
    assert set(scenes[1]["characters"]) == {"anchor"}  # only who appears, plus the anchor
    assert set(scenes[2]["characters"]) == {"anchor", "chef"}
    assert scenes[1]["out_long"] == "ep3_s2_long.mp4"


def test_a_panel_line_with_a_visual_plays_over_the_full_screen():
    lines = [{"who": "anchor"}, {"who": "panel", "screen": "s1"}]
    assert episode.plan_shots(lines) == ["anchor_solo", "screen_full"]


def test_screens_inside_one_line_switch_in_order_and_crossfade():
    ln = {"screen": ["a", "b", "c"], "start": 10.0, "end": 16.0}
    assert episode.screen_at(ln, 10.5)[0] == "a"
    key, since, prev, fade = episode.screen_at(ln, 12.1)  # b starts at 12.0
    assert (key, prev) == ("b", "a") and 0 < fade < 1
    assert episode.screen_at(ln, 15.9)[:3:2] == ("c", None)
    split = {"screen": ["a", "b"], "screen_split": [0.25], "start": 0.0, "end": 8.0}
    assert episode.screen_at(split, 2.5)[0] == "b"


def test_number_card_counts_up_and_formats():
    assert episode.fmt_number(568800, {}) == "568,800"
    assert episode.fmt_number(94.8, {"decimals": 1, "suffix": "%"}) == "94.8%"
    card = {"title": "BY THE NUMBERS", "stats": [{"value": 100, "label": "x"}]}
    before, after = episode.card_image(card, 660, 371, 0.0), episode.card_image(card, 660, 371, 3.0)
    assert before.size == (660, 371) and before.tobytes() != after.tobytes()


def test_caption_timing_is_spread_over_each_line():
    lines = [{"text": "Hello, world.", "start": 1.0, "end": 2.0}, {"text": "Bye", "start": 3.0, "end": 3.5}]
    words = episode.estimate_words(lines)
    assert [w["w"] for w in words] == ["Hello,", "world.", "Bye"]
    assert words[0]["s"] == 1.0 and abs(words[1]["e"] - 2.0) < 1e-9 and words[2]["s"] == 3.0


def test_recognized_word_timings_win_over_the_estimate():
    lines = [{"text": "Hello, world.", "start": 2.0, "end": 3.0, "words": [["Hello,", 0.1, 0.4], ["world.", 0.5, 0.9]]}]
    words = episode.estimate_words(lines)
    assert [(w["w"], w["s"], w["e"]) for w in words] == [("Hello,", 2.1, 2.4), ("world.", 2.5, 2.9)]


def test_long_caption_groups_shrink_to_stay_on_screen():
    import newsrig
    from PIL import Image
    canvas = Image.new("RGB", (newsrig.SW, newsrig.SH))
    words = [{"w": w, "s": 0, "e": 1} for w in ("a", "three-and-a-half-meter", "shark")]
    newsrig.draw_caption(canvas, words, 0.5)
    band = canvas.crop((0, newsrig.CAPTION_Y - 50, newsrig.SW, newsrig.CAPTION_Y + 50))
    left, right = band.crop((0, 0, 10, 100)), band.crop((newsrig.SW - 10, 0, newsrig.SW, 100))
    assert left.getextrema() == ((0, 0),) * 3 and right.getextrema() == ((0, 0),) * 3  # nothing touches the edges
