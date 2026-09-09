from __future__ import annotations

from pathlib import Path

from localdoc.application.conversion_manager import ConversionManager
from localdoc.application.history_service import HistoryService
from localdoc.application.settings_service import SettingsService
from localdoc.domain.models import AppSettings, ConversionJob
from localdoc.infrastructure.database import Database
from localdoc.infrastructure.paths import AppPaths
from localdoc.infrastructure.repositories import JobRepository
from localdoc.infrastructure.tesseract_adapter import TesseractAdapter
from localdoc.ui.main_window import MainWindow
from localdoc.workers.conversion_worker import ConversionResult


class FakeRunner:
    def run(self, job: ConversionJob, settings: AppSettings) -> ConversionResult:
        job.compute_hash()
        output_path = settings.output_dir / f"{job.source_path.stem}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"# {job.name}\n\ncontenido", encoding="utf-8")
        return ConversionResult(output_path=output_path, source_hash=job.source_hash)

    def cancel_active(self) -> None:
        return None


def build_window(tmp_path: Path, qtbot) -> MainWindow:
    paths = AppPaths(base_dir=tmp_path / "LocalDoc", default_output_dir=tmp_path / "Markdown")
    paths.ensure()
    settings_service = SettingsService(paths)
    settings = AppSettings(output_dir=paths.default_output_dir)
    history = HistoryService(JobRepository(Database(paths.database_file)))
    manager = ConversionManager(history, settings, conversion_runner=FakeRunner())
    window = MainWindow(manager, settings_service, TesseractAdapter(tmp_path / "missing.exe"))
    qtbot.addWidget(window)
    return window


def test_main_window_initializes(tmp_path: Path, qtbot) -> None:
    window = build_window(tmp_path, qtbot)

    assert window.windowTitle() == "LocalDoc"
    assert window.table.rowCount() == 0
    assert "OCR no disponible" in window.ocr_status.text()


def test_main_window_adds_file_to_queue(tmp_path: Path, qtbot) -> None:
    window = build_window(tmp_path, qtbot)
    source = tmp_path / "nota.txt"
    source.write_text("hola", encoding="utf-8")

    window._add_paths([source])

    assert window.table.rowCount() == 1
    assert window.manager.jobs[0].name == "nota.txt"


def test_main_window_runs_conversion_and_shows_preview(tmp_path: Path, qtbot) -> None:
    window = build_window(tmp_path, qtbot)
    source = tmp_path / "nota.txt"
    source.write_text("hola", encoding="utf-8")
    window._add_paths([source])

    window.manager.run_next()
    window._refresh_detail(window.manager.jobs[0])

    assert "# nota.txt" in window.preview.toPlainText()
