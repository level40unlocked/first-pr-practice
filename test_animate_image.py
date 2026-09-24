import os
import tempfile
import unittest

from PIL import Image

from animate_image import EFFECTS, compute_frame, create_video, generate_frames


def _make_test_image(width=40, height=30):
    return Image.new("RGB", (width, height), color=(120, 200, 50))


class ComputeFrameTests(unittest.TestCase):
    def test_frame_size_matches_source(self):
        image = _make_test_image()
        frame = compute_frame(image, 0.5, effect="zoom_in")
        self.assertEqual(frame.size, image.size)

    def test_all_effects_produce_a_valid_frame(self):
        image = _make_test_image()
        for effect in EFFECTS:
            frame = compute_frame(image, 0.5, effect=effect)
            self.assertEqual(frame.size, image.size)

    def test_rejects_unknown_effect(self):
        with self.assertRaises(ValueError):
            compute_frame(_make_test_image(), 0.5, effect="spin")

    def test_rejects_t_out_of_range(self):
        with self.assertRaises(ValueError):
            compute_frame(_make_test_image(), 1.5, effect="zoom_in")

    def test_rejects_zoom_not_greater_than_one(self):
        with self.assertRaises(ValueError):
            compute_frame(_make_test_image(), 0.5, effect="zoom_in", zoom=1.0)


class GenerateFramesTests(unittest.TestCase):
    def test_frame_count_matches_duration_and_fps(self):
        frames = list(generate_frames(_make_test_image(), duration=1.0, fps=10))
        self.assertEqual(len(frames), 10)

    def test_frames_are_numpy_arrays_with_expected_shape(self):
        frames = list(generate_frames(_make_test_image(40, 30), duration=0.5, fps=4))
        for frame in frames:
            self.assertEqual(frame.shape, (30, 40, 3))


class CreateVideoTests(unittest.TestCase):
    def test_creates_a_non_empty_video_file(self):
        image = _make_test_image()
        with tempfile.TemporaryDirectory() as tmp_dir:
            image_path = os.path.join(tmp_dir, "source.png")
            output_path = os.path.join(tmp_dir, "output.mp4")
            image.save(image_path)

            create_video(image_path, output_path, duration=0.3, fps=5)

            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)


if __name__ == "__main__":
    unittest.main()
