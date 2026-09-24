"""Automate a 2D "talking" video where the head nods independently of a static body.

This combines two already-validated, cut-free tricks instead of rotating
limbs out of a single merged image (which turned out fragile -- clipped
fingers, crossed legs, visible seams):

- The head is its own circular layer (rotation-invariant silhouette --
  a circle looks the same at any angle, so it can nod/tilt with zero seam
  risk, unlike a rectangular or limb-shaped cutout).
- The mouth swaps between a few pre-drawn shapes, same as lipsync_video.py,
  composited onto the head *before* the head is rotated, so the mouth
  always rides along with the head's motion.

The body below the neck never moves or gets cut.
"""

import argparse
import shutil
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from lipsync_video import (
    MOUTH_STATES,
    _draw_placeholder_face,
    _draw_placeholder_mouth,
    _mux_audio,
    analyze_amplitude,
    envelope_follow,
    generate_placeholder_audio,
    select_mouth_state,
)


def load_head_character(character_dir):
    """Load a head/body-split character: body.png, head.png, mouth_<state>.png.

    ``head.png`` must be a circular cutout (transparent outside the circle)
    so it can be rotated without ever exposing a seam. Its position on
    ``body.png`` is read from ``head_meta.txt`` (written alongside it).
    """
    character_dir = Path(character_dir)
    body = Image.open(character_dir / "body.png").convert("RGBA")
    head = Image.open(character_dir / "head.png").convert("RGBA")
    mouths = {}
    for state in MOUTH_STATES:
        mouth = Image.open(character_dir / f"mouth_{state}.png").convert("RGBA")
        if mouth.size != head.size:
            raise ValueError(f"mouth_{state}.png must match head.png size {head.size}")
        mouths[state] = mouth

    meta_path = character_dir / "head_meta.txt"
    box_str = meta_path.read_text().split("box=")[1].strip().strip("()")
    head_pos = tuple(int(v.strip()) for v in box_str.split(","))[:2]
    return body, head, mouths, head_pos


def _circular_crop(image, center, radius, feather=2, inset=3):
    """Crop a feathered circular piece out of ``image`` -- rotation-invariant silhouette."""
    box = (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)
    piece = image.crop(box)
    mask = Image.new("L", piece.size, 0)
    ImageDraw.Draw(mask).ellipse((inset, inset, piece.size[0] - inset, piece.size[1] - inset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    piece.putalpha(mask)
    return piece, box, mask


def generate_placeholder_head_character(size=480):
    """Build a built-in head/body-split character so the pipeline runs without custom art."""
    face = _draw_placeholder_face(size).convert("RGBA")
    face_rgb_bg = Image.new("RGBA", (size, size), (246, 241, 230, 255))
    face_rgb_bg.alpha_composite(face)

    center = (size // 2, size // 2)
    radius = int(size * 0.47)
    head, box, mask = _circular_crop(face_rgb_bg, center, radius)

    body = face_rgb_bg.copy()
    erase = Image.new("RGBA", head.size, (246, 241, 230, 255))
    erase.putalpha(mask)
    body.alpha_composite(erase, (box[0], box[1]))

    mouths = {}
    for state in MOUTH_STATES:
        mouth_full = _draw_placeholder_mouth(state, size)
        mouths[state] = mouth_full.crop(box)

    return body, head, mouths, (box[0], box[1])


def compose_head(head, mouth_overlay):
    """Layer a mouth shape onto the head, before any rotation is applied."""
    return Image.alpha_composite(head, mouth_overlay)


def nod_schedule(total_frames, step_frames=18, amplitude_deg=6, dy_px=4, dx_px=2):
    """A small 4-step head-nod cycle: neutral, lean-left, neutral, lean-right.

    Returns one ``(angle, dx, dy)`` per frame, holding each state for
    ``step_frames`` frames before switching to the next -- the same
    "hold, then switch" cadence as pose_video.py's poses.
    """
    states = [
        (0.0, 0, 0),
        (-amplitude_deg, -dx_px, -dy_px),
        (0.0, 0, 0),
        (amplitude_deg, dx_px, -dy_px),
    ]
    step_frames = max(1, step_frames)
    return [states[(i // step_frames) % len(states)] for i in range(total_frames)]


def render_frame(body, head_composed, head_pos, angle, dx, dy):
    rotated = head_composed.rotate(angle, resample=Image.BILINEAR)
    canvas = body.copy()
    canvas.alpha_composite(rotated, (head_pos[0] + dx, head_pos[1] + dy))
    return canvas.convert("RGB")


def create_talking_head_video(output_path, character_dir=None, audio_path=None, fps=24,
                               speed=1.0, nod_step_frames=18, nod_amplitude_deg=6):
    """Render a talking video: audio-synced mouth + an independent head nod cycle.

    If ``character_dir`` is omitted, a built-in placeholder head/body character
    is generated so the pipeline can run without custom art.
    """
    import imageio.v2 as imageio

    tmp_dir = Path(tempfile.mkdtemp(prefix="talkinghead_"))
    try:
        if character_dir:
            body, head, mouths, head_pos = load_head_character(character_dir)
        else:
            body, head, mouths, head_pos = generate_placeholder_head_character()

        if not audio_path:
            audio_path = tmp_dir / "placeholder_audio.wav"
            generate_placeholder_audio(audio_path)

        amplitudes = analyze_amplitude(audio_path, fps)
        envelope = envelope_follow(amplitudes, speed=speed)
        total_frames = len(envelope)

        nod_per_frame = nod_schedule(total_frames, step_frames=nod_step_frames, amplitude_deg=nod_amplitude_deg)

        silent_video_path = tmp_dir / "silent.mp4"
        with imageio.get_writer(str(silent_video_path), fps=fps, macro_block_size=None) as writer:
            for i, openness in enumerate(envelope):
                state = select_mouth_state(openness)
                head_composed = compose_head(head, mouths[state])
                angle, dx, dy = nod_per_frame[i]
                frame = render_frame(body, head_composed, head_pos, angle, dx, dy)
                writer.append_data(np.asarray(frame))

        if audio_path:
            _mux_audio(silent_video_path, audio_path, output_path)
        else:
            shutil.move(str(silent_video_path), str(output_path))
        return Path(output_path)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a 2D talking video with an independently nodding head "
                    "(circular layer, no seams) over a static body."
    )
    parser.add_argument("-c", "--character-dir",
                         help="Folder with body.png, head.png, mouth_closed/mid/open.png, head_meta.txt. "
                              "Omit to use a built-in placeholder head/body character.")
    parser.add_argument("-a", "--audio", help="Path to a speech audio file. Omit for a placeholder track.")
    parser.add_argument("-o", "--output", default="talking_head.mp4")
    parser.add_argument("-f", "--fps", type=int, default=24)
    parser.add_argument("-s", "--speed", type=float, default=1.0, help="Mouth reaction speed multiplier")
    parser.add_argument("--nod-step-frames", type=int, default=18,
                         help="How many frames each head-nod state holds before switching")
    parser.add_argument("--nod-amplitude", type=float, default=6, help="Head nod angle in degrees")
    return parser.parse_args()


def main():
    args = parse_args()
    output = create_talking_head_video(
        args.output,
        args.character_dir,
        audio_path=args.audio,
        fps=args.fps,
        speed=args.speed,
        nod_step_frames=args.nod_step_frames,
        nod_amplitude_deg=args.nod_amplitude,
    )
    print(f"Saved talking head video to {output}")


if __name__ == "__main__":
    main()
