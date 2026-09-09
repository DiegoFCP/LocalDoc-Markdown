from __future__ import annotations

from localdoc.domain.models import ConversionJob
from localdoc.infrastructure.repositories import JobRepository


class HistoryService:
    def __init__(self, repository: JobRepository) -> None:
        self.repository = repository

    def record(self, job: ConversionJob) -> None:
        self.repository.upsert(job)

    def recent(self, limit: int = 100) -> list[ConversionJob]:
        return self.repository.list_recent(limit=limit)

