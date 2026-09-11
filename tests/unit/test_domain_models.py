from __future__ import annotations

from pathlib import Path

import pytest

from localdoc.domain.enums import ConversionStrategy, JobStatus
from localdoc.domain.exceptions import InvalidStateTransitionError, UnsupportedFileError
from localdoc.domain.models import (
    ConversionJob,
    FileLimits,
    safe_filename,
    safe_stem,
    validate_jobs,
)


def test_conversion_job_sets_document_strategy(tmp_path: Path) -> None:
    source = tmp_path / "documento.pdf"
    source.write_text("content", encoding="utf-8")

    job = ConversionJob(source)

    assert job.status == JobStatus.QUEUED
    assert job.strategy == ConversionStrategy.MARKITDOWN
    assert job.uses_ocr is False


def test_conversion_job_sets_ocr_strategy(tmp_path: Path) -> None:
    source = tmp_path / "imagen.png"
    source.write_bytes(b"image")

    job = ConversionJob(source)

    assert job.strategy == ConversionStrategy.TESSERACT_OCR
    assert job.uses_ocr is True


def test_conversion_job_rejects_unsupported_extension(tmp_path: Path) -> None:
    source = tmp_path / "script.exe"
    source.write_bytes(b"nope")

    with pytest.raises(UnsupportedFileError):
        ConversionJob(source)


def test_conversion_job_state_transitions(tmp_path: Path) -> None:
    source = tmp_path / "documento.txt"
    output = tmp_path / "documento.md"
    source.write_text("hello", encoding="utf-8")

    job = ConversionJob(source)
    job.mark_processing()
    job.mark_completed(output)

    assert job.status == JobStatus.COMPLETED
    assert job.output_path == output
    assert job.duration_seconds is not None


def test_completed_job_cannot_be_reprocessed(tmp_path: Path) -> None:
    source = tmp_path / "documento.txt"
    output = tmp_path / "documento.md"
    source.write_text("hello", encoding="utf-8")

    job = ConversionJob(source)
    job.mark_processing()
    job.mark_completed(output)

    with pytest.raises(InvalidStateTransitionError):
        job.mark_processing()


def test_failed_job_can_be_reset_for_retry(tmp_path: Path) -> None:
    source = tmp_path / "documento.txt"
    source.write_text("hello", encoding="utf-8")

    job = ConversionJob(source)
    job.mark_processing()
    job.mark_failed("fallo")
    job.reset_for_retry()

    assert job.status == JobStatus.QUEUED
    assert job.error == ""


def test_validate_jobs_rejects_too_many(tmp_path: Path) -> None:
    files = []
    for index in range(3):
        source = tmp_path / f"{index}.txt"
        source.write_text("x", encoding="utf-8")
        files.append(ConversionJob(source))

    with pytest.raises(Exception, match="Demasiados archivos"):
        validate_jobs(files, FileLimits(max_files=2, max_file_size_mb=1))


def test_safe_filename_normalizes_extension() -> None:
    assert safe_filename("../Mi Archivo!!.PDF") == "Mi_Archivo.pdf"


def test_safe_stem_handles_unicode_and_long_names() -> None:
    long_name = "á" * 8 + "documento-" + ("x" * 300) + ".PDF"

    stem = safe_stem(long_name)

    assert stem.startswith("documento-")
    assert len(stem) <= 120
