from __future__ import annotations

import multiprocessing

from localdoc.infrastructure.logging_config import configure_logging


def main() -> int:
    multiprocessing.freeze_support()
    configure_logging()
    return 0

