from __future__ import annotations

from pathlib import Path

from localdoc.application.conversion_manager import ConversionManager
from localdoc.application.conversion_service import ConversionService
from localdoc.application.history_service import HistoryService
from localdoc.domain.enums import JobStatus
from localdoc.domain.models import AppSettings
from localdoc.infrastructure.database import Database
from localdoc.infrastructure.repositories import JobRepository


class FakeDocumentConverter:
    def convert(self, source_path: Path) -> str:
        return f"# {source_path.name}\n\nok\n"


class FakeOcrEngine:
    def is_available(self) -> bool:
        return True

    def extract_text(self, source_path: Path, language: str) -> str:
        return f"texto {language} {source_path.name}"


def build_manager(tmp_path: Path) -> ConversionManager:
    service = ConversionService(FakeDocumentConverter(), FakeOcrEngine())
    history = HistoryService(JobRepository(Database(tmp_path / "localdoc.db")))
    settings = AppSettings(output_dir=tmp_path / "out")
    return ConversionManager(service, history, settings)


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


def test_manager_continues_after_failed_job(tmp_path: Path) -> None:
    class BrokenConverter:
        def convert(self, source_path: Path) -> str:
            raise RuntimeError("broken")

    service = ConversionService(BrokenConverter(), FakeOcrEngine())
    history = HistoryService(JobRepository(Database(tmp_path / "localdoc.db")))
    manager = ConversionManager(service, history, AppSettings(output_dir=tmp_path / "out"))
    source = tmp_path / "documento.txt"
    source.write_text("hello", encoding="utf-8")

    [job] = manager.add_files([source])
    manager.run_next()

    assert job.status == JobStatus.FAILED
    assert "broken" in job.error
