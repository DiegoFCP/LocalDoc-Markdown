from __future__ import annotations

import threading
from pathlib import Path

from localdoc.application.conversion_manager import ConversionManager
from localdoc.application.history_service import HistoryService
from localdoc.domain.enums import JobStatus
from localdoc.domain.models import AppSettings, ConversionJob
from localdoc.infrastructure.database import Database
from localdoc.infrastructure.repositories import JobRepository
from localdoc.workers.conversion_worker import ConversionResult


class FakeRunner:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.cancelled = False

    def run(self, job: ConversionJob, settings: AppSettings) -> ConversionResult:
        if self.fail:
            return ConversionResult(output_path=None, error="broken")
        job.compute_hash()
        output_path = settings.output_dir / f"{job.source_path.stem}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"# {job.name}\n\nok\n", encoding="utf-8")
        return ConversionResult(output_path=output_path, source_hash=job.source_hash)

    def cancel_active(self) -> None:
        self.cancelled = True


class BlockingRunner:
    def __init__(self) -> None:
        self.cancelled = threading.Event()

    def run(self, job: ConversionJob, settings: AppSettings) -> ConversionResult:
        self.cancelled.wait(timeout=5)
        return ConversionResult(output_path=None, cancelled=True)

    def cancel_active(self) -> None:
        self.cancelled.set()


def build_manager(tmp_path: Path, runner: FakeRunner | None = None) -> ConversionManager:
    history = HistoryService(JobRepository(Database(tmp_path / "localdoc.db")))
    settings = AppSettings(output_dir=tmp_path / "out")
    return ConversionManager(history, settings, conversion_runner=runner or FakeRunner())


def test_manager_adds_and_runs_document_job(tmp_path: Path) -> None:
    source = tmp_path / "documento.txt"
    source.write_text("hello", encoding="utf-8")
    manager = build_manager(tmp_path)

    [job] = manager.add_files([source])
    processed = manager.run_next()

    assert processed is job
    assert job.status == JobStatus.COMPLETED
    assert job.output_path is not None
    assert job.output_path.read_text(encoding="utf-8").startswith("# documento.txt")


def test_manager_deduplicates_files_inside_same_batch(tmp_path: Path) -> None:
    source = tmp_path / "documento.txt"
    source.write_text("hello", encoding="utf-8")
    manager = build_manager(tmp_path)

    jobs = manager.add_files([source, source])

    assert len(jobs) == 1
    assert len(manager.jobs) == 1


def test_manager_marks_deleted_source_as_failed(tmp_path: Path) -> None:
    source = tmp_path / "documento.txt"
    source.write_text("hello", encoding="utf-8")
    manager = build_manager(tmp_path)
    [job] = manager.add_files([source])
    source.unlink()

    manager.run_next()

    assert job.status == JobStatus.FAILED
    assert job.error


def test_manager_accepts_queue_at_file_limit(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)
    files = []
    for index in range(manager.settings.file_limits.max_files):
        source = tmp_path / f"{index}.txt"
        source.write_text("x", encoding="utf-8")
        files.append(source)

    jobs = manager.add_files(files)

    assert len(jobs) == manager.settings.file_limits.max_files


def test_manager_continues_after_failed_job(tmp_path: Path) -> None:
    manager = build_manager(tmp_path, FakeRunner(fail=True))
    source = tmp_path / "documento.txt"
    source.write_text("hello", encoding="utf-8")

    [job] = manager.add_files([source])
    manager.run_next()

    assert job.status == JobStatus.FAILED
    assert "broken" in job.error


def test_manager_run_all_processes_each_pending_job(tmp_path: Path) -> None:
    first = tmp_path / "a.txt"
    second = tmp_path / "b.txt"
    first.write_text("a", encoding="utf-8")
    second.write_text("b", encoding="utf-8")
    manager = build_manager(tmp_path)

    manager.add_files([first, second])
    processed = manager.run_all()

    assert len(processed) == 2
    assert {job.status for job in processed} == {JobStatus.COMPLETED}


def test_manager_can_cancel_pending_job(tmp_path: Path) -> None:
    source = tmp_path / "documento.txt"
    source.write_text("hello", encoding="utf-8")
    manager = build_manager(tmp_path)

    [job] = manager.add_files([source])
    manager.cancel_pending(job.id)

    assert job.status == JobStatus.CANCELLED


def test_manager_cancel_requests_runner_shutdown(tmp_path: Path) -> None:
    runner = FakeRunner()
    manager = build_manager(tmp_path, runner)

    manager.cancel()

    assert runner.cancelled is True


def test_manager_marks_active_job_cancelled(tmp_path: Path) -> None:
    source = tmp_path / "documento.txt"
    source.write_text("hello", encoding="utf-8")
    runner = BlockingRunner()
    manager = build_manager(tmp_path, runner)
    [job] = manager.add_files([source])

    thread = threading.Thread(target=manager.run_next)
    thread.start()
    manager.cancel()
    thread.join(timeout=2)

    assert job.status == JobStatus.CANCELLED
