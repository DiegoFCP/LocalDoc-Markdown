from __future__ import annotations

from pathlib import Path

from localdoc.domain.enums import JobStatus
from localdoc.domain.models import ConversionJob
from localdoc.infrastructure.database import Database
from localdoc.infrastructure.repositories import JobRepository


def test_job_repository_persists_completed_job(tmp_path: Path) -> None:
    source = tmp_path / "documento.txt"
    output = tmp_path / "documento.md"
    source.write_text("hello", encoding="utf-8")

    job = ConversionJob(source)
    job.compute_hash()
    job.mark_processing()
    job.mark_completed(output)

    repository = JobRepository(Database(tmp_path / "localdoc.db"))
    repository.upsert(job)
    rows = repository.list_recent()

    assert len(rows) == 1
    assert rows[0].id == job.id
    assert rows[0].status == JobStatus.COMPLETED
    assert rows[0].output_path == output
    assert rows[0].source_hash == job.source_hash
