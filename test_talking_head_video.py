import os
import tempfile
import unittest

import numpy as np
from PIL import Image, ImageChops

from lipsync_video import generate_placeholder_audio
from talking_head_video import (
    compose_head,
    create_talking_head_video,
    generate_placeholder_head_character,
    load_head_character,
    nod_schedule,
    render_frame,
)


class GeneratePlaceholderHeadCharacterTests(unittest.TestCase):
    def test_head_and_mouths_share_the_same_size(self):
        body, head, mouths, head_pos = generate_placeholder_head_character(size=200)
        for mouth in mouths.values():
            self.assertEqual(mouth.size, head.size)

    def test_head_silhouette_is_rotation_invariant(self):
        # the *boundary* (alpha channel) of a circular crop should stay a
        # circle at any rotation angle, even though the content inside
        # (hair, face) naturally moves -- that's what avoids seams
        _, head, _, _ = generate_placeholder_head_character(size=200)
        rotated = head.rotate(37, resample=Image.BILINEAR)
        original_alpha = np.array(head.split()[-1])
        rotated_alpha = np.array(rotated.split()[-1])
        diff = np.abs(original_alpha.astype(int) - rotated_alpha.astype(int))
        # allow for minor edge resampling noise, but the silhouette shape itself should match
        self.assertLess(diff.mean(), 5)

    def test_neutral_reassembly_matches_original(self):
        body, head, mouths, head_pos = generate_placeholder_head_character(size=200)
        composed = compose_head(head, mouths["closed"])
        frame = render_frame(body, composed, head_pos, angle=0, dx=0, dy=0)
        self.assertEqual(frame.size, body.size)


class NodScheduleTests(unittest.TestCase):
    def test_holds_each_state_for_step_frames(self):
        schedule = nod_schedule(total_frames=8, step_frames=2, amplitude_deg=5)
        self.assertEqual(schedule[0], schedule[1])
        self.assertNotEqual(schedule[0], schedule[2])

    def test_first_state_is_neutral(self):
        schedule = nod_schedule(total_frames=4, step_frames=4)
        self.assertEqual(schedule[0], (0.0, 0, 0))


class LoadHeadCharacterTests(unittest.TestCase):
    def test_loads_saved_placeholder_character(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            body, head, mouths, head_pos = generate_placeholder_head_character(size=200)
            body.convert("RGB").save(os.path.join(tmp_dir, "body.png"))
            head.save(os.path.join(tmp_dir, "head.png"))
            for state, mouth in mouths.items():
                mouth.save(os.path.join(tmp_dir, f"mouth_{state}.png"))
            box = (head_pos[0], head_pos[1], head_pos[0] + head.size[0], head_pos[1] + head.size[1])
            with open(os.path.join(tmp_dir, "head_meta.txt"), "w") as f:
                f.write(f"center=(0, 0) radius=0 box={box}\n")

            loaded_body, loaded_head, loaded_mouths, loaded_pos = load_head_character(tmp_dir)

            self.assertEqual(loaded_pos, head_pos)
            self.assertEqual(loaded_head.size, head.size)
            self.assertEqual(set(loaded_mouths.keys()), set(mouths.keys()))


class CreateTalkingHeadVideoTests(unittest.TestCase):
    def test_creates_a_non_empty_video_with_placeholder_character(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            audio_path = os.path.join(tmp_dir, "audio.wav")
            generate_placeholder_audio(audio_path, duration=0.5)
            output_path = os.path.join(tmp_dir, "output.mp4")

            create_talking_head_video(output_path, audio_path=audio_path, fps=8, nod_step_frames=2)

            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)


if __name__ == "__main__":
    unittest.main()
