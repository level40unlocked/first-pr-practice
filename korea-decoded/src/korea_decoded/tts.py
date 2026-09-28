"""Text-to-speech providers. Which voice a script gets is decided by its pillar
(config: [voice_assignment]); each voice names its provider in [voices.*]."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import requests

from korea_decoded.config import PROJECT_ROOT, ChannelConfig

AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac")


class TTSError(RuntimeError):
    pass


class TTS(Protocol):
    def synthesize(self, text: str, out_path: Path) -> Path: ...


def find_audio_url(result) -> str | None:
    """Higgsfield result payloads differ per application, so search for the first audio URL."""
    if isinstance(result, str):
        return result if result.startswith("http") and result.split("?")[0].lower().endswith(AUDIO_EXTENSIONS) else None
    if isinstance(result, dict):
        values = result.values()
    elif isinstance(result, list):
        values = result
    else:
        return None
    for value in values:
        url = find_audio_url(value)
        if url:
            return url
    return None


class HiggsfieldTTS:
    """Higgsfield text2speech_v2 through the official SDK (HF_KEY or HF_API_KEY/HF_API_SECRET).

    The argument names mirror what Higgsfield's own tools accept for this model
    (prompt, variant, voice_type, voice_id); confirm them against the API docs on
    the first real run.
    """

    def __init__(self, application: str, variant: str, voice_id: str,
                 voice_type: str = "preset", client=None, session: requests.Session | None = None):
        if not application:
            raise TTSError(
                "Higgsfield TTS application path is not set: fill [higgsfield].tts_application "
                "in config/channel.toml (see https://docs.higgsfield.ai)"
            )
        if client is None:
            import higgsfield_client as client
        self.client = client
        self.application = application
        self.arguments = {"variant": variant, "voice_type": voice_type, "voice_id": voice_id}
        self.session = session or requests.Session()

    def synthesize(self, text: str, out_path: Path) -> Path:
        result = self.client.subscribe(self.application, arguments={"prompt": text, **self.arguments})
        url = find_audio_url(result)
        if not url:
            raise TTSError(f"no audio URL in Higgsfield result: {str(result)[:300]}")
        resp = self.session.get(url, timeout=120)
        resp.raise_for_status()
        out_path = out_path.with_suffix(Path(url.split("?")[0]).suffix or ".mp3")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(resp.content)
        return out_path


class KokoroTTS:
    """Free, local Kokoro (Apache 2.0) via kokoro-onnx."""

    def __init__(self, model_path: Path, voices_path: Path, voice: str, speed: float = 1.0, engine=None):
        if engine is None:
            if not model_path.exists() or not voices_path.exists():
                raise TTSError(
                    f"Kokoro model files missing ({model_path}, {voices_path}); download them from "
                    "https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0"
                )
            from kokoro_onnx import Kokoro
            engine = Kokoro(str(model_path), str(voices_path))
        self.engine = engine
        self.voice = voice
        self.speed = speed

    def synthesize(self, text: str, out_path: Path) -> Path:
        import soundfile as sf

        samples, sample_rate = self.engine.create(text, voice=self.voice, speed=self.speed, lang="en-us")
        out_path = out_path.with_suffix(".wav")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(out_path, samples, sample_rate)
        return out_path


def build_tts(voice_name: str, config: ChannelConfig) -> TTS:
    try:
        spec = config.voices[voice_name]
    except KeyError:
        raise TTSError(f"voice '{voice_name}' is not defined in [voices.*]") from None
    provider = spec.get("provider")
    if provider == "higgsfield":
        return HiggsfieldTTS(
            application=config.higgsfield.get("tts_application", ""),
            variant=spec["variant"],
            voice_id=spec["voice_id"],
            voice_type=spec.get("voice_type", "preset"),
        )
    if provider == "kokoro":
        return KokoroTTS(
            model_path=PROJECT_ROOT / config.kokoro.get("model_path", "models/kokoro-v1.0.onnx"),
            voices_path=PROJECT_ROOT / config.kokoro.get("voices_path", "models/voices-v1.0.bin"),
            voice=spec["voice"],
            speed=float(spec.get("speed", 1.0)),
        )
    raise TTSError(f"unknown TTS provider '{provider}' for voice '{voice_name}'")
