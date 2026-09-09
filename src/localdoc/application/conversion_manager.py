from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from localdoc.application.conversion_service import ConversionService
from localdoc.application.history_service import HistoryService
from localdoc.domain.enums import JobStatus
from localdoc.domain.models import AppSettings, ConversionJob, validate_jobs

JobCallback = Callable[[ConversionJob], None]


class ConversionManager:
    def __init__(
        self,
        conversion_service: ConversionService,
        history_service: HistoryService,
        settings: AppSettings,
        on_job_changed: JobCallback | None = None,
    ) -> None:
        self.conversion_service = conversion_service
        self.history_service = history_service
        self.settings = settings
        self.on_job_changed = on_job_changed
        self.jobs: list[ConversionJob] = []

    def add_files(self, paths: list[Path]) -> list[ConversionJob]:
        new_jobs = [ConversionJob(path) for path in paths]
        validate_jobs(self.jobs + new_jobs, self.settings.file_limits)
        self.jobs.extend(new_jobs)
        for job in new_jobs:
            self._notify(job)
        return new_jobs

    def pending(self) -> list[ConversionJob]:
        return [job for job in self.jobs if job.status == JobStatus.QUEUED]

    def run_next(self) -> ConversionJob | None:
        pending = self.pending()
        if not pending:
            return None
        job = pending[0]
        job.mark_processing()
        self._notify(job)
        try:
            output_path = self.conversion_service.convert(
                job,
                self.settings.output_dir,
                self.settings.ocr_language,
            )
            job.mark_completed(output_path)
        except Exception as exc:
            job.mark_failed(str(exc))
        self.history_service.record(job)
        self._notify(job)
        return job

    def retry_failed(self, job_id: str) -> ConversionJob:
        job = self._get_job(job_id)
        job.reset_for_retry()
        self._notify(job)
        return job

    def cancel_pending(self, job_id: str) -> ConversionJob:
        job = self._get_job(job_id)
        if job.status == JobStatus.QUEUED:
            job.mark_cancelled()
            self.history_service.record(job)
            self._notify(job)
        return job

    def _get_job(self, job_id: str) -> ConversionJob:
        for job in self.jobs:
            if job.id == job_id:
                return job
        raise KeyError(job_id)

    def _notify(self, job: ConversionJob) -> None:
        if self.on_job_changed:
            self.on_job_changed(job)

