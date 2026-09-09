from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path

from localdoc.application.conversion_service import ConversionService
from localdoc.application.history_service import HistoryService
from localdoc.domain.enums import JobStatus
from localdoc.domain.models import AppSettings, ConversionJob, validate_jobs
from localdoc.workers.conversion_worker import ConversionRunner, ProcessConversionRunner

JobCallback = Callable[[ConversionJob], None]


class ConversionManager:
    def __init__(
        self,
        history_service: HistoryService,
        settings: AppSettings,
        conversion_runner: ConversionRunner | None = None,
        on_job_changed: JobCallback | None = None,
        conversion_service: ConversionService | None = None,
    ) -> None:
        self.history_service = history_service
        self.settings = settings
        self.conversion_runner = conversion_runner or ProcessConversionRunner()
        self.conversion_service = conversion_service
        self.on_job_changed = on_job_changed
        self.jobs: list[ConversionJob] = []
        self._cancel_requested = threading.Event()
        self._worker_thread: threading.Thread | None = None

    def add_files(self, paths: list[Path]) -> list[ConversionJob]:
        new_jobs = [ConversionJob(path) for path in paths]
        validate_jobs(self.jobs + new_jobs, self.settings.file_limits)
        self.jobs.extend(new_jobs)
        for job in new_jobs:
            self._notify(job)
        return new_jobs

    def pending(self) -> list[ConversionJob]:
        return [job for job in self.jobs if job.status == JobStatus.QUEUED]

    def processing(self) -> ConversionJob | None:
        return next((job for job in self.jobs if job.status == JobStatus.PROCESSING), None)

    def run_next(self) -> ConversionJob | None:
        pending = self.pending()
        if not pending:
            return None
        job = pending[0]
        job.mark_processing()
        self._notify(job)
        try:
            result = self.conversion_runner.run(job, self.settings)
            if result.cancelled:
                job.mark_cancelled()
            elif result.output_path:
                job.source_hash = result.source_hash
                job.mark_completed(result.output_path)
            else:
                job.mark_failed(result.error or "No se pudo convertir el documento.")
        except Exception as exc:
            job.mark_failed(str(exc))
        self.history_service.record(job)
        self._notify(job)
        return job

    def run_all(self) -> list[ConversionJob]:
        processed = []
        while self.pending() and not self._cancel_requested.is_set():
            job = self.run_next()
            if job is not None:
                processed.append(job)
        if self._cancel_requested.is_set():
            for job in self.pending():
                job.mark_cancelled()
                self.history_service.record(job)
                self._notify(job)
        self._cancel_requested.clear()
        return processed

    def start(self) -> None:
        if self._worker_thread and self._worker_thread.is_alive():
            return
        self._cancel_requested.clear()
        self._worker_thread = threading.Thread(target=self.run_all, daemon=True)
        self._worker_thread.start()

    def cancel(self) -> None:
        self._cancel_requested.set()
        self.conversion_runner.cancel_active()

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

    def remove_pending(self, job_id: str) -> ConversionJob:
        job = self._get_job(job_id)
        if job.status == JobStatus.QUEUED:
            self.jobs.remove(job)
            self._notify(job)
        return job

    def clear_finished(self) -> None:
        self.jobs = [
            job
            for job in self.jobs
            if job.status not in {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}
        ]

    def _get_job(self, job_id: str) -> ConversionJob:
        for job in self.jobs:
            if job.id == job_id:
                return job
        raise KeyError(job_id)

    def _notify(self, job: ConversionJob) -> None:
        if self.on_job_changed:
            self.on_job_changed(job)
