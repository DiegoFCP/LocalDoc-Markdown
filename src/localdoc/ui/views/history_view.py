from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from localdoc.application.history_service import HistoryService
from localdoc.domain.models import ConversionJob
from localdoc.ui.components import EmptyState, SecondaryButton
from localdoc.ui.models.history_table_model import HistoryTableModel
from localdoc.ui.models.queue_table_model import file_type_label
from localdoc.ui.widgets.file_details import FileDetails


class HistoryView(QWidget):
    def __init__(self, history_service: HistoryService, parent=None) -> None:
        super().__init__(parent)
        self.history_service = history_service
        self.all_jobs: list[ConversionJob] = []
        self.filtered_jobs: list[ConversionJob] = []
        self.selected_job_id: str | None = None
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Historial")
        title.setObjectName("HeroTitle")
        title.setStyleSheet("font-size: 22px;")

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar conversiones...")
        self.search.setAccessibleName("Buscar conversiones")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "Completado", "Error", "Cancelado", "En espera"])
        self.status_filter.setAccessibleName("Filtro por estado")
        self.type_filter = QComboBox()
        self.type_filter.addItem("Todos")
        self.type_filter.setAccessibleName("Filtro por tipo")
        self.refresh_button = SecondaryButton("Actualizar", tooltip="Actualizar historial")
        self.search.textChanged.connect(self.apply_filters)
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        self.refresh_button.clicked.connect(self.refresh)
        filters.addWidget(self.search, 1)
        filters.addWidget(self.status_filter)
        filters.addWidget(self.type_filter)
        filters.addWidget(self.refresh_button)

        self.model = HistoryTableModel()
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.clicked.connect(self._select_index)
        self.table.setAccessibleName("Historial de conversiones")

        self.empty = EmptyState("Aun no hay conversiones", "Tus conversiones apareceran aqui.")
        self.details = FileDetails()
        self.open_file_button = SecondaryButton("Abrir Markdown", tooltip="Abrir salida Markdown")
        self.open_folder_button = SecondaryButton(
            "Abrir carpeta",
            tooltip="Abrir carpeta de salida",
        )
        self.open_file_button.clicked.connect(self.open_output_file)
        self.open_folder_button.clicked.connect(self.open_output_folder)

        detail_actions = QHBoxLayout()
        detail_actions.addWidget(self.open_file_button)
        detail_actions.addWidget(self.open_folder_button)
        detail_actions.addStretch(1)

        layout.addWidget(title)
        layout.addLayout(filters)
        layout.addWidget(self.empty)
        layout.addWidget(self.table, 1)
        layout.addLayout(detail_actions)
        layout.addWidget(self.details)

    def refresh(self) -> None:
        self.all_jobs = self.history_service.recent()
        types = sorted({file_type_label(job) for job in self.all_jobs})
        current_type = self.type_filter.currentText()
        self.type_filter.blockSignals(True)
        self.type_filter.clear()
        self.type_filter.addItem("Todos")
        self.type_filter.addItems(types)
        if current_type in {"Todos", *types}:
            self.type_filter.setCurrentText(current_type)
        self.type_filter.blockSignals(False)
        self.apply_filters()

    def apply_filters(self) -> None:
        query = self.search.text().strip().lower()
        status = self.status_filter.currentText()
        file_type = self.type_filter.currentText()
        self.filtered_jobs = []
        for job in self.all_jobs:
            if query and query not in job.name.lower():
                continue
            if status != "Todos" and status != self._status_text(job):
                continue
            if file_type != "Todos" and file_type != file_type_label(job):
                continue
            self.filtered_jobs.append(job)
        self.model.set_jobs(self.filtered_jobs)
        self.table.setVisible(bool(self.filtered_jobs))
        self.empty.setVisible(not self.filtered_jobs)
        self._refresh_actions()

    def selected_job(self) -> ConversionJob | None:
        if not self.selected_job_id:
            return None
        return next((job for job in self.filtered_jobs if job.id == self.selected_job_id), None)

    def open_output_file(self) -> None:
        job = self.selected_job()
        if job and job.output_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(job.output_path)))

    def open_output_folder(self) -> None:
        job = self.selected_job()
        if job and job.output_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(job.output_path.parent)))

    def _select_index(self, index) -> None:
        self.selected_job_id = index.data(Qt.ItemDataRole.UserRole)
        self.details.set_job(self.selected_job())
        self._refresh_actions()

    def _refresh_actions(self) -> None:
        has_output = bool(self.selected_job() and self.selected_job().output_path)
        self.open_file_button.setEnabled(has_output)
        self.open_folder_button.setEnabled(has_output)
        if not self.selected_job():
            self.details.set_job(None)

    def _status_text(self, job: ConversionJob) -> str:
        return {
            "completed": "Completado",
            "failed": "Error",
            "cancelled": "Cancelado",
            "queued": "En espera",
            "processing": "Procesando",
        }.get(job.status.value, job.status.value)
