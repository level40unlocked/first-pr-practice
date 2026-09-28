"""Renders a vertical Short: background images + narration + word-highlighted captions.

Timing comes from the narration itself (Whisper word timestamps), so any TTS
provider works, including ones that don't return timing data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

WIDTH, HEIGHT, FPS = 1080, 1920, 30
YELLOW, WHITE, BLACK = (255, 212, 0), (255, 255, 255), (0, 0, 0)
CAPTION_TAIL = 0.15  # seconds a caption lingers after its last word, if nothing follows


@dataclass(frozen=True)
class Word:
    text: str
    start: float
    end: float


@dataclass(frozen=True)
class CaptionSpan:
    start: float
    end: float
    words: tuple[str, ...]
    highlight: int  # index into words


def transcribe(audio_path: Path, model_name: str = "base.en") -> list[Word]:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio_path), word_timestamps=True)
    return [Word(w.word.strip(), w.start, w.end) for s in segments for w in s.words]


def chunk_words(words: list[Word], max_words: int = 3) -> list[list[Word]]:
    """Groups words into caption chunks, breaking early at punctuation."""
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == max_words or re.search(r"[.?!,…]$", w.text):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def caption_spans(chunks: list[list[Word]], duration: float) -> list[CaptionSpan]:
    """One span per spoken word, showing its whole chunk with that word highlighted.

    Spans never overlap: a chunk's last word lingers at most CAPTION_TAIL and is
    always cut off when the next chunk starts.
    """
    spans = []
    for c, chunk in enumerate(chunks):
        next_start = chunks[c + 1][0].start if c + 1 < len(chunks) else duration
        texts = tuple(w.text.upper() for w in chunk)
        for k, w in enumerate(chunk):
            if k + 1 < len(chunk):
                end = chunk[k + 1].start
            else:
                end = min(w.end + CAPTION_TAIL, next_start)
            if end > w.start:
                spans.append(CaptionSpan(w.start, end, texts, k))
    return spans


def scene_bounds(words: list[Word], line_word_counts: list[int], n_images: int, duration: float) -> list[float]:
    """Start times for each image. Script lines are spread evenly over the images and
    each image starts when its first line starts. Returns n_images + 1 boundaries."""
    if not words or n_images <= 1 or not line_word_counts:
        return [duration * i / max(n_images, 1) for i in range(max(n_images, 1))] + [duration]
    line_starts, cum = [], 0
    for count in line_word_counts:
        line_starts.append(words[min(cum, len(words) - 1)].start)
        cum += count
    n_lines = len(line_word_counts)
    first_line_of_image = [min(round(i * n_lines / n_images), n_lines - 1) for i in range(n_images)]
    bounds = [0.0] + [line_starts[i] for i in first_line_of_image[1:]] + [duration]
    # Guard against misaligned transcripts producing out-of-order cuts.
    for i in range(1, len(bounds)):
        bounds[i] = max(bounds[i], bounds[i - 1])
    return bounds


def _font(font_path: Path | None, size: int):
    from PIL import ImageFont

    if font_path and font_path.exists():
        return ImageFont.truetype(str(font_path), size)
    return ImageFont.load_default(size)


def _text_image(lines, size, font_path, stroke, box=False, max_width=WIDTH - 80):
    """lines: list of list of (word, color). Shrinks the font until the widest line fits."""
    import numpy as np
    from PIL import Image, ImageDraw

    while True:
        font = _font(font_path, size)
        space = font.getlength(" ")
        widths = [sum(font.getlength(w) for w, _ in ln) + space * (len(ln) - 1) for ln in lines]
        if max(widths) <= max_width or size <= 24:
            break
        size = int(size * 0.9)
    line_h = int(size * 1.2)
    img = Image.new("RGBA", (WIDTH, line_h * len(lines) + 40), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if box:
        bw = max(widths) + 70
        draw.rounded_rectangle(((WIDTH - bw) / 2, 0, (WIDTH + bw) / 2, img.height), 28, fill=(0, 0, 0, 170))
    for row, (ln, width) in enumerate(zip(lines, widths)):
        x = (WIDTH - width) / 2
        for word, color in ln:
            draw.text((x, 20 + row * line_h), word, font=font, fill=color, stroke_width=stroke, stroke_fill=BLACK)
            x += font.getlength(word) + space
    return np.asarray(img)


def _ken_burns(image_path: Path, duration: float, zoom_in: bool):
    import numpy as np
    from moviepy import VideoClip
    from PIL import Image

    img = Image.open(image_path).convert("RGB")
    scale = max(WIDTH / img.width, HEIGHT / img.height) * 1.12  # headroom for the zoom
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)

    def frame(t):
        p = t / max(duration, 0.01)
        z = 1.0 + 0.10 * (p if zoom_in else 1 - p)
        cw, ch = img.width / z, img.height / z
        x, y = (img.width - cw) / 2, (img.height - ch) / 2
        return np.asarray(img.crop((x, y, x + cw, y + ch)).resize((WIDTH, HEIGHT), Image.BILINEAR))

    return VideoClip(frame, duration=duration)


def _split_hook(hook: str) -> list[list[tuple[str, tuple]]]:
    words = hook.upper().split()
    if len(words) < 3:
        return [[(w, WHITE) for w in words]]
    half = (len(words) + 1) // 2
    return [[(w, WHITE) for w in words[:half]], [(w, YELLOW) for w in words[half:]]]


def render(audio_path: Path, image_paths: list[Path], out_path: Path, words: list[Word],
           line_word_counts: list[int], hook_text: str, channel_name: str = "Four Eyes Report",
           font_path: Path | None = None) -> Path:
    from moviepy import AudioFileClip, CompositeVideoClip, ImageClip

    if not image_paths:
        raise ValueError("at least one background image is required")
    audio = AudioFileClip(str(audio_path))
    duration = audio.duration

    bounds = scene_bounds(words, line_word_counts, len(image_paths), duration)
    layers = [
        _ken_burns(path, end - start, n % 2 == 0).with_start(start)
        for n, (path, start, end) in enumerate(zip(image_paths, bounds, bounds[1:]))
        if end > start
    ]

    for span in caption_spans(chunk_words(words), duration):
        line = [(w, YELLOW if i == span.highlight else WHITE) for i, w in enumerate(span.words)]
        clip = ImageClip(_text_image([line], 92, font_path, stroke=10))
        layers.append(clip.with_start(span.start).with_duration(span.end - span.start)
                      .with_position(("center", int(HEIGHT * 0.60))))

    hook = ImageClip(_text_image(_split_hook(hook_text), 84, font_path, stroke=6, box=True))
    layers.append(hook.with_start(0).with_duration(min(2.2, duration)).with_position(("center", int(HEIGHT * 0.16))))

    first, _, rest = channel_name.upper().partition(" ")
    tag = [[(first, WHITE)] + ([(rest, YELLOW)] if rest else [])]
    layers.append(ImageClip(_text_image(tag, 40, font_path, stroke=4, box=True))
                  .with_duration(duration).with_position(("center", 70)))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    video = CompositeVideoClip(layers, size=(WIDTH, HEIGHT)).with_duration(duration).with_audio(audio)
    video.write_videofile(str(out_path), fps=FPS, codec="libx264", audio_codec="aac", preset="veryfast",
                          ffmpeg_params=["-crf", "21"], threads=8, logger=None)
    return out_path
