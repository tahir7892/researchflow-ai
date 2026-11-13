"""SQLite audit trail. API keys are NEVER stored here."""
from __future__ import annotations
import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent.parent / ".data" / "researchflow.sqlite"


def initialize(path: Path = DB_PATH):
    path.parent.mkdir(exist_ok=True, parents=True)
    with sqlite3.connect(str(path)) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS approvals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            topic TEXT NOT NULL,
            mode TEXT NOT NULL,
            source_count INTEGER NOT NULL,
            reviewed_edit INTEGER NOT NULL,
            approved_markdown TEXT NOT NULL,
            source_status TEXT NOT NULL)""")


def save_approval(result: dict, edited_markdown: str, path: Path = DB_PATH) -> int:
    initialize(path)
    with sqlite3.connect(str(path)) as db:
        cursor = db.execute("""INSERT INTO approvals
            (created_at, topic, mode, source_count, reviewed_edit, approved_markdown, source_status)
            VALUES(?,?,?,?,?,?,?)""",
            (datetime.now(timezone.utc).isoformat(), result["topic"], result["mode"],
             len(result["papers"]), int(edited_markdown != result["markdown"]),
             edited_markdown, json.dumps(result["source_status"])))
        return int(cursor.lastrowid)


def recent_approvals(path: Path = DB_PATH) -> list[dict]:
    initialize(path)
    with sqlite3.connect(str(path)) as db:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute("""SELECT id, created_at, topic, mode, source_count, reviewed_edit
                                                FROM approvals ORDER BY id DESC LIMIT 20""").fetchall()]
