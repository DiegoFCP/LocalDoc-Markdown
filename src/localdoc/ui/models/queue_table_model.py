from __future__ import annotations

from localdoc.domain.enums import JobStatus
from localdoc.domain.models import ConversionJob

STATUS_LABELS = {
    JobStatus.QUEUED: "En espera",
    JobStatus.PROCESSING: "Procesando",
    JobStatus.COMPLETED: "Completado",
    JobStatus.FAILED: "Error",
    JobStatus.CANCELLED: "Cancelado",
}


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / 1024 / 1024:.1f} MB"


def job_row(job: ConversionJob) -> list[str]:
    return [
        job.extension.lstrip(".").upper() or "FILE",
        job.name,
        format_size(job.size_bytes),
        STATUS_LABELS[job.status],
    ]

