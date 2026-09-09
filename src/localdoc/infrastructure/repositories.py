from __future__ import annotations

from datetime import datetime
from pathlib import Path

from localdoc.domain.enums import ConversionStrategy, JobStatus
from localdoc.domain.models import ConversionJob
from localdoc.infrastructure.database import Database


class JobRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def upsert(self, job: ConversionJob) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO conversion_jobs (
                    id, source_path, source_name, extension, size_bytes, source_hash,
                    status, strategy, uses_ocr, attempts, output_path, error,
                    created_at, started_at, finished_at, duration_seconds
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    source_hash=excluded.source_hash,
                    status=excluded.status,
                    strategy=excluded.strategy,
                    uses_ocr=excluded.uses_ocr,
                    attempts=excluded.attempts,
                    output_path=excluded.output_path,
                    error=excluded.error,
                    started_at=excluded.started_at,
                    finished_at=excluded.finished_at,
                    duration_seconds=excluded.duration_seconds
                """,
                self._to_row(job),
            )

    def list_recent(self, limit: int = 100) -> list[ConversionJob]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM conversion_jobs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def _to_row(self, job: ConversionJob) -> tuple[object, ...]:
        return (
            job.id,
            str(job.source_path),
            job.name,
            job.extension,
            job.size_bytes,
            job.source_hash,
            job.status.value,
            job.strategy.value,
            int(job.uses_ocr),
            job.attempts,
            str(job.output_path) if job.output_path else None,
            job.error,
            job.created_at.isoformat(timespec="seconds"),
            job.started_at.isoformat(timespec="seconds") if job.started_at else None,
            job.finished_at.isoformat(timespec="seconds") if job.finished_at else None,
            job.duration_seconds,
        )

    def _from_row(self, row: object) -> ConversionJob:
        source_path = Path(row["source_path"])
        job = ConversionJob(source_path=source_path, id=row["id"])
        job.status = JobStatus(row["status"])
        job.source_hash = row["source_hash"] or ""
        job.strategy = ConversionStrategy(row["strategy"])
        job.uses_ocr = bool(row["uses_ocr"])
        job.attempts = int(row["attempts"])
        job.output_path = Path(row["output_path"]) if row["output_path"] else None
        job.error = row["error"] or ""
        job.created_at = datetime.fromisoformat(row["created_at"])
        job.started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
        job.finished_at = (
            datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None
        )
        return job

