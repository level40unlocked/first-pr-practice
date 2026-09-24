"""Turn a still 2D image into a short video with a simple pan/zoom (Ken Burns) animation."""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

EFFECTS = ("zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down")


def _lerp(a, b, t):
    return a + (b - a) * t


def _ease_in_out(t):
    return t * t * (3 - 2 * t)


def compute_frame(image, t, effect="zoom_in", zoom=1.15):
    """Return a single animation frame as a PIL Image.

    ``t`` is the animation progress in [0, 1]. The frame is produced by
    cropping a window out of ``image`` and resizing it back to the original
    size, which creates the pan/zoom illusion when frames are played back to
    back.
    """
    if effect not in EFFECTS:
        raise ValueError(f"Unknown effect: {effect!r}. Choose from {EFFECTS}.")
    if not 0.0 <= t <= 1.0:
        raise ValueError("t must be between 0 and 1")
    if zoom <= 1.0:
        raise ValueError("zoom must be greater than 1.0")

    img_w, img_h = image.size
    max_scale, min_scale = 1.0, 1.0 / zoom

    if effect == "zoom_in":
        scale = _lerp(max_scale, min_scale, t)
    elif effect == "zoom_out":
        scale = _lerp(min_scale, max_scale, t)
    else:
        scale = min_scale

    crop_w, crop_h = img_w * scale, img_h * scale
    half_w, half_h = crop_w / 2, crop_h / 2
    cx, cy = img_w / 2, img_h / 2

    if effect == "pan_left":
        cx = _lerp(img_w - half_w, half_w, t)
    elif effect == "pan_right":
        cx = _lerp(half_w, img_w - half_w, t)
    elif effect == "pan_up":
        cy = _lerp(img_h - half_h, half_h, t)
    elif effect == "pan_down":
        cy = _lerp(half_h, img_h - half_h, t)

    box = (cx - half_w, cy - half_h, cx + half_w, cy + half_h)
    return image.crop(box).resize((img_w, img_h), Image.LANCZOS)


def generate_frames(image, duration, fps, effect="zoom_in", zoom=1.15, ease=True):
    """Yield the animation frames as RGB numpy arrays."""
    num_frames = max(1, round(duration * fps))
    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0.0
        if ease:
            t = _ease_in_out(t)
        frame = compute_frame(image, t, effect=effect, zoom=zoom)
        yield np.asarray(frame.convert("RGB"))


def create_video(image_path, output_path, duration=4.0, fps=30, effect="zoom_in", zoom=1.15, ease=True):
    """Render an animated video from a single image and save it to ``output_path``."""
    import imageio.v2 as imageio

    image = Image.open(image_path)
    frames = generate_frames(image, duration, fps, effect=effect, zoom=zoom, ease=ease)
    with imageio.get_writer(output_path, fps=fps, macro_block_size=None) as writer:
        for frame in frames:
            writer.append_data(frame)
    return Path(output_path)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Turn a still 2D image into a short video with a simple pan/zoom animation."
    )
    parser.add_argument("image", help="Path to the source image")
    parser.add_argument("-o", "--output", default="output.mp4", help="Path to the output video file")
    parser.add_argument("-d", "--duration", type=float, default=4.0, help="Video duration in seconds")
    parser.add_argument("-f", "--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("-e", "--effect", choices=EFFECTS, default="zoom_in", help="Animation effect")
    parser.add_argument("-z", "--zoom", type=float, default=1.15, help="Zoom ratio, must be greater than 1.0")
    parser.add_argument("--no-ease", action="store_true", help="Disable ease-in-out easing")
    return parser.parse_args()


def main():
    args = parse_args()
    output = create_video(
        args.image,
        args.output,
        duration=args.duration,
        fps=args.fps,
        effect=args.effect,
        zoom=args.zoom,
        ease=not args.no_ease,
    )
    print(f"Saved animated video to {output}")


if __name__ == "__main__":
    main()
