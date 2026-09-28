from korea_decoded import db, pipeline
from korea_decoded.config import load_config
from korea_decoded.models import FactCheck, RawTopic, ScriptLine, ShortScript

CONFIG = load_config()


def make_script(sensitivity="go"):
    return ShortScript(
        title="Why Naver Beat Google",
        hook_text="Google isn't #1 here",
        pillar="business_tech",
        target_countries=[],
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


def scripted_topic(conn, tmp_path, pillar_title="How Coupang delivers overnight"):
    pipeline.ingest(conn, [RawTopic(source="t", title=pillar_title, url="https://x/9")], CONFIG)
    [(uid, _, _)] = pipeline.write_scripts(conn, FakeWriter(), tmp_path / "out", limit=1)
    return uid


def test_voice_uses_the_pillar_voice_and_records_it(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    uid = scripted_topic(conn, tmp_path)
    used = {}

    class FakeTTS:
        def synthesize(self, text, out_path):
            used["text"] = text
            out_path.with_suffix(".wav").write_bytes(b"x")
            return out_path.with_suffix(".wav")

    def build(voice, config):
        used["voice"] = voice
        return FakeTTS()

    voice, path = pipeline.voice_topic(conn, uid, CONFIG, tmp_path, build)
    assert voice == used["voice"] == "fenrir"  # FakeWriter scripts are business_tech
    assert used["text"] == "Google wins everywhere."
    row = db.get_topic(conn, uid)
    assert (row["status"], row["voice"], row["audio_path"]) == ("voiced", "fenrir", str(path))


def test_voice_refuses_unscripted_topics(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    pipeline.ingest(conn, [RawTopic(source="t", title="Seoul travel tips", url="https://x/8")], CONFIG)
    uid = db.list_topics(conn)[0]["uid"]
    try:
        pipeline.voice_topic(conn, uid, CONFIG, tmp_path, lambda v, c: None)
    except pipeline.PipelineError as e:
        assert "not scripted" in str(e)
    else:
        raise AssertionError("expected PipelineError")


def test_connect_migrates_old_databases(tmp_path):
    import sqlite3
    old = sqlite3.connect(tmp_path / "old.db")
    old.execute("CREATE TABLE topics (uid TEXT PRIMARY KEY, source TEXT NOT NULL, title TEXT NOT NULL, "
                "url TEXT NOT NULL, summary TEXT NOT NULL DEFAULT '', engagement INTEGER NOT NULL DEFAULT 0, "
                "published_at TEXT NOT NULL DEFAULT '', pillar TEXT, score REAL NOT NULL DEFAULT 0, "
                "sensitivity TEXT NOT NULL, sensitivity_reason TEXT NOT NULL DEFAULT '', status TEXT NOT NULL, "
                "script_path TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')))")
    old.close()
    conn = db.connect(tmp_path / "old.db")
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(topics)")}
    assert {"voice", "audio_path", "video_path"} <= cols


def test_comparison_topics_get_the_comparison_pillar_and_countries(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    pipeline.ingest(conn, [RawTopic(source="t", title="Korea vs Japan: convenience store showdown",
                                    url="https://x/10")], CONFIG)
    row = db.list_topics(conn)[0]
    assert row["pillar"] == "korea_vs_world"
    assert row["countries"] == "JP"
