"""Glue between collectors, scoring, sensitivity rules, the DB and the script writer."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from korea_decoded import db, scoring, sensitivity
from korea_decoded.config import PROJECT_ROOT, ChannelConfig
from korea_decoded.models import RawTopic, ShortScript
from korea_decoded.scriptwriter import ScriptWriter, render_markdown, slugify


def ingest(conn: sqlite3.Connection, topics: list[RawTopic], config: ChannelConfig) -> dict:
    counts = {"new": 0, "review": 0, "duplicate": 0}
    for t in topics:
        pillar = scoring.detect_pillar(t, config)
        check = sensitivity.classify(f"{t.title} {t.summary}", config.negative_keywords)
        status = "review" if check.level == "review" else "new"
        inserted = db.insert_topic(
            conn,
            uid=t.uid,
            source=t.source,
            title=t.title,
            url=t.url,
            summary=t.summary,
            engagement=t.engagement,
            published_at=t.published_at,
            pillar=pillar.key if pillar else None,
            countries=",".join(scoring.detect_countries(t, config)),
            score=scoring.score(t, pillar),
            sensitivity=check.level,
            sensitivity_reason=check.reason,
            status=status,
        )
        counts[status if inserted else "duplicate"] += 1
    return counts


def write_scripts(
    conn: sqlite3.Connection, writer: ScriptWriter, out_dir: Path, limit: int
) -> list[tuple[str, Path, str]]:
    """Writes scripts for the top topics. Returns (uid, path, resulting status) per topic.

    A topic that passed the keyword check can still be flagged by the model; its
    script is saved but the topic goes back to the review queue.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for topic in db.ready_for_script(conn, limit):
        script = writer.write(topic)
        path = out_dir / f"{topic['uid']}-{slugify(script.title)}.md"
        path.write_text(render_markdown(script, topic), encoding="utf-8")
        # Structured copy for the voice and render steps.
        path.with_suffix(".json").write_text(script.model_dump_json(indent=2), encoding="utf-8")

        # A human-approved topic stays approved even if the model flags it.
        flagged = script.sensitivity == "review" and topic["status"] != "approved"
        status = "review" if flagged else "scripted"
        if flagged:
            conn.execute(
                "UPDATE topics SET sensitivity = 'review', sensitivity_reason = ? WHERE uid = ?",
                (f"model: {script.sensitivity_reason}", topic["uid"]),
            )
        db.set_status(conn, topic["uid"], status, script_path=str(path))
        results.append((topic["uid"], path, status))
    return results


class PipelineError(RuntimeError):
    pass


def load_script(topic) -> ShortScript:
    if not topic["script_path"]:
        raise PipelineError(f"topic {topic['uid']} has no script yet")
    json_path = Path(topic["script_path"]).with_suffix(".json")
    if not json_path.exists():
        raise PipelineError(f"structured script missing: {json_path} (regenerate with `write`)")
    return ShortScript.model_validate_json(json_path.read_text(encoding="utf-8"))


def voice_topic(conn: sqlite3.Connection, uid: str, config: ChannelConfig, out_dir: Path,
                build_tts, voice: str | None = None) -> tuple[str, Path]:
    """Narrates a fact-checked script with the voice assigned to its pillar."""
    topic = db.get_topic(conn, uid)
    if topic is None:
        raise PipelineError(f"unknown topic: {uid}")
    if topic["status"] not in ("scripted", "voiced", "rendered"):
        raise PipelineError(f"topic {uid} is '{topic['status']}', not scripted")
    script = load_script(topic)
    voice = voice or config.voice_for(script.pillar or topic["pillar"])
    text = " ".join(line.en for line in script.lines)
    audio_path = build_tts(voice, config).synthesize(text, out_dir / f"{uid}-{voice}")
    db.update_media(conn, uid, "voiced", voice=voice, audio_path=str(audio_path))
    return voice, audio_path


def render_topic(conn: sqlite3.Connection, uid: str, image_paths: list[Path], out_dir: Path,
                 config: ChannelConfig, transcribe, render) -> Path:
    topic = db.get_topic(conn, uid)
    if topic is None or not topic["audio_path"]:
        raise PipelineError(f"topic {uid} has no narration yet (run `voice {uid}` first)")
    script = load_script(topic)
    words = transcribe(Path(topic["audio_path"]))
    video_path = render(
        audio_path=Path(topic["audio_path"]),
        image_paths=image_paths,
        out_path=out_dir / f"{uid}-{topic['voice']}.mp4",
        words=words,
        line_word_counts=[len(line.en.split()) for line in script.lines],
        hook_text=script.hook_text,
        channel_name=config.name,
        font_path=PROJECT_ROOT / config.editor.get("font_path", "assets/fonts/Montserrat-ExtraBold.ttf"),
    )
    db.update_media(conn, uid, "rendered", video_path=str(video_path))
    return video_path
