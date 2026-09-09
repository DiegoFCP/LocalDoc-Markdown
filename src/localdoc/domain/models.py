from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from localdoc.domain.enums import ConversionStrategy, JobStatus
from localdoc.domain.exceptions import (
    FileLimitError,
    InvalidStateTransitionError,
    UnsupportedFileError,
)

P0_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".html",
    ".htm",
    ".txt",
    ".csv",
    ".json",
    ".xml",
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
CSV_FORMULA_PREFIXES = ("=", "+", "-", "@")
MAX_SAFE_STEM_LENGTH = 120


@dataclass(frozen=True)
class FileLimits:
    max_files: int = 100
    max_file_size_mb: int = 100

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@dataclass
class ConversionJob:
    source_path: Path
    id: str = field(default_factory=lambda: uuid4().hex)
    status: JobStatus = JobStatus.QUEUED
    output_path: Path | None = None
    source_hash: str = ""
    error: str = ""
    attempts: int = 0
    uses_ocr: bool = False
    strategy: ConversionStrategy = ConversionStrategy.MARKITDOWN
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    finished_at: datetime | None = None

    def __post_init__(self) -> None:
        self.source_path = self.source_path.expanduser().resolve()
        suffix = self.extension
        if suffix not in P0_EXTENSIONS:
            raise UnsupportedFileError(f"Formato no soportado: {suffix or 'sin extension'}")
        self.uses_ocr = suffix in IMAGE_EXTENSIONS
        self.strategy = (
            ConversionStrategy.TESSERACT_OCR if self.uses_ocr else ConversionStrategy.MARKITDOWN
        )

    @property
    def name(self) -> str:
        return self.source_path.name

    @property
    def extension(self) -> str:
        return self.source_path.suffix.lower()

    @property
    def size_bytes(self) -> int:
        return self.source_path.stat().st_size if self.source_path.exists() else 0

    @property
    def duration_seconds(self) -> float | None:
        if not self.started_at or not self.finished_at:
            return None
        return (self.finished_at - self.started_at).total_seconds()

    def compute_hash(self) -> str:
        digest = hashlib.sha256()
        with self.source_path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        self.source_hash = digest.hexdigest().upper()
        return self.source_hash

    def mark_processing(self) -> None:
        self._transition(JobStatus.PROCESSING)
        self.attempts += 1
        self.started_at = datetime.now()
        self.error = ""

    def mark_completed(self, output_path: Path) -> None:
        self.output_path = output_path
        self.finished_at = datetime.now()
        self._transition(JobStatus.COMPLETED)

    def mark_failed(self, error: str) -> None:
        self.error = error
        self.finished_at = datetime.now()
        self._transition(JobStatus.FAILED)

    def mark_cancelled(self) -> None:
        self.finished_at = datetime.now()
        self._transition(JobStatus.CANCELLED)

    def reset_for_retry(self) -> None:
        if self.status != JobStatus.FAILED:
            raise InvalidStateTransitionError("Solo se pueden reintentar trabajos fallidos.")
        self.status = JobStatus.QUEUED
        self.error = ""
        self.started_at = None
        self.finished_at = None

    def _transition(self, new_status: JobStatus) -> None:
        allowed = {
            JobStatus.QUEUED: {JobStatus.PROCESSING, JobStatus.CANCELLED},
            JobStatus.PROCESSING: {
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            },
            JobStatus.FAILED: {JobStatus.QUEUED},
            JobStatus.COMPLETED: set(),
            JobStatus.CANCELLED: set(),
        }
        if new_status not in allowed[self.status]:
            raise InvalidStateTransitionError(f"{self.status} -> {new_status}")
        self.status = new_status


@dataclass(frozen=True)
class AppSettings:
    output_dir: Path
    ocr_enabled: bool = True
    ocr_language: str = "spa+eng"
    tesseract_path: Path | None = None
    file_limits: FileLimits = field(default_factory=FileLimits)
    conversion_timeout_seconds: int = 300


def safe_filename(filename: str) -> str:
    path = Path(filename).name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(path).stem).strip("._")
    suffix = re.sub(r"[^A-Za-z0-9.]+", "", Path(path).suffix)
    return f"{(stem or 'documento')[:MAX_SAFE_STEM_LENGTH]}{suffix.lower()}"


def safe_stem(filename: str) -> str:
    return Path(safe_filename(filename)).stem or "documento"


def csv_safe(value: object) -> str:
    text = "" if value is None else str(value)
    if text.startswith(CSV_FORMULA_PREFIXES):
        return "'" + text
    return text


def validate_jobs(jobs: list[ConversionJob], limits: FileLimits) -> None:
    if len(jobs) > limits.max_files:
        raise FileLimitError(f"Demasiados archivos: {len(jobs)}. Limite: {limits.max_files}.")
    oversized = [job.name for job in jobs if job.size_bytes > limits.max_file_size_bytes]
    if oversized:
        names = ", ".join(oversized[:5])
        raise FileLimitError(f"Archivo(s) sobre {limits.max_file_size_mb} MB: {names}.")
