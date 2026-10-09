from types import SimpleNamespace

import pytest

from korea_decoded.config import load_config
from korea_decoded.scriptwriter import ScriptError, ScriptWriter, build_system_prompt

from test_pipeline import make_script

CONFIG = load_config()
TOPIC = {"uid": "abc", "title": "Naver vs Google", "source": "t", "url": "https://x",
         "pillar": "business_tech", "summary": ""}


class FakeMessages:
    def __init__(self, response):
        self.response = response
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.response


def fake_client(stop_reason="end_turn", text=None):
    content = [] if text is None else [SimpleNamespace(type="text", text=text)]
    messages = FakeMessages(SimpleNamespace(stop_reason=stop_reason, content=content))
    return SimpleNamespace(beta=SimpleNamespace(messages=messages)), messages


def test_system_prompt_includes_all_approved_examples():
    prompt = build_system_prompt(CONFIG)
    assert "Four Eyes Report" in prompt
    for title in ("Jeonse", "Suneung", "Naver", "Convenience", "Baby Comeback"):
        assert title in prompt


def test_write_parses_structured_output():
    client, messages = fake_client(text=make_script().model_dump_json())
    script = ScriptWriter(CONFIG, client=client).write(TOPIC)
    assert script.title == "Why Naver Beat Google"
    fmt = messages.kwargs["output_config"]["format"]
    assert fmt["type"] == "json_schema"
    assert fmt["schema"]["additionalProperties"] is False


@pytest.mark.parametrize("stop_reason", ["refusal", "max_tokens"])
def test_write_raises_on_unusable_stop_reason(stop_reason):
    client, _ = fake_client(stop_reason=stop_reason, text="{}")
    with pytest.raises(ScriptError):
        ScriptWriter(CONFIG, client=client).write(TOPIC)
