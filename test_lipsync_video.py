import math
import os
import tempfile
import unittest
import wave

import numpy as np

from lipsync_video import (
    MOUTH_STATES,
    analyze_amplitude,
    blend_mouth_overlay,
    compose_frame,
    create_talking_video,
    envelope_follow,
    generate_placeholder_audio,
    generate_placeholder_character,
    select_mouth_state,
)


def _write_wav(path, samples, sample_rate=22050):
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())


class SelectMouthStateTests(unittest.TestCase):
    def test_low_amplitude_is_closed(self):
        self.assertEqual(select_mouth_state(0.0), "closed")

    def test_mid_amplitude_is_mid(self):
        self.assertEqual(select_mouth_state(0.3), "mid")

    def test_high_amplitude_is_open(self):
        self.assertEqual(select_mouth_state(0.9), "open")


class AnalyzeAmplitudeTests(unittest.TestCase):
    def test_frame_count_matches_duration_and_fps(self):
        sample_rate = 22050
        duration = 1.0
        samples = np.zeros(int(sample_rate * duration))
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "silence.wav")
            _write_wav(path, samples, sample_rate)
            amplitudes = analyze_amplitude(path, fps=10, smoothing=1)
        self.assertEqual(len(amplitudes), 10)

    def test_loud_segment_has_higher_amplitude_than_silence(self):
        sample_rate = 22050
        duration = 1.0
        t = np.arange(int(sample_rate * duration)) / sample_rate
        samples = np.zeros_like(t)
        loud_start, loud_end = int(0.4 * sample_rate), int(0.6 * sample_rate)
        samples[loud_start:loud_end] = np.sin(2 * math.pi * 200 * t[loud_start:loud_end])

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "burst.wav")
            _write_wav(path, samples, sample_rate)
            amplitudes = analyze_amplitude(path, fps=10, smoothing=1)

        self.assertGreater(amplitudes[5], amplitudes[0])


class PlaceholderAssetTests(unittest.TestCase):
    def test_placeholder_character_mouths_match_base_size(self):
        base, mouths = generate_placeholder_character(size=64)
        self.assertEqual(set(mouths.keys()), set(MOUTH_STATES))
        for mouth in mouths.values():
            self.assertEqual(mouth.size, base.size)

    def test_placeholder_audio_has_expected_duration(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "audio.wav")
            generate_placeholder_audio(path, duration=0.5, sample_rate=8000)
            with wave.open(path, "rb") as wav_file:
                duration = wav_file.getnframes() / wav_file.getframerate()
            self.assertAlmostEqual(duration, 0.5, places=2)


class EnvelopeFollowTests(unittest.TestCase):
    def test_rises_quickly_and_falls_slowly(self):
        amplitudes = [1.0] + [0.0] * 10
        envelope = envelope_follow(amplitudes, attack=0.6, release=0.15)
        self.assertAlmostEqual(envelope[0], 0.6)
        # release is slower than attack, so it should still be above zero for a while
        self.assertGreater(envelope[3], 0.1)

    def test_stays_at_zero_for_silence(self):
        envelope = envelope_follow([0.0] * 5)
        self.assertTrue(all(v == 0.0 for v in envelope))


class BlendMouthOverlayTests(unittest.TestCase):
    def test_zero_openness_matches_closed_mouth(self):
        _, mouths = generate_placeholder_character(size=64)
        blended = blend_mouth_overlay(mouths, 0.0)
        self.assertEqual(np.asarray(blended).tolist(), np.asarray(mouths["closed"]).tolist())

    def test_full_openness_matches_open_mouth(self):
        _, mouths = generate_placeholder_character(size=64)
        blended = blend_mouth_overlay(mouths, 1.0)
        self.assertEqual(np.asarray(blended).tolist(), np.asarray(mouths["open"]).tolist())

    def test_mid_openness_matches_mid_mouth(self):
        _, mouths = generate_placeholder_character(size=64)
        blended = blend_mouth_overlay(mouths, 0.5)
        self.assertEqual(np.asarray(blended).tolist(), np.asarray(mouths["mid"]).tolist())


class ComposeFrameTests(unittest.TestCase):
    def test_composed_frame_matches_base_size(self):
        base, mouths = generate_placeholder_character(size=64)
        frame = compose_frame(base, mouths["open"])
        self.assertEqual(frame.size, base.size)
        self.assertEqual(frame.mode, "RGB")

    def test_rejects_mismatched_mouth_size(self):
        base, _ = generate_placeholder_character(size=64)
        _, other_mouths = generate_placeholder_character(size=32)
        with self.assertRaises(ValueError):
            compose_frame(base, other_mouths["open"])


class CreateTalkingVideoTests(unittest.TestCase):
    def test_creates_a_non_empty_video_with_placeholder_assets(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            audio_path = os.path.join(tmp_dir, "audio.wav")
            generate_placeholder_audio(audio_path, duration=0.5)
            output_path = os.path.join(tmp_dir, "output.mp4")

            create_talking_video(output_path, audio_path=audio_path, fps=8)

            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)


if __name__ == "__main__":
    unittest.main()
