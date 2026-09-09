from __future__ import annotations

from enum import StrEnum


class JobStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConversionStrategy(StrEnum):
    MARKITDOWN = "markitdown"
    TESSERACT_OCR = "tesseract_ocr"

