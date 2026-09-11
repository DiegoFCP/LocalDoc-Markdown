from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor, QFont

from localdoc.domain.enums import JobStatus
from localdoc.domain.models import ConversionJob
from localdoc.ui.icons import file_type_icon, status_icon

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
        file_label(job),
        format_size(job.size_bytes),
        STATUS_LABELS[job.status],
        "",
    ]


def file_type_label(job: ConversionJob) -> str:
    extension = job.extension.lstrip(".").upper()
    if job.uses_ocr:
        return "IMG"
    return extension or "FILE"


def file_label(job: ConversionJob) -> str:
    return f"[{file_type_label(job)}] {job.name}"


class QueueTableModel(QAbstractTableModel):
    headers = ["Archivo", "Tamano", "Estado", ""]

    def __init__(self, jobs: list[ConversionJob] | None = None) -> None:
        super().__init__()
        self.jobs = jobs or []

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        parent = parent or QModelIndex()
        return 0 if parent.isValid() else len(self.jobs)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        parent = parent or QModelIndex()
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        job = self.jobs[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return job_row(job)[index.column()]
        if role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 0:
                return file_type_icon(file_type_label(job))
            if index.column() == 2:
                return status_icon(job.status.value)
        if role == Qt.ItemDataRole.ForegroundRole and index.column() == 2:
            return QColor(
                {
                    JobStatus.QUEUED: "#7D879D",
                    JobStatus.PROCESSING: "#286BF4",
                    JobStatus.COMPLETED: "#1FA46F",
                    JobStatus.FAILED: "#D94D4D",
                    JobStatus.CANCELLED: "#7D879D",
                }[job.status]
            )
        if role == Qt.ItemDataRole.FontRole and index.column() in {0, 2}:
            font = QFont()
            font.setWeight(QFont.Weight.DemiBold)
            return font
        if role == Qt.ItemDataRole.UserRole:
            return job.id
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return None
        return self.headers[section]

    def set_jobs(self, jobs: list[ConversionJob]) -> None:
        self.beginResetModel()
        self.jobs = jobs
        self.endResetModel()
