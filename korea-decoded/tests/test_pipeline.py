from korea_decoded import db, pipeline
from korea_decoded.config import load_config
from korea_decoded.models import FactCheck, RawTopic, ScriptLine, ShortScript

CONFIG = load_config()


def make_script(sensitivity="go"):
    return ShortScript(
        title="Why Naver Beat Google",
        hook_text="Google isn't #1 here",
        pillar="business_tech",
        sensitivity=sensitivity,
        sensitivity_reason="neutral tech history" if sensitivity == "go" else "touches a scandal",
        lines=[ScriptLine(en="Google wins everywhere.", ko="구글은 어디서나 이겨.", visual="world map")],
        fact_checks=[FactCheck(claim="Naver is #1 in Korea", where_to_verify="InternetTrend")],
        hashtags=["#Korea", "#Naver"],
    )


class FakeWriter:
    def __init__(self, sensitivity="go"):
        self.sensitivity = sensitivity

    def write(self, topic):
        return make_script(self.sensitivity)


def test_ingest_routes_by_sensitivity_and_dedupes(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    topics = [
        RawTopic(source="t", title="How Naver beat Google in Korea", url="https://x/1", engagement=500),
        RawTopic(source="t", title="Jeonse fraud victims protest in Seoul", url="https://x/2"),
    ]
    assert pipeline.ingest(conn, topics, CONFIG) == {"new": 1, "review": 1, "duplicate": 0}
    assert pipeline.ingest(conn, topics, CONFIG)["duplicate"] == 2

    good = db.list_topics(conn, "new")[0]
    assert good["pillar"] == "business_tech"
    assert db.list_topics(conn, "review")[0]["url"] == "https://x/2"


def test_review_topics_are_not_scripted_until_approved(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    pipeline.ingest(conn, [RawTopic(source="t", title="Crypto scam hits Seoul", url="https://x/3")], CONFIG)
    assert pipeline.write_scripts(conn, FakeWriter(), tmp_path / "out", limit=5) == []

    uid = db.list_topics(conn, "review")[0]["uid"]
    db.set_status(conn, uid, "approved")
    [(_, path, status)] = pipeline.write_scripts(conn, FakeWriter(), tmp_path / "out", limit=5)
    assert status == "scripted"
    text = path.read_text(encoding="utf-8")
    assert "## EN" in text and "## KO" in text and "구글은 어디서나 이겨." in text


def test_model_flag_sends_go_topic_back_to_review(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    pipeline.ingest(conn, [RawTopic(source="t", title="Samsung history", url="https://x/4")], CONFIG)
    [(uid, _, status)] = pipeline.write_scripts(conn, FakeWriter("review"), tmp_path / "out", limit=5)
    assert status == "review"
    row = db.list_topics(conn, "review")[0]
    assert row["uid"] == uid
    assert row["sensitivity_reason"].startswith("model:")
