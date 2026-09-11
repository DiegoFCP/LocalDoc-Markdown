from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from localdoc.domain.models import ConversionJob
from localdoc.ui.models.queue_table_model import STATUS_LABELS, file_type_label, format_size


class HistoryTableModel(QAbstractTableModel):
    headers = ["Archivo", "Tipo", "Estado", "Fecha", "Tamaño"]

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
        values = [
            job.name,
            file_type_label(job),
            STATUS_LABELS[job.status],
            job.created_at.strftime("%Y-%m-%d %H:%M"),
            format_size(job.size_bytes),
        ]
        if role == Qt.ItemDataRole.DisplayRole:
            return values[index.column()]
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
