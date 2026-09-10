from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from localdoc.domain.models import AppSettings, FileLimits
from localdoc.infrastructure.paths import AppPaths


class SettingsService:
    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths

    def load(self) -> AppSettings:
        path = self.paths.settings_file
        if not path.exists():
            return self.default()
        data = json.loads(path.read_text(encoding="utf-8"))
        limits = data.get("file_limits", {})
        return AppSettings(
            output_dir=Path(data.get("output_dir", self.paths.default_output_dir)),
            ocr_enabled=bool(data.get("ocr_enabled", True)),
            ocr_language=str(data.get("ocr_language", "spa+eng")),
            tesseract_path=Path(data["tesseract_path"]) if data.get("tesseract_path") else None,
            theme_mode=str(data.get("theme_mode", "system")),
            file_limits=FileLimits(
                max_files=int(limits.get("max_files", 100)),
                max_file_size_mb=int(limits.get("max_file_size_mb", 100)),
            ),
            conversion_timeout_seconds=int(data.get("conversion_timeout_seconds", 300)),
        )

    def save(self, settings: AppSettings) -> None:
        self.paths.ensure()
        data = asdict(settings)
        data["output_dir"] = str(settings.output_dir)
        data["tesseract_path"] = str(settings.tesseract_path) if settings.tesseract_path else None
        self.paths.settings_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def default(self) -> AppSettings:
        return AppSettings(output_dir=self.paths.default_output_dir)
