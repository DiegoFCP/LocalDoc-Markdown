from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from localdoc.infrastructure.paths import AppPaths, get_default_paths


def configure_logging(paths: AppPaths | None = None) -> None:
    active_paths = paths or get_default_paths()
    active_paths.ensure()
    handler = RotatingFileHandler(
        active_paths.log_file,
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[handler],
    )

