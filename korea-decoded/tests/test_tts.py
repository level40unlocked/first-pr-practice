from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from korea_decoded.config import load_config
from korea_decoded.tts import HiggsfieldTTS, KokoroTTS, TTSError, build_tts, find_audio_url

CONFIG = load_config()


def test_pillars_map_to_the_chosen_voices():
    assert CONFIG.voice_for("society") == "skye"
    assert CONFIG.voice_for("travel") == "skye"
    assert CONFIG.voice_for("economy_money") == "miles"
    assert CONFIG.voice_for("business_tech") == "fenrir"
    assert CONFIG.voice_for(None) == "skye"


def test_skye_uses_seed_speech_and_fenrir_is_local():
    assert CONFIG.voices["skye"]["variant"] == "seed_speech"
    assert CONFIG.voices["fenrir"]["provider"] == "kokoro"


def test_find_audio_url_searches_nested_results():
    result = {"status": "done", "outputs": [{"image": "https://x/a.png"}, {"audio": {"url": "https://x/b.mp3?sig=1"}}]}
    assert find_audio_url(result) == "https://x/b.mp3?sig=1"
    assert find_audio_url({"images": [{"url": "https://x/a.png"}]}) is None


def test_higgsfield_without_application_path_fails_clearly():
    with pytest.raises(TTSError, match="tts_application"):
        build_tts("skye", CONFIG)  # config ships with the path empty until confirmed


def test_higgsfield_synthesize_downloads_audio(tmp_path):
    calls = {}

    def subscribe(application, arguments):
        calls["application"], calls["arguments"] = application, arguments
        return {"audio": {"url": "https://cdn.example/out.mp3"}}

    session = SimpleNamespace(get=lambda url, timeout: SimpleNamespace(content=b"ID3data", raise_for_status=lambda: None))
    tts = HiggsfieldTTS("some/tts/app", "seed_speech", "voice-123",
                        client=SimpleNamespace(subscribe=subscribe), session=session)
    path = tts.synthesize("Hello Korea", tmp_path / "clip")
    assert path == tmp_path / "clip.mp3" and path.read_bytes() == b"ID3data"
    assert calls["arguments"] == {"prompt": "Hello Korea", "variant": "seed_speech",
                                  "voice_type": "preset", "voice_id": "voice-123"}


def test_kokoro_writes_wav(tmp_path):
    engine = SimpleNamespace(create=lambda text, voice, speed, lang: (np.zeros(2400, dtype=np.float32), 24000))
    path = KokoroTTS(Path("unused"), Path("unused"), "am_fenrir", engine=engine).synthesize("hi", tmp_path / "f")
    assert path.suffix == ".wav" and path.stat().st_size > 0


def test_kokoro_missing_model_files_fail_clearly(tmp_path):
    with pytest.raises(TTSError, match="model files missing"):
        KokoroTTS(tmp_path / "nope.onnx", tmp_path / "nope.bin", "am_fenrir")


def test_for_speech_fixes_names_the_voice_would_misread():
    from korea_decoded.tts import for_speech
    rules = {"Master K": "Master Kay"}
    assert for_speech("Good evening, I'm Master K.", rules) == "Good evening, I'm Master Kay."
    assert for_speech("Master Kim and Master Kay stay as they are.", rules) == "Master Kim and Master Kay stay as they are."
    assert load_config().pronunciation["Master K"] == "Master Kay"


def test_each_cast_member_has_a_fixed_voice():
    config = load_config()
    assert config.voice_for_character("anchor") == "miles"
    assert config.voice_for_character("panel") == "juno"
    assert config.cast["anchor"]["label"] == "MASTER K"
    with pytest.raises(KeyError):
        config.voice_for_character("nobody")
