import wave

import numpy as np
from PIL import Image

from korea_decoded.editor import Word, caption_spans, chunk_words, render, scene_bounds

WORDS = [Word("If", 0.0, 0.2), Word("you", 0.2, 0.4), Word("think", 0.4, 0.7), Word("stores", 0.7, 1.0),
         Word("are", 1.0, 1.1), Word("boring…", 1.1, 1.6), Word("Korea", 1.62, 2.0), Word("disagrees.", 2.0, 2.5)]


def test_chunks_break_at_three_words_and_punctuation():
    chunks = chunk_words(WORDS)
    assert [[w.text for w in c] for c in chunks] == [
        ["If", "you", "think"], ["stores", "are", "boring…"], ["Korea", "disagrees."]]


def test_captions_never_overlap():
    # Regression: the last word of a chunk used to linger 0.15s into the next chunk.
    spans = caption_spans(chunk_words(WORDS), duration=3.0)
    for a, b in zip(spans, spans[1:]):
        assert a.end <= b.start + 1e-9, (a, b)
    boring = next(s for s in spans if s.words[s.highlight] == "BORING…")
    assert boring.end == 1.62  # cut at "Korea", not 1.6 + 0.15


def test_scene_bounds_follow_line_starts():
    # 3 lines (3, 3, 2 words) over 3 images: each image starts with its line.
    assert scene_bounds(WORDS, [3, 3, 2], 3, 3.0) == [0.0, 0.7, 1.62, 3.0]


def test_scene_bounds_fall_back_to_even_split_without_words():
    assert scene_bounds([], [3], 2, 4.0) == [0.0, 2.0, 4.0]


def test_render_produces_a_vertical_video(tmp_path):
    audio = tmp_path / "a.wav"
    with wave.open(str(audio), "wb") as f:
        f.setnchannels(1), f.setsampwidth(2), f.setframerate(16000)
        f.writeframes((np.sin(np.linspace(0, 2000, 16000 * 2)) * 3000).astype(np.int16).tobytes())
    images = []
    for i, color in enumerate(["red", "blue"]):
        images.append(tmp_path / f"{i}.png")
        Image.new("RGB", (720, 1280), color).save(images[-1])

    out = render(audio, images, tmp_path / "out.mp4", WORDS[:5], [3, 2], "Korean stores hit different")

    from moviepy import VideoFileClip
    clip = VideoFileClip(str(out))
    assert clip.size == [1080, 1920] and abs(clip.duration - 2.0) < 0.1
    clip.close()
