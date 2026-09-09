from __future__ import annotations

from pathlib import Path

from localdoc.application.settings_service import SettingsService
from localdoc.domain.models import AppSettings, FileLimits
from localdoc.infrastructure.paths import AppPaths


def test_app_paths_create_standard_directories(tmp_path: Path) -> None:
    paths = AppPaths(base_dir=tmp_path / "LocalDoc", default_output_dir=tmp_path / "Markdown")

    paths.ensure()

    assert paths.config_dir.exists()
    assert paths.data_dir.exists()
    assert paths.logs_dir.exists()
    assert paths.cache_dir.exists()
    assert paths.default_output_dir.exists()


def test_settings_round_trip(tmp_path: Path) -> None:
    paths = AppPaths(base_dir=tmp_path / "LocalDoc", default_output_dir=tmp_path / "Markdown")
    service = SettingsService(paths)
    settings = AppSettings(
        output_dir=tmp_path / "outputs",
        ocr_enabled=False,
        ocr_language="eng",
        tesseract_path=tmp_path / "tesseract.exe",
        file_limits=FileLimits(max_files=7, max_file_size_mb=8),
        conversion_timeout_seconds=9,
    )

    service.save(settings)
    loaded = service.load()

    assert loaded.output_dir == settings.output_dir
    assert loaded.ocr_enabled is False
    assert loaded.ocr_language == "eng"
    assert loaded.tesseract_path == settings.tesseract_path
    assert loaded.file_limits.max_files == 7
    assert loaded.file_limits.max_file_size_mb == 8
    assert loaded.conversion_timeout_seconds == 9
