"""Glue between collectors, scoring, sensitivity rules, the DB and the script writer."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from korea_decoded import db, scoring, sensitivity
from korea_decoded.config import ChannelConfig
from korea_decoded.models import RawTopic
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
