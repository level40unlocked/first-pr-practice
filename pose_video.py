"""Automate a simple 2D "moving" video: cycle through a handful of drawn poses.

This is the same trick as lipsync_video.py's mouth-shape switching, applied
to whole-body poses: no rigging, no rotation math, no smooth interpolation.
A small set of complete pose images (e.g. "legs apart" / "legs together"
for a walk cycle) is cycled on a fixed cadence, which reads as simple, even
deliberately choppy, movement -- enough to say "this character is moving,"
not a smooth Disney-style walk cycle.
"""

import argparse
import shutil
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from lipsync_video import _ensure_wav, _mux_audio


# ---------------------------------------------------------------------------
# Pose loading
# ---------------------------------------------------------------------------

def load_poses(pose_dir):
    """Load ``pose_*.png`` files from a folder, cycled in sorted filename order."""
    pose_dir = Path(pose_dir)
    paths = sorted(pose_dir.glob("pose_*.png"))
    if not paths:
        raise ValueError(f"no pose_*.png files found in {pose_dir}")

    poses = [Image.open(path).convert("RGB") for path in paths]
    size = poses[0].size
    for path, pose in zip(paths, poses):
        if pose.size != size:
            raise ValueError(f"{path.name} must match the size of {paths[0].name} ({size})")
    return poses


def iter_pose_frames(poses, total_frames, step_frames):
    """Yield one pose (as an RGB numpy array) per video frame.

    Poses are cycled in order, holding each one for ``step_frames`` frames
    before switching to the next -- a higher ``step_frames`` reads as
    slower, choppier movement; a lower one reads as faster movement.
    """
    step_frames = max(1, step_frames)
    n = len(poses)
    for i in range(total_frames):
        pose = poses[(i // step_frames) % n]
        yield np.asarray(pose)


# ---------------------------------------------------------------------------
# Placeholder poses (used when the user hasn't supplied their own)
# ---------------------------------------------------------------------------

def _draw_placeholder_pose(legs_apart, size=(400, 500)):
    w, h = size
    bg = (246, 241, 230)
    ink = (30, 24, 18)
    shirt = (70, 100, 170)
    skin = (245, 202, 170)

    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)
    cx, hip_y = w // 2, int(h * 0.6)

    draw.ellipse((cx - 45, 60, cx + 45, 150), fill=skin, outline=ink, width=4)
    draw.rectangle((cx - 55, 150, cx + 55, hip_y), fill=shirt, outline=ink, width=4)
    draw.line((cx - 55, 200, cx - 90, 260), fill=shirt, width=18)
    draw.line((cx + 55, 200, cx + 90, 260), fill=shirt, width=18)

    foot_y = h - 60
    if legs_apart:
        draw.line((cx - 10, hip_y, cx - 60, foot_y), fill=ink, width=20)
        draw.line((cx + 10, hip_y, cx + 60, foot_y), fill=ink, width=20)
    else:
        draw.line((cx - 10, hip_y, cx - 15, foot_y), fill=ink, width=20)
        draw.line((cx + 10, hip_y, cx + 15, foot_y), fill=ink, width=20)

    return img


def generate_placeholder_poses():
    """Build a simple built-in 2-pose walk cycle so the pipeline can run without custom art."""
    return [_draw_placeholder_pose(True), _draw_placeholder_pose(False)]


# ---------------------------------------------------------------------------
# Video assembly
# ---------------------------------------------------------------------------

def _audio_duration(audio_path):
    wav_path, tmp_to_clean = _ensure_wav(audio_path)
    try:
        with wave.open(wav_path, "rb") as wav_file:
            return wav_file.getnframes() / wav_file.getframerate()
    finally:
        if tmp_to_clean:
            Path(tmp_to_clean).unlink(missing_ok=True)


def render_pose_video(output_path, poses, audio_path=None, fps=8, step_frames=4, duration=None):
    """Render a video that cycles through an already-built list of pose images.

    This is the shared assembly step behind ``create_pose_video`` (poses
    loaded from a folder or placeholder) and other pose sources such as
    ``body_wiggle.py`` (poses derived from a single image). Duration comes
    from ``audio_path`` if given, otherwise from ``duration``, otherwise
    from three full cycles through the poses.
    """
    import imageio.v2 as imageio

    tmp_dir = Path(tempfile.mkdtemp(prefix="pose_"))
    try:
        if audio_path:
            duration = _audio_duration(audio_path)
        elif duration is None:
            duration = len(poses) * step_frames / fps * 3

        total_frames = max(1, round(duration * fps))
        silent_video_path = tmp_dir / "silent.mp4"

        with imageio.get_writer(str(silent_video_path), fps=fps, macro_block_size=None) as writer:
            for frame in iter_pose_frames(poses, total_frames, step_frames):
                writer.append_data(frame)

        if audio_path:
            _mux_audio(silent_video_path, audio_path, output_path)
        else:
            shutil.move(str(silent_video_path), str(output_path))
        return Path(output_path)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def create_pose_video(output_path, pose_dir=None, audio_path=None, fps=8, step_frames=4, duration=None):
    """Render a simple pose-cycling video and save it to ``output_path``.

    If ``pose_dir`` is omitted, a built-in placeholder walk cycle is used.
    """
    poses = load_poses(pose_dir) if pose_dir else generate_placeholder_poses()
    return render_pose_video(output_path, poses, audio_path=audio_path, fps=fps, step_frames=step_frames, duration=duration)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a simple 2D video that cycles through a handful of drawn poses "
                    "(e.g. a walk cycle), with no rigging or smooth interpolation."
    )
    parser.add_argument(
        "-p", "--pose-dir",
        help="Folder with pose_*.png files, all the same size, cycled in sorted filename order "
             "(e.g. pose_01.png, pose_02.png). Omit to use a built-in placeholder walk cycle.",
    )
    parser.add_argument(
        "-a", "--audio",
        help="Optional audio file to mux in; also sets the video's duration.",
    )
    parser.add_argument("-o", "--output", default="pose.mp4", help="Path to the output video file")
    parser.add_argument("-f", "--fps", type=int, default=8, help="Frames per second")
    parser.add_argument(
        "--step-frames", type=int, default=4,
        help="How many frames each pose holds before switching to the next. "
             "Higher = slower/choppier movement, lower = faster.",
    )
    parser.add_argument(
        "-d", "--duration", type=float, default=None,
        help="Video duration in seconds (ignored if --audio is given). "
             "Defaults to three full cycles through the poses.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    output = create_pose_video(
        args.output,
        pose_dir=args.pose_dir,
        audio_path=args.audio,
        fps=args.fps,
        step_frames=args.step_frames,
        duration=args.duration,
    )
    print(f"Saved pose video to {output}")


if __name__ == "__main__":
    main()
