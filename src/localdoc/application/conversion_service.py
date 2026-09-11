from __future__ import annotations

from pathlib import Path
from typing import Protocol

from localdoc.domain.enums import ConversionStrategy
from localdoc.domain.exceptions import ConversionFailedError, OcrUnavailableError
from localdoc.domain.models import ConversionJob, safe_stem
from localdoc.infrastructure.filesystem import resolve_available_output_path


class DocumentConverter(Protocol):
    def convert(self, source_path: Path) -> str: ...


class OcrEngine(Protocol):
    def is_available(self) -> bool: ...
    def extract_text(self, source_path: Path, language: str) -> str: ...


class ConversionService:
    def __init__(self, document_converter: DocumentConverter, ocr_engine: OcrEngine) -> None:
        self.document_converter = document_converter
        self.ocr_engine = ocr_engine

    def convert(self, job: ConversionJob, output_dir: Path, ocr_language: str) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        job.compute_hash()
        output_path = resolve_available_output_path(output_dir, safe_stem(job.name), ".md")
        try:
            if job.strategy == ConversionStrategy.TESSERACT_OCR:
                if not self.ocr_engine.is_available():
                    raise OcrUnavailableError("No se encontro Tesseract OCR.")
                text = self.ocr_engine.extract_text(job.source_path, ocr_language).strip()
                markdown = f"# {job.name}\n\n{text or '_OCR no encontro texto legible._'}\n"
            else:
                markdown = self.document_converter.convert(job.source_path)
        except OcrUnavailableError:
            raise
        except Exception as exc:
            raise ConversionFailedError(str(exc)) from exc

        output_path.write_text(markdown, encoding="utf-8")
        return output_path

