"""Automate simple 2D character movement by rigidly transforming ONE whole image.

Cutting a character into limb pieces and rotating them individually is
fragile on real, detailed artwork -- fingers get clipped, legs cross,
seams show at the shoulders (this was tried and it didn't hold up).
Generating a separate AI image per pose avoids the seam problem but costs
money and the character drifts between generations.

This script avoids both: it never cuts the artwork at all. It moves the
*entire* character image as one rigid piece -- a small bounce/rock cycle
(vertical shift + a slight tilt, pivoting near the feet) -- which reads as
"this character is walking/moving" without any risk of limbs looking
disjointed, since nothing is ever separated from anything else. It works
best on art with a flat, uniform background color, which is used to fill
in whatever edge the shift/rotation exposes.
"""

import argparse
from pathlib import Path

from PIL import Image

from pose_video import render_pose_video


def _detect_background_color(image, margin=4):
    """Guess the flat background color by sampling the image's corners."""
    rgb = image.convert("RGB")
    w, h = rgb.size
    corners = [
        rgb.getpixel((margin, margin)),
        rgb.getpixel((w - 1 - margin, margin)),
        rgb.getpixel((margin, h - 1 - margin)),
        rgb.getpixel((w - 1 - margin, h - 1 - margin)),
    ]
    r = sum(c[0] for c in corners) // 4
    g = sum(c[1] for c in corners) // 4
    b = sum(c[2] for c in corners) // 4
    return (r, g, b)


def _rigid_transform(image, bg_color, dx, dy, angle_deg):
    """Rotate the whole image around a pivot near its feet, then shift it.

    The rotation/shift can expose edges beyond the original artwork; those
    are filled with ``bg_color`` so nothing looks cut or clipped.
    """
    w, h = image.size
    pivot = (w / 2, h * 0.95)  # near the bottom edge, roughly where feet meet the ground
    rotated = image.rotate(angle_deg, resample=Image.BICUBIC, center=pivot, fillcolor=bg_color)

    canvas = Image.new("RGB", (w, h), bg_color)
    canvas.paste(rotated, (dx, dy))
    return canvas


def generate_wiggle_poses(image, amplitude_px=10, tilt_deg=2.5, sway_px=4, bg_color=None):
    """Derive a small bounce/rock cycle from a single character image.

    Returns 4 whole-image poses (neutral, lean-left+up, neutral,
    lean-right+up) built purely by rotating/shifting the same source
    image -- no cropping, no per-limb pieces, nothing to misalign.
    """
    image = image.convert("RGB")
    if bg_color is None:
        bg_color = _detect_background_color(image)

    neutral = _rigid_transform(image, bg_color, 0, 0, 0)
    lean_left = _rigid_transform(image, bg_color, -sway_px, -amplitude_px, -tilt_deg)
    lean_right = _rigid_transform(image, bg_color, sway_px, -amplitude_px, tilt_deg)

    return [neutral, lean_left, neutral, lean_right]


def create_wiggle_video(output_path, image_path, audio_path=None, fps=8, step_frames=4, duration=None,
                         amplitude_px=10, tilt_deg=2.5, sway_px=4):
    """Render a bounce/rock movement video derived from a single character image."""
    image = Image.open(image_path)
    poses = generate_wiggle_poses(image, amplitude_px=amplitude_px, tilt_deg=tilt_deg, sway_px=sway_px)
    return render_pose_video(output_path, poses, audio_path=audio_path, fps=fps, step_frames=step_frames, duration=duration)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Animate a single 2D character image with a simple whole-body bounce/rock "
                    "cycle -- no limb cutting, no extra AI generation."
    )
    parser.add_argument("image", help="Path to a character image, ideally on a flat, uniform background")
    parser.add_argument("-a", "--audio", help="Optional audio file to mux in; also sets the video's duration")
    parser.add_argument("-o", "--output", default="wiggle.mp4", help="Path to the output video file")
    parser.add_argument("-f", "--fps", type=int, default=8, help="Frames per second")
    parser.add_argument(
        "--step-frames", type=int, default=4,
        help="How many frames each pose holds before switching. Higher = slower/choppier.",
    )
    parser.add_argument(
        "-d", "--duration", type=float, default=None,
        help="Video duration in seconds (ignored if --audio is given). Defaults to three full cycles.",
    )
    parser.add_argument("--amplitude", type=float, default=10, help="Vertical bounce distance in pixels")
    parser.add_argument("--tilt", type=float, default=2.5, help="Rock/lean angle in degrees")
    parser.add_argument("--sway", type=float, default=4, help="Horizontal sway distance in pixels")
    return parser.parse_args()


def main():
    args = parse_args()
    output = create_wiggle_video(
        args.output,
        args.image,
        audio_path=args.audio,
        fps=args.fps,
        step_frames=args.step_frames,
        duration=args.duration,
        amplitude_px=args.amplitude,
        tilt_deg=args.tilt,
        sway_px=args.sway,
    )
    print(f"Saved wiggle video to {output}")


if __name__ == "__main__":
    main()
