import os
import tempfile
import unittest

import numpy as np
from PIL import Image

from lipsync_video import generate_placeholder_audio
from pose_video import (
    create_pose_video,
    generate_placeholder_poses,
    iter_pose_frames,
    load_poses,
)


def _write_pose(path, color):
    Image.new("RGB", (20, 30), color=color).save(path)


class LoadPosesTests(unittest.TestCase):
    def test_loads_poses_in_sorted_order(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            _write_pose(os.path.join(tmp_dir, "pose_02.png"), (0, 255, 0))
            _write_pose(os.path.join(tmp_dir, "pose_01.png"), (255, 0, 0))

            poses = load_poses(tmp_dir)

            self.assertEqual(len(poses), 2)
            self.assertEqual(poses[0].getpixel((0, 0)), (255, 0, 0))
            self.assertEqual(poses[1].getpixel((0, 0)), (0, 255, 0))

    def test_raises_when_no_poses_found(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(ValueError):
                load_poses(tmp_dir)

    def test_raises_on_mismatched_pose_size(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            _write_pose(os.path.join(tmp_dir, "pose_01.png"), (255, 0, 0))
            Image.new("RGB", (10, 10), color=(0, 255, 0)).save(os.path.join(tmp_dir, "pose_02.png"))

            with self.assertRaises(ValueError):
                load_poses(tmp_dir)


class IterPoseFramesTests(unittest.TestCase):
    def test_holds_each_pose_for_step_frames_before_switching(self):
        poses = [Image.new("RGB", (4, 4), color=(255, 0, 0)), Image.new("RGB", (4, 4), color=(0, 0, 255))]

        frames = list(iter_pose_frames(poses, total_frames=6, step_frames=2))

        expected_colors = [(255, 0, 0), (255, 0, 0), (0, 0, 255), (0, 0, 255), (255, 0, 0), (255, 0, 0)]
        for frame, color in zip(frames, expected_colors):
            self.assertTrue(np.all(frame[0, 0] == color))

    def test_frame_count_matches_total_frames(self):
        poses = [Image.new("RGB", (4, 4), color=(1, 2, 3))]
        frames = list(iter_pose_frames(poses, total_frames=5, step_frames=3))
        self.assertEqual(len(frames), 5)


class PlaceholderPosesTests(unittest.TestCase):
    def test_returns_two_same_size_poses(self):
        poses = generate_placeholder_poses()
        self.assertEqual(len(poses), 2)
        self.assertEqual(poses[0].size, poses[1].size)


class CreatePoseVideoTests(unittest.TestCase):
    def test_creates_a_non_empty_video_with_placeholder_poses(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "output.mp4")

            create_pose_video(output_path, fps=8, step_frames=2, duration=0.5)

            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)

    def test_duration_follows_audio_when_given(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            audio_path = os.path.join(tmp_dir, "audio.wav")
            generate_placeholder_audio(audio_path, duration=0.5)
            output_path = os.path.join(tmp_dir, "output.mp4")

            create_pose_video(output_path, audio_path=audio_path, fps=8, step_frames=2)

            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)


if __name__ == "__main__":
    unittest.main()
