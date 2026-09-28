"""SQLite store for topics and their progress through the pipeline.

Topic status flow:
    new ──────────────┐
                      ├──> scripted
    review ─> approved┘
          └─> rejected
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS topics (
    uid TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    engagement INTEGER NOT NULL DEFAULT 0,
    published_at TEXT NOT NULL DEFAULT '',
    pillar TEXT,
    score REAL NOT NULL DEFAULT 0,
    sensitivity TEXT NOT NULL,
    sensitivity_reason TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    script_path TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

STATUSES = ("new", "review", "approved", "rejected", "scripted")


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


def insert_topic(conn: sqlite3.Connection, **fields) -> bool:
    """Insert a topic; returns False if it was already collected."""
    cols = ", ".join(fields)
    marks = ", ".join("?" for _ in fields)
    cur = conn.execute(
        f"INSERT OR IGNORE INTO topics ({cols}) VALUES ({marks})", tuple(fields.values())
    )
    conn.commit()
    return cur.rowcount == 1


def list_topics(conn: sqlite3.Connection, status: str | None = None, limit: int = 50):
    if status:
        return conn.execute(
            "SELECT * FROM topics WHERE status = ? ORDER BY score DESC LIMIT ?", (status, limit)
        ).fetchall()
    return conn.execute("SELECT * FROM topics ORDER BY score DESC LIMIT ?", (limit,)).fetchall()


def ready_for_script(conn: sqlite3.Connection, limit: int):
    return conn.execute(
        "SELECT * FROM topics WHERE status IN ('new', 'approved') ORDER BY score DESC LIMIT ?",
        (limit,),
    ).fetchall()


def set_status(conn: sqlite3.Connection, uid: str, status: str, script_path: str | None = None) -> bool:
    if status not in STATUSES:
        raise ValueError(f"unknown status: {status}")
    cur = conn.execute(
        "UPDATE topics SET status = ?, script_path = COALESCE(?, script_path) WHERE uid = ?",
        (status, script_path, uid),
    )
    conn.commit()
    return cur.rowcount == 1
