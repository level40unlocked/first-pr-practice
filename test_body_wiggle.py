import os
import tempfile
import unittest

import numpy as np
from PIL import Image

from body_wiggle import (
    _detect_background_color,
    create_wiggle_video,
    generate_wiggle_poses,
)


def _make_test_character(w=100, h=150, bg=(220, 220, 220)):
    img = Image.new("RGB", (w, h), bg)
    for y in range(h // 3, h):
        for x in range(w // 3, 2 * w // 3):
            img.putpixel((x, y), (40, 60, 120))
    return img


class DetectBackgroundColorTests(unittest.TestCase):
    def test_detects_uniform_corner_color(self):
        img = _make_test_character(bg=(200, 210, 220))
        self.assertEqual(_detect_background_color(img), (200, 210, 220))


class GenerateWigglePosesTests(unittest.TestCase):
    def test_returns_four_same_size_poses(self):
        img = _make_test_character()
        poses = generate_wiggle_poses(img)
        self.assertEqual(len(poses), 4)
        for pose in poses:
            self.assertEqual(pose.size, img.size)

    def test_first_and_third_pose_are_neutral_and_identical(self):
        img = _make_test_character()
        poses = generate_wiggle_poses(img, amplitude_px=8, tilt_deg=2, sway_px=3)
        np.testing.assert_array_equal(np.asarray(poses[0]), np.asarray(poses[2]))

    def test_lean_poses_differ_from_neutral(self):
        img = _make_test_character()
        poses = generate_wiggle_poses(img, amplitude_px=8, tilt_deg=2, sway_px=3)
        self.assertFalse(np.array_equal(np.asarray(poses[0]), np.asarray(poses[1])))
        self.assertFalse(np.array_equal(np.asarray(poses[0]), np.asarray(poses[3])))

    def test_background_fills_exposed_edges_not_clipped_or_black(self):
        img = _make_test_character(bg=(219, 219, 219))
        poses = generate_wiggle_poses(img, amplitude_px=12, tilt_deg=3, sway_px=5)
        # a corner that is background in the neutral pose should still look
        # like the same background after the shift/rotation, not black
        corner = poses[1].getpixel((2, 2))
        self.assertLess(sum(abs(a - b) for a, b in zip(corner, (219, 219, 219))), 60)


class CreateWiggleVideoTests(unittest.TestCase):
    def test_creates_a_non_empty_video(self):
        img = _make_test_character()
        with tempfile.TemporaryDirectory() as tmp_dir:
            image_path = os.path.join(tmp_dir, "character.png")
            output_path = os.path.join(tmp_dir, "output.mp4")
            img.save(image_path)

            create_wiggle_video(output_path, image_path, fps=8, step_frames=2, duration=0.5)

            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)


if __name__ == "__main__":
    unittest.main()
