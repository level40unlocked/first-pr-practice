import json
from types import SimpleNamespace

from PIL import Image

from korea_decoded import visuals
from korea_decoded.visuals import (AIImageSource, PexelsSource, Scene, VisualPlan, VisualPlanner,
                                   gather, make_card, normalize_plan)
from test_pipeline import make_script


def scene(line, source="stock", **kw):
    base = dict(stock_query="", ai_prompt="", card_text="", card_subtext="")
    base.update(kw)
    return Scene(line=line, source=source, **base)


class FakeResp:
    def __init__(self, json_data=None, content=b""):
        self._json, self.content = json_data, content

    def json(self):
        return self._json

    def raise_for_status(self):
        pass


def png_bytes():
    import io
    buf = io.BytesIO()
    Image.new("RGB", (10, 20), "green").save(buf, format="PNG")
    return buf.getvalue()


def test_card_is_a_vertical_image(tmp_path):
    path = make_card("2.1 vs 0.7", "children per woman", tmp_path / "c")
    assert Image.open(path).size == (1080, 1920)


def test_plan_gets_one_scene_per_line_in_order():
    script = make_script()  # one line
    plan = VisualPlan(scenes=[scene(5, stock_query="ignored"), ])
    normalized = normalize_plan(plan, script)
    assert [s.line for s in normalized.scenes] == [0]
    assert normalized.scenes[0].source == "card"


def test_planner_sends_every_line_and_uses_low_effort():
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        plan = VisualPlan(scenes=[scene(0, stock_query="world map")])
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=plan.model_dump_json())])

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
    plan = VisualPlanner(client).plan(make_script())
    assert plan.scenes[0].stock_query == "world map"
    assert "Google wins everywhere." in captured["messages"][0]["content"]
    assert captured["output_config"]["effort"] == "low"


def test_pexels_skips_photos_already_used(tmp_path):
    photos = {"photos": [{"id": 1, "src": {"large2x": "https://p/1.jpg"}, "photographer": "A", "url": "u1"},
                         {"id": 2, "src": {"large2x": "https://p/2.jpg"}, "photographer": "B", "url": "u2"}]}
    session = SimpleNamespace(get=lambda url, **kw: FakeResp(photos) if "search" in url else FakeResp(content=b"jpg"))
    source = PexelsSource("key", session)
    first = source.fetch(scene(0, stock_query="seoul"), tmp_path / "a")
    second = source.fetch(scene(1, stock_query="seoul"), tmp_path / "b")
    assert "Photo by A" in first[1] and "Photo by B" in second[1]


def test_ai_source_reads_documented_result_shape(tmp_path):
    client = SimpleNamespace(subscribe=lambda app, arguments: {"images": [{"url": "https://x/img.png"}]})
    session = SimpleNamespace(get=lambda url, **kw: FakeResp(content=png_bytes()))
    path, credit = AIImageSource("app", {"aspect_ratio": "9:16"}, client, session).fetch(
        scene(0, "ai", ai_prompt="police escort"), tmp_path / "x")
    assert path.suffix == ".png" and credit.startswith("AI image")


def test_gather_falls_back_to_cards_and_records_credits(tmp_path):
    class Broken:
        def fetch(self, scene, out_path):
            raise RuntimeError("network down")

    class Stock:
        def fetch(self, scene, out_path):
            if not scene.stock_query:  # like PexelsSource
                return None
            p = out_path.with_suffix(".jpg")
            Image.new("RGB", (10, 20)).save(p)
            return p, "stock credit"

    plan = VisualPlan(scenes=[scene(0, stock_query="seoul"), scene(1, "ai", ai_prompt="robot"),
                              scene(2, "card", card_text="$20 vs $30")])
    logs = []
    paths, credits = gather(plan, tmp_path / "v", {"stock": Stock(), "ai": Broken()}, log=logs.append)
    assert [c.source for c in credits] == ["stock", "card", "card"]
    assert [p.stem for p in paths] == ["00", "01", "02"]
    assert any("ai failed" in m for m in logs)
    assert json.loads((tmp_path / "v" / "credits.json").read_text())[0]["detail"] == "stock credit"
    assert visuals.existing_images(tmp_path / "v") == paths


def test_no_keys_means_no_remote_sources(monkeypatch):
    monkeypatch.delenv("PEXELS_API_KEY", raising=False)
    cfg = SimpleNamespace(visuals={"allow_ai": False})
    assert visuals.build_sources(cfg) == {}
