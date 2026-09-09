from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import get_context
from multiprocessing.context import SpawnProcess
from multiprocessing.queues import Queue
from pathlib import Path
from queue import Empty
from threading import Lock
from typing import Protocol

from localdoc.domain.enums import ConversionStrategy
from localdoc.domain.models import AppSettings, ConversionJob, safe_stem
from localdoc.infrastructure.filesystem import resolve_available_output_path
from localdoc.infrastructure.markitdown_adapter import MarkItDownAdapter
from localdoc.infrastructure.tesseract_adapter import TesseractAdapter


@dataclass(frozen=True)
class ConversionRequest:
    source_path: Path
    output_dir: Path
    strategy: ConversionStrategy
    ocr_language: str
    tesseract_path: Path | None


@dataclass(frozen=True)
class ConversionResult:
    output_path: Path | None
    source_hash: str = ""
    error: str = ""
    timed_out: bool = False
    cancelled: bool = False


class ConversionRunner(Protocol):
    def run(self, job: ConversionJob, settings: AppSettings) -> ConversionResult: ...
    def cancel_active(self) -> None: ...


def _convert_request(request: ConversionRequest, result_queue: Queue) -> None:
    try:
        job = ConversionJob(request.source_path)
        source_hash = job.compute_hash()
        output_path = resolve_available_output_path(
            request.output_dir,
            safe_stem(request.source_path.name),
            ".md",
        )
        if request.strategy == ConversionStrategy.TESSERACT_OCR:
            ocr_engine = TesseractAdapter(request.tesseract_path)
            text = ocr_engine.extract_text(request.source_path, request.ocr_language).strip()
            markdown = (
                f"# {request.source_path.name}\n\n"
                f"{text or '_OCR no encontro texto legible._'}\n"
            )
        else:
            markdown = MarkItDownAdapter().convert(request.source_path)

        request.output_dir.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        result_queue.put(ConversionResult(output_path=output_path, source_hash=source_hash))
    except Exception as exc:
        result_queue.put(ConversionResult(output_path=None, error=str(exc)))


class ProcessConversionRunner:
    def __init__(self) -> None:
        self._process: SpawnProcess | None = None
        self._lock = Lock()
        self._cancel_requested = False

    def run(self, job: ConversionJob, settings: AppSettings) -> ConversionResult:
        context = get_context("spawn")
        result_queue = context.Queue()
        self._cancel_requested = False
        request = ConversionRequest(
            source_path=job.source_path,
            output_dir=settings.output_dir,
            strategy=job.strategy,
            ocr_language=settings.ocr_language,
            tesseract_path=settings.tesseract_path,
        )
        process = context.Process(target=_convert_request, args=(request, result_queue))
        with self._lock:
            self._process = process
        process.start()
        process.join(settings.conversion_timeout_seconds)

        if self._cancel_requested:
            if process.is_alive():
                process.terminate()
                process.join(5)
            with self._lock:
                self._process = None
            return ConversionResult(output_path=None, cancelled=True)

        if process.is_alive():
            process.terminate()
            process.join(5)
            with self._lock:
                self._process = None
            return ConversionResult(
                output_path=None,
                error="La conversion excedio el tiempo limite.",
                timed_out=True,
            )

        with self._lock:
            self._process = None
        try:
            return result_queue.get_nowait()
        except Empty:
            return ConversionResult(
                output_path=None,
                error="La conversion termino sin entregar resultado.",
            )

    def cancel_active(self) -> None:
        self._cancel_requested = True
        with self._lock:
            process = self._process
        if process is not None and process.is_alive():
            process.terminate()
            process.join(5)


class ServiceConversionRunner:
    def __init__(self, service) -> None:
        self.service = service

    def run(self, job: ConversionJob, settings: AppSettings) -> ConversionResult:
        try:
            output_path = self.service.convert(job, settings.output_dir, settings.ocr_language)
            return ConversionResult(output_path=output_path, source_hash=job.source_hash)
        except Exception as exc:
            return ConversionResult(output_path=None, error=str(exc))

    def cancel_active(self) -> None:
        return None
