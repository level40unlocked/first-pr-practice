"""Automate a simple 2D "talking" video: swap mouth shapes in sync with audio volume.

This is a rule-based (no AI model) lip-sync approach: the character's mouth
switches between a small set of drawn shapes ("closed", "mid", "open")
based on how loud the audio is at each moment. It works with a
custom-drawn character (a folder of PNGs) or, if none is supplied, a
built-in placeholder character and audio track so the whole pipeline can
be tried end to end immediately.
"""

import argparse
import math
import os
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

MOUTH_STATES = ("closed", "mid", "open")


# ---------------------------------------------------------------------------
# Audio analysis
# ---------------------------------------------------------------------------

def _ensure_wav(audio_path):
    """Return a path to a WAV version of ``audio_path``, converting if needed.

    Returns ``(wav_path, temp_path_to_clean_up_or_None)``.
    """
    path = Path(audio_path)
    if path.suffix.lower() == ".wav":
        return str(path), None

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    tmp_wav = str(Path(tempfile.mkstemp(suffix=".wav")[1]))
    subprocess.run(
        [ffmpeg_exe, "-y", "-i", str(path), "-ac", "1", "-ar", "22050", tmp_wav],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return tmp_wav, tmp_wav


def analyze_amplitude(audio_path, fps, smoothing=2):
    """Return one normalized loudness value (0-1) per video frame for ``audio_path``."""
    wav_path, tmp_to_clean = _ensure_wav(audio_path)
    try:
        with wave.open(wav_path, "rb") as wav_file:
            n_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            raw = wav_file.readframes(wav_file.getnframes())

        dtype = {1: np.uint8, 2: np.int16, 4: np.int32}[sample_width]
        samples = np.frombuffer(raw, dtype=dtype).astype(np.float64)
        if n_channels > 1:
            samples = samples.reshape(-1, n_channels).mean(axis=1)
        if sample_width == 1:
            samples -= 128  # unsigned 8-bit -> signed

        duration = len(samples) / frame_rate if frame_rate else 0.0
        num_video_frames = max(1, round(duration * fps))
        samples_per_frame = max(1, len(samples) // num_video_frames)

        rms_values = []
        for i in range(num_video_frames):
            start = i * samples_per_frame
            end = start + samples_per_frame
            chunk = samples[start:end]
            rms_values.append(math.sqrt(float(np.mean(chunk ** 2))) if len(chunk) else 0.0)

        peak = max(rms_values) if rms_values else 0.0
        amplitudes = [(v / peak if peak > 0 else 0.0) for v in rms_values]

        if smoothing > 1 and len(amplitudes) > 1:
            kernel = np.ones(smoothing) / smoothing
            amplitudes = list(np.convolve(amplitudes, kernel, mode="same"))

        return amplitudes
    finally:
        if tmp_to_clean and os.path.exists(tmp_to_clean):
            os.remove(tmp_to_clean)


def select_mouth_state(amplitude, low_threshold=0.15, high_threshold=0.45):
    """Map a normalized loudness value to one of ``MOUTH_STATES``."""
    if amplitude <= low_threshold:
        return "closed"
    if amplitude <= high_threshold:
        return "mid"
    return "open"


def envelope_follow(amplitudes, attack=0.6, release=0.15):
    """Smooth per-frame amplitude into a mouth-openness envelope (0-1).

    A high ``attack`` makes the mouth snap open quickly when sound starts;
    a low ``release`` makes it close more gradually afterwards, which reads
    as more natural than switching mouth shapes on the raw, jittery
    amplitude.
    """
    envelope = []
    level = 0.0
    for amplitude in amplitudes:
        coeff = attack if amplitude > level else release
        level += (amplitude - level) * coeff
        envelope.append(level)
    return envelope


# ---------------------------------------------------------------------------
# Frame composition
# ---------------------------------------------------------------------------

def blend_mouth_overlay(mouths, openness):
    """Interpolate between the closed/mid/open overlays for an in-between mouth shape."""
    openness = max(0.0, min(1.0, openness))
    if openness <= 0.5:
        return Image.blend(mouths["closed"], mouths["mid"], openness * 2)
    return Image.blend(mouths["mid"], mouths["open"], (openness - 0.5) * 2)


def compose_frame(base_image, mouth_overlay):
    """Paste a mouth overlay onto the base character image and return an RGB PIL Image."""
    if mouth_overlay.size != base_image.size:
        raise ValueError("mouth overlay must be the same size as the base image")
    frame = Image.alpha_composite(base_image.convert("RGBA"), mouth_overlay.convert("RGBA"))
    return frame.convert("RGB")


def load_character(character_dir):
    """Load a custom character: ``base.png`` plus one ``mouth_<state>.png`` per state.

    Every image must share the same canvas size, and mouth images must be
    transparent everywhere except where the mouth is drawn, so they can be
    layered directly on top of ``base.png``.
    """
    character_dir = Path(character_dir)
    base = Image.open(character_dir / "base.png").convert("RGBA")
    mouths = {}
    for state in MOUTH_STATES:
        mouth = Image.open(character_dir / f"mouth_{state}.png").convert("RGBA")
        if mouth.size != base.size:
            raise ValueError(f"mouth_{state}.png must match base.png size {base.size}")
        mouths[state] = mouth
    return base, mouths


# ---------------------------------------------------------------------------
# Placeholder character + audio (used when the user hasn't supplied their own)
# ---------------------------------------------------------------------------

def _draw_placeholder_face(size=480):
    base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)
    cx, cy = size // 2, size // 2

    draw.pieslice((cx - 170, cy - 220, cx + 170, cy + 60), 180, 360, fill=(60, 40, 30, 255))
    draw.ellipse((cx - 160, cy - 180, cx + 160, cy + 180), fill=(255, 219, 172, 255), outline=(90, 60, 40, 255), width=4)
    draw.ellipse((cx - 80, cy - 40, cx - 40, cy), fill=(40, 30, 20, 255))
    draw.ellipse((cx + 40, cy - 40, cx + 80, cy), fill=(40, 30, 20, 255))
    return base


def _draw_placeholder_mouth(state, size=480):
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = size // 2, size // 2 + 90

    if state == "closed":
        draw.line((cx - 45, cy, cx + 45, cy), fill=(120, 40, 40, 255), width=6)
    elif state == "mid":
        draw.ellipse((cx - 40, cy - 15, cx + 40, cy + 15), fill=(120, 40, 40, 255))
    else:  # open
        draw.ellipse((cx - 45, cy - 30, cx + 45, cy + 30), fill=(90, 20, 20, 255))
        draw.ellipse((cx - 25, cy - 12, cx + 25, cy + 12), fill=(230, 120, 120, 255))
    return overlay


def generate_placeholder_character(size=480):
    """Build a simple built-in 2D face so the pipeline can run without custom art."""
    base = _draw_placeholder_face(size)
    mouths = {state: _draw_placeholder_mouth(state, size) for state in MOUTH_STATES}
    return base, mouths


def generate_placeholder_audio(output_path, duration=4.0, sample_rate=22050, seed=0):
    """Synthesize a speech-like waveform (tone bursts separated by silence) as a WAV file."""
    rng = np.random.default_rng(seed)
    n_samples = int(duration * sample_rate)
    t = np.arange(n_samples) / sample_rate
    signal = np.zeros(n_samples)

    n_words = max(1, int(duration * 2))
    word_len = max(1, n_samples // (n_words * 2))
    for i in range(n_words):
        start = min(i * word_len * 2, n_samples)
        end = min(start + word_len, n_samples)
        if start >= end:
            continue
        freq = rng.uniform(140, 220)
        envelope = np.hanning(end - start)
        signal[start:end] += np.sin(2 * math.pi * freq * t[start:end]) * envelope

    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / peak
    pcm = (signal * 32767 * 0.8).astype(np.int16)

    output_path = Path(output_path)
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())
    return output_path


# ---------------------------------------------------------------------------
# Video assembly
# ---------------------------------------------------------------------------

def _mux_audio(silent_video_path, audio_path, output_path):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg_exe, "-y",
            "-i", str(silent_video_path),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(output_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def create_talking_video(output_path, character_dir=None, audio_path=None, fps=24):
    """Render a talking-head video and save it to ``output_path``.

    If ``character_dir`` or ``audio_path`` are omitted, a placeholder
    character and/or a synthesized placeholder audio track are generated
    automatically so the whole pipeline can be exercised immediately.
    """
    import imageio.v2 as imageio

    tmp_dir = Path(tempfile.mkdtemp(prefix="lipsync_"))
    try:
        base, mouths = load_character(character_dir) if character_dir else generate_placeholder_character()

        if not audio_path:
            audio_path = tmp_dir / "placeholder_audio.wav"
            generate_placeholder_audio(audio_path)

        amplitudes = analyze_amplitude(audio_path, fps)
        envelope = envelope_follow(amplitudes)
        silent_video_path = tmp_dir / "silent.mp4"

        with imageio.get_writer(str(silent_video_path), fps=fps, macro_block_size=None) as writer:
            for openness in envelope:
                mouth = blend_mouth_overlay(mouths, openness)
                frame = compose_frame(base, mouth)
                writer.append_data(np.asarray(frame))

        _mux_audio(silent_video_path, audio_path, output_path)
        return Path(output_path)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a simple 2D talking video whose mouth moves in sync with audio volume."
    )
    parser.add_argument(
        "-c", "--character-dir",
        help="Folder with base.png, mouth_closed.png, mouth_mid.png, mouth_open.png "
             "(all the same size). Omit to use a built-in placeholder character.",
    )
    parser.add_argument(
        "-a", "--audio",
        help="Path to a speech audio file (wav/mp3/...). Omit to use a generated placeholder track.",
    )
    parser.add_argument("-o", "--output", default="talking.mp4", help="Path to the output video file")
    parser.add_argument("-f", "--fps", type=int, default=24, help="Frames per second")
    return parser.parse_args()


def main():
    args = parse_args()
    output = create_talking_video(
        args.output,
        character_dir=args.character_dir,
        audio_path=args.audio,
        fps=args.fps,
    )
    print(f"Saved talking video to {output}")


if __name__ == "__main__":
    main()
