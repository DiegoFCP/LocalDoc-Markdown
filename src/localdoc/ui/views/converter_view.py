from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QSplitter,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from localdoc.application.conversion_manager import ConversionManager
from localdoc.domain.enums import JobStatus
from localdoc.domain.exceptions import LocalDocError
from localdoc.domain.models import P0_EXTENSIONS, ConversionJob
from localdoc.ui.components import (
    IconButton,
    InlineNotification,
    PrimaryButton,
    SecondaryButton,
    StatusBanner,
)
from localdoc.ui.models.queue_table_model import (
    STATUS_LABELS,
    QueueTableModel,
    file_type_label,
    format_size,
)
from localdoc.ui.widgets.drop_zone import DropZone
from localdoc.ui.widgets.file_details import FileDetails
from localdoc.ui.widgets.markdown_preview import MarkdownPreview


class ConverterView(QWidget):
    browse_requested = Signal()
    status_changed = Signal(str)

    def __init__(self, manager: ConversionManager, parent=None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.selected_job_id: str | None = None
        self._build_ui()
        self.refresh_queue()
        self.refresh_detail(None)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter()
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_detail_panel())
        splitter.setSizes([760, 420])
        layout.addWidget(splitter, 1)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 16, 24)
        layout.setSpacing(14)

        eyebrow = QLabel("CONVIERTE · LEE · EDITA · AVANZA")
        eyebrow.setObjectName("Muted")
        title = QLabel("Tu documento, listo para trabajar")
        title.setObjectName("HeroTitle")
        title.setWordWrap(True)

        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self.add_paths)
        self.drop_zone.browse_requested.connect(self.browse_requested.emit)

        privacy = QLabel("Procesamiento 100% local. Tus archivos permanecen en tu equipo.")
        privacy.setObjectName("Muted")

        header_row = QHBoxLayout()
        self.queue_title = QLabel("Archivos en cola (0)")
        self.queue_title.setObjectName("CardTitle")
        self.queue_menu_button = IconButton(
            "...",
            tooltip="Mas acciones de cola",
            accessible_name="Mas acciones de cola",
        )
        self.queue_menu_button.clicked.connect(self._open_queue_menu)
        header_row.addWidget(self.queue_title)
        header_row.addStretch(1)
        header_row.addWidget(self.queue_menu_button)

        self.queue_model = QueueTableModel(self.manager.jobs)
        self.table = QTableView()
        self.table.setModel(self.queue_model)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setMinimumSectionSize(80)
        self.table.setColumnWidth(0, 380)
        self.table.setColumnWidth(1, 110)
        self.table.setColumnWidth(2, 140)
        self.table.clicked.connect(self._select_index)
        self.table.setAccessibleName("Cola de archivos")

        actions = QHBoxLayout()
        self.convert_button = PrimaryButton(
            "Convertir",
            tooltip="Convertir archivos pendientes",
        )
        self.cancel_button = SecondaryButton(
            "Cancelar",
            tooltip="Solicitar cancelacion de la conversion activa",
        )
        self.convert_button.clicked.connect(self.start_conversion)
        self.cancel_button.clicked.connect(self.cancel_conversion)
        actions.addStretch(1)
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.convert_button)

        self.notification = InlineNotification()
        self.empty_queue = QLabel(
            "Todavia no hay documentos. Arrastra archivos arriba para comenzar."
        )
        self.empty_queue.setObjectName("Muted")
        self.empty_queue.setWordWrap(True)

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(self.drop_zone)
        layout.addWidget(privacy)
        layout.addWidget(self.notification)
        layout.addLayout(header_row)
        layout.addWidget(self.empty_queue)
        layout.addWidget(self.table, 1)
        layout.addLayout(actions)
        return panel

    def _build_detail_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("SurfacePanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Archivo seleccionado")
        title.setObjectName("CardTitle")
        self.detail_name = QLabel("Sin seleccion")
        self.detail_name.setObjectName("HeroTitle")
        self.detail_name.setStyleSheet("font-size: 18px;")
        self.detail_name.setWordWrap(True)
        self.detail_meta = QLabel("Selecciona un archivo para ver el detalle.")
        self.detail_meta.setObjectName("Muted")
        self.detail_meta.setWordWrap(True)

        self.status_banner = StatusBanner()

        self.copy_button = SecondaryButton(
            "Copiar",
            tooltip="Copiar la vista Markdown al portapapeles",
        )
        self.open_file_button = SecondaryButton(
            "Abrir",
            tooltip="Abrir el archivo Markdown generado",
        )
        self.open_folder_button = SecondaryButton(
            "Abrir carpeta",
            tooltip="Abrir la carpeta de salida",
        )
        self.more_button = IconButton("...", tooltip="Mas acciones", accessible_name="Mas acciones")
        self.copy_button.clicked.connect(self.copy_markdown)
        self.open_file_button.clicked.connect(self.open_output_file)
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.more_button.clicked.connect(self._open_selected_menu)

        action_grid = QGridLayout()
        action_grid.addWidget(self.copy_button, 0, 0)
        action_grid.addWidget(self.open_file_button, 0, 1)
        action_grid.addWidget(self.more_button, 0, 2)
        action_grid.addWidget(self.open_folder_button, 1, 0, 1, 3)

        self.preview = MarkdownPreview()
        self.details = FileDetails()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.preview, "Vista previa")
        self.tabs.addTab(self.details, "Detalles")

        layout.addWidget(title)
        layout.addWidget(self.detail_name)
        layout.addWidget(self.detail_meta)
        layout.addWidget(self.status_banner)
        layout.addLayout(action_grid)
        layout.addWidget(self.tabs, 1)
        return panel

    def add_paths(self, paths: list[Path]) -> None:
        files = self.collect_files(paths)
        rejected = len(paths) - len(files)
        if not files:
            self.notify("No se encontraron archivos compatibles.")
            return
        try:
            added = self.manager.add_files(files)
        except LocalDocError as exc:
            self.notify(exc.user_message)
            return
        except Exception:
            self.notify("No se pudieron agregar los archivos.")
            return
        message = f"{len(added)} archivo(s) agregado(s)."
        if rejected > 0:
            message += f" {rejected} no compatible(s)."
        self.notify(message)
        self.refresh_queue()

    def collect_files(self, paths: list[Path]) -> list[Path]:
        files: list[Path] = []
        for path in paths:
            if path.is_dir():
                files.extend(
                    candidate
                    for candidate in path.rglob("*")
                    if candidate.is_file() and candidate.suffix.lower() in P0_EXTENSIONS
                )
            elif path.is_file() and path.suffix.lower() in P0_EXTENSIONS:
                files.append(path)
        return files

    def start_conversion(self) -> None:
        if not self.manager.pending():
            self.notify("No hay archivos pendientes.")
            return
        self.notify("Convirtiendo documentos...", timeout_ms=0)
        self.manager.start()
        self.refresh_running_state()

    def cancel_conversion(self) -> None:
        self.manager.cancel()
        self.notify("Cancelacion solicitada.")

    def retry_selected(self) -> None:
        job = self.selected_job()
        if job is None or job.status != JobStatus.FAILED:
            self.notify("Selecciona un archivo con error para reintentar.")
            return
        self.manager.retry_failed(job.id)
        self.refresh_queue()

    def clear_finished(self) -> None:
        self.manager.clear_finished()
        self.selected_job_id = None
        self.refresh_queue()
        self.refresh_detail(None)

    def refresh_job(self, job: ConversionJob) -> None:
        self.selected_job_id = self.selected_job_id or job.id
        self.refresh_queue()
        self.refresh_detail(self.selected_job() or job)

    def refresh_queue(self) -> None:
        self.queue_model.set_jobs(self.manager.jobs)
        self.queue_title.setText(f"Archivos en cola ({len(self.manager.jobs)})")
        self.table.setVisible(bool(self.manager.jobs))
        self.empty_queue.setVisible(not self.manager.jobs)
        self.refresh_running_state()

    def refresh_detail(self, job: ConversionJob | None) -> None:
        if job is None:
            self.detail_name.setText("Sin seleccion")
            self.detail_meta.setText("Selecciona un archivo para ver el detalle.")
            self.status_banner.set_status(None)
            self.preview.clear()
            self.details.set_job(None)
            self.refresh_action_buttons(None)
            return
        self.detail_name.setText(job.name)
        self.detail_meta.setText(f"{file_type_label(job)} · {format_size(job.size_bytes)}")
        self.status_banner.set_status(job.status)
        self.preview.load_path(job.output_path)
        self.details.set_job(job)
        self.refresh_action_buttons(job)

    def selected_job(self) -> ConversionJob | None:
        if not self.selected_job_id:
            return None
        return next((job for job in self.manager.jobs if job.id == self.selected_job_id), None)

    def refresh_action_buttons(self, job: ConversionJob | None) -> None:
        has_output = bool(job and job.output_path and job.output_path.exists())
        self.copy_button.setEnabled(has_output)
        self.open_file_button.setEnabled(has_output)
        self.open_folder_button.setEnabled(has_output)

    def refresh_running_state(self) -> None:
        running = self.manager.is_running()
        pending_count = len(self.manager.pending())
        self.convert_button.setEnabled(pending_count > 0 and not running)
        self.cancel_button.setEnabled(running)
        if running:
            self.convert_button.setText("Procesando...")
            return
        if pending_count == 0:
            self.convert_button.setText("Convertir")
        elif pending_count == 1:
            self.convert_button.setText("Convertir 1 archivo")
        else:
            self.convert_button.setText(f"Convertir {pending_count} archivos")
        if self.manager.jobs:
            completed = sum(1 for job in self.manager.jobs if job.status == JobStatus.COMPLETED)
            failed = sum(1 for job in self.manager.jobs if job.status == JobStatus.FAILED)
            cancelled = sum(1 for job in self.manager.jobs if job.status == JobStatus.CANCELLED)
            self.status_changed.emit(
                f"{completed} completado(s), {failed} error(es), {cancelled} cancelado(s)"
            )

    def copy_markdown(self) -> None:
        QApplication.clipboard().setText(self.preview.to_plain_text())
        self.notify("Markdown copiado.")

    def open_output_file(self) -> None:
        job = self.selected_job()
        if job and job.output_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(job.output_path)))
            self.notify("Archivo abierto.")

    def open_output_folder(self) -> None:
        job = self.selected_job()
        folder = (
            job.output_path.parent
            if job and job.output_path
            else self.manager.settings.output_dir
        )
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
        self.notify("Carpeta abierta.")

    def notify(self, message: str, timeout_ms: int = 3500) -> None:
        self.notification.show_message(message, timeout_ms)

    def _select_index(self, index) -> None:
        self.selected_job_id = index.data(Qt.ItemDataRole.UserRole)
        self.refresh_detail(self.selected_job())

    def _open_queue_menu(self) -> None:
        menu = QMenu(self)
        menu.addAction("Limpiar completados", self.clear_finished)
        menu.addAction("Quitar cancelados", self.clear_finished)
        menu.addAction("Quitar finalizados", self.clear_finished)
        menu.exec(self.queue_menu_button.mapToGlobal(self.queue_menu_button.rect().bottomLeft()))

    def _open_selected_menu(self) -> None:
        menu = QMenu(self)
        job = self.selected_job()
        if job and job.status == JobStatus.FAILED:
            menu.addAction("Reintentar", self.retry_selected)
        if job and job.output_path:
            menu.addAction("Abrir Markdown", self.open_output_file)
            menu.addAction("Abrir carpeta", self.open_output_folder)
            menu.addAction("Copiar Markdown", self.copy_markdown)
        menu.exec(self.more_button.mapToGlobal(self.more_button.rect().bottomLeft()))

    def selected_status_label(self) -> str:
        job = self.selected_job()
        return STATUS_LABELS[job.status] if job else ""
