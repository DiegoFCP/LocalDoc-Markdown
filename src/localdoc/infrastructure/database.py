from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversion_jobs (
    id TEXT PRIMARY KEY,
    source_path TEXT NOT NULL,
    source_name TEXT NOT NULL,
    extension TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    source_hash TEXT,
    status TEXT NOT NULL,
    strategy TEXT NOT NULL,
    uses_ocr INTEGER NOT NULL,
    attempts INTEGER NOT NULL,
    output_path TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    duration_seconds REAL
);

CREATE INDEX IF NOT EXISTS idx_conversion_jobs_created_at
ON conversion_jobs(created_at DESC);
"""


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.executescript(SCHEMA)
        return connection

