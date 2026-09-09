from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, TimeoutError
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkerResult:
    output_path: Path | None
    error: str = ""


def run_with_timeout(function, timeout_seconds: int) -> WorkerResult:
    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(function)
        try:
            return future.result(timeout=timeout_seconds)
        except TimeoutError:
            future.cancel()
            return WorkerResult(output_path=None, error="La conversion excedio el tiempo limite.")

