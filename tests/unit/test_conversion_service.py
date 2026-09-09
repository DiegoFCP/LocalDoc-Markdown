from __future__ import annotations

from pathlib import Path

import pytest

from localdoc.application.conversion_service import ConversionService
from localdoc.domain.enums import ConversionStrategy
from localdoc.domain.exceptions import OcrUnavailableError
from localdoc.domain.models import ConversionJob


class FakeDocumentConverter:
    def convert(self, source_path: Path) -> str:
        return f"# {source_path.name}\n\nok\n"


class FakeOcrEngine:
    def __init__(self, available: bool = True) -> None:
        self.available = available

    def is_available(self) -> bool:
        return self.available

    def extract_text(self, source_path: Path, language: str) -> str:
        return f"texto {language} {source_path.name}"


def test_conversion_service_writes_markdown_output(tmp_path: Path) -> None:
    source = tmp_path / "documento.txt"
    source.write_text("hello", encoding="utf-8")
    job = ConversionJob(source)
    service = ConversionService(FakeDocumentConverter(), FakeOcrEngine())

    output_path = service.convert(job, tmp_path / "out", "spa+eng")

    assert output_path.name == "documento.md"
    assert output_path.read_text(encoding="utf-8").startswith("# documento.txt")
    assert job.source_hash


def test_conversion_service_uses_ocr_for_images(tmp_path: Path) -> None:
    source = tmp_path / "imagen.png"
    source.write_bytes(b"fake image bytes")
    job = ConversionJob(source)
    service = ConversionService(FakeDocumentConverter(), FakeOcrEngine())

    output_path = service.convert(job, tmp_path / "out", "spa+eng")

    assert job.strategy == ConversionStrategy.TESSERACT_OCR
    assert "texto spa+eng imagen.png" in output_path.read_text(encoding="utf-8")


def test_conversion_service_reports_missing_ocr(tmp_path: Path) -> None:
    source = tmp_path / "imagen.png"
    source.write_bytes(b"fake image bytes")
    job = ConversionJob(source)
    service = ConversionService(FakeDocumentConverter(), FakeOcrEngine(available=False))

    with pytest.raises(OcrUnavailableError):
        service.convert(job, tmp_path / "out", "spa+eng")
