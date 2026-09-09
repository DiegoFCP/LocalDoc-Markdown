from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    base_dir: Path
    default_output_dir: Path

    @property
    def config_dir(self) -> Path:
        return self.base_dir / "config"

    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"

    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"

    @property
    def cache_dir(self) -> Path:
        return self.base_dir / "cache"

    @property
    def settings_file(self) -> Path:
        return self.config_dir / "settings.json"

    @property
    def database_file(self) -> Path:
        return self.data_dir / "localdoc.db"

    @property
    def log_file(self) -> Path:
        return self.logs_dir / "localdoc.log"

    def ensure(self) -> None:
        for path in (self.config_dir, self.data_dir, self.logs_dir, self.cache_dir):
            path.mkdir(parents=True, exist_ok=True)
        self.default_output_dir.mkdir(parents=True, exist_ok=True)


def get_default_paths() -> AppPaths:
    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    user_profile = Path(os.environ.get("USERPROFILE", Path.home()))
    return AppPaths(
        base_dir=local_app_data / "LocalDoc",
        default_output_dir=user_profile / "Documents" / "LocalDoc" / "Markdown",
    )

