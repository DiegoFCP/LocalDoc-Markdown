from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from localdoc.application.conversion_manager import ConversionManager
from localdoc.application.settings_service import SettingsService
from localdoc.domain.enums import JobStatus
from localdoc.domain.exceptions import LocalDocError
from localdoc.domain.models import P0_EXTENSIONS, ConversionJob
from localdoc.infrastructure.tesseract_adapter import TesseractAdapter
from localdoc.ui.dialogs.settings_dialog import SettingsDialog
from localdoc.ui.models.queue_table_model import STATUS_LABELS, job_row
from localdoc.ui.widgets.drop_zone import DropZone

LOGGER = logging.getLogger(__name__)
PREVIEW_LIMIT = 200_000


class UiBridge(QObject):
    job_changed = Signal(object)


class MainWindow(QMainWindow):
    def __init__(
        self,
        manager: ConversionManager,
        settings_service: SettingsService,
        tesseract_adapter: TesseractAdapter,
    ) -> None:
        super().__init__()
        self.manager = manager
        self.settings_service = settings_service
        self.tesseract_adapter = tesseract_adapter
        self.bridge = UiBridge()
        self.bridge.job_changed.connect(self._on_job_changed)
        self.manager.on_job_changed = self.bridge.job_changed.emit
        self.selected_job_id: str | None = None

        self.setWindowTitle("LocalDoc")
        self.resize(1180, 760)
        self.setMinimumSize(960, 640)

        self._build_ui()
        self._refresh_engine_status()
        self._refresh_queue()

        self.timer = QTimer(self)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self._refresh_running_state)
        self.timer.start()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_top_bar())

        splitter = QSplitter()
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_detail_panel())
        splitter.setSizes([740, 380])
        layout.addWidget(splitter, 1)
        self.setCentralWidget(root)

    def _build_top_bar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("TopBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 14, 24, 14)

        brand = QLabel("LocalDoc")
        brand.setObjectName("Brand")
        self.engine_status = QLabel("Motor: verificando")
        self.engine_status.setObjectName("Pill")
        self.ocr_status = QLabel("OCR: verificando")
        self.ocr_status.setObjectName("Pill")
        settings = QPushButton("Configuracion")
        settings.clicked.connect(self._open_settings)

        layout.addWidget(brand)
        layout.addStretch(1)
        layout.addWidget(self.engine_status)
        layout.addWidget(self.ocr_status)
        layout.addWidget(settings)
        return bar

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 16, 24)
        layout.setSpacing(14)

        eyebrow = QLabel("Convierte, lee, edita, avanza")
        eyebrow.setObjectName("Muted")
        title = QLabel("Tu documento, listo para trabajar")
        title.setObjectName("HeroTitle")
        title.setWordWrap(True)

        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self._add_paths)
        self.drop_zone.browse_requested.connect(self._browse_files)

        actions = QHBoxLayout()
        self.convert_button = QPushButton("Convertir")
        self.convert_button.setObjectName("PrimaryButton")
        self.cancel_button = QPushButton("Cancelar")
        self.retry_button = QPushButton("Reintentar error")
        self.clear_button = QPushButton("Limpiar finalizados")
        self.convert_button.clicked.connect(self._start_conversion)
        self.cancel_button.clicked.connect(self._cancel_conversion)
        self.retry_button.clicked.connect(self._retry_selected)
        self.clear_button.clicked.connect(self._clear_finished)
        actions.addWidget(self.convert_button)
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.retry_button)
        actions.addWidget(self.clear_button)
        actions.addStretch(1)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Tipo", "Nombre", "Tamano", "Estado"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._select_current_row)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.banner = QLabel("Agrega documentos para comenzar.")
        self.banner.setObjectName("Muted")

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(self.drop_zone)
        layout.addLayout(actions)
        layout.addWidget(QLabel("Archivos en cola"))
        layout.addWidget(self.table, 1)
        layout.addWidget(self.banner)
        return panel

    def _build_detail_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Archivo seleccionado")
        title.setObjectName("HeroTitle")
        title.setStyleSheet("font-size: 18px;")
        self.detail_name = QLabel("Sin seleccion")
        self.detail_name.setWordWrap(True)
        self.detail_meta = QLabel("")
        self.detail_meta.setObjectName("Muted")
        self.detail_error = QLabel("")
        self.detail_error.setWordWrap(True)

        grid = QGridLayout()
        self.copy_button = QPushButton("Copiar Markdown")
        self.open_file_button = QPushButton("Abrir archivo")
        self.open_folder_button = QPushButton("Abrir carpeta")
        self.copy_button.clicked.connect(self._copy_markdown)
        self.open_file_button.clicked.connect(self._open_output_file)
        self.open_folder_button.clicked.connect(self._open_output_folder)
        grid.addWidget(self.copy_button, 0, 0)
        grid.addWidget(self.open_file_button, 0, 1)
        grid.addWidget(self.open_folder_button, 1, 0, 1, 2)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("La vista Markdown aparecera al finalizar la conversion.")

        layout.addWidget(title)
        layout.addWidget(self.detail_name)
        layout.addWidget(self.detail_meta)
        layout.addWidget(self.detail_error)
        layout.addLayout(grid)
        layout.addWidget(QLabel("Vista Markdown"))
        layout.addWidget(self.preview, 1)
        return panel

    def _refresh_engine_status(self) -> None:
        self.engine_status.setText("Motor listo")
        if self.tesseract_adapter.is_available():
            languages = self.tesseract_adapter.available_languages()
            label = "OCR disponible"
            if languages:
                label = f"OCR disponible: {', '.join(languages[:3])}"
            self.ocr_status.setText(label)
        else:
            self.ocr_status.setText("OCR no disponible")

    def _browse_files(self) -> None:
        patterns = " ".join(f"*{extension}" for extension in sorted(P0_EXTENSIONS))
        selected, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecciona documentos",
            "",
            f"Archivos compatibles ({patterns});;Todos los archivos (*.*)",
        )
        self._add_paths([Path(path) for path in selected])

    def _add_paths(self, paths: list[Path]) -> None:
        files = self._collect_files(paths)
        if not files:
            self._show_message("No se encontraron archivos compatibles.")
            return
        try:
            added = self.manager.add_files(files)
        except LocalDocError as exc:
            self._show_message(exc.user_message, str(exc))
            return
        except Exception as exc:
            self._show_message("No se pudieron agregar los archivos.", str(exc))
            return
        self.banner.setText(f"{len(added)} archivo(s) agregado(s).")
        self._refresh_queue()

    def _collect_files(self, paths: list[Path]) -> list[Path]:
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

    def _start_conversion(self) -> None:
        if not self.manager.pending():
            self._show_message("No hay archivos pendientes.")
            return
        self.banner.setText("Convirtiendo documentos...")
        self.manager.start()
        self._refresh_running_state()

    def _cancel_conversion(self) -> None:
        self.manager.cancel()
        self.banner.setText("Cancelacion solicitada.")

    def _retry_selected(self) -> None:
        job = self._selected_job()
        if job is None or job.status != JobStatus.FAILED:
            self._show_message("Selecciona un archivo con error para reintentar.")
            return
        self.manager.retry_failed(job.id)
        self._refresh_queue()

    def _clear_finished(self) -> None:
        self.manager.clear_finished()
        self.selected_job_id = None
        self._refresh_queue()
        self._refresh_detail(None)

    def _on_job_changed(self, job: ConversionJob) -> None:
        self.selected_job_id = self.selected_job_id or job.id
        self._refresh_queue()
        self._refresh_detail(self._selected_job() or job)

    def _refresh_queue(self) -> None:
        self.table.setRowCount(len(self.manager.jobs))
        for row_index, job in enumerate(self.manager.jobs):
            for column_index, value in enumerate(job_row(job)):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, job.id)
                self.table.setItem(row_index, column_index, item)
        self._refresh_running_state()

    def _select_current_row(self) -> None:
        items = self.table.selectedItems()
        if not items:
            return
        self.selected_job_id = items[0].data(Qt.ItemDataRole.UserRole)
        self._refresh_detail(self._selected_job())

    def _selected_job(self) -> ConversionJob | None:
        if not self.selected_job_id:
            return None
        return next((job for job in self.manager.jobs if job.id == self.selected_job_id), None)

    def _refresh_detail(self, job: ConversionJob | None) -> None:
        if job is None:
            self.detail_name.setText("Sin seleccion")
            self.detail_meta.setText("")
            self.detail_error.setText("")
            self.preview.clear()
            self._refresh_action_buttons(None)
            return
        duration = f"{job.duration_seconds:.2f}s" if job.duration_seconds is not None else "-"
        self.detail_name.setText(job.name)
        self.detail_meta.setText(
            f"{job.extension.upper()} · {STATUS_LABELS[job.status]} · "
            f"Intentos: {job.attempts} · Duracion: {duration}"
        )
        self.detail_error.setText(job.error if job.status == JobStatus.FAILED else "")
        self._load_preview(job)
        self._refresh_action_buttons(job)

    def _load_preview(self, job: ConversionJob) -> None:
        if not job.output_path or not job.output_path.exists():
            self.preview.clear()
            return
        text = job.output_path.read_text(encoding="utf-8", errors="replace")
        if len(text) > PREVIEW_LIMIT:
            text = text[:PREVIEW_LIMIT] + "\n\n[Preview truncada]"
        self.preview.setPlainText(text)

    def _refresh_action_buttons(self, job: ConversionJob | None) -> None:
        has_output = bool(job and job.output_path and job.output_path.exists())
        self.copy_button.setEnabled(has_output)
        self.open_file_button.setEnabled(has_output)
        self.open_folder_button.setEnabled(has_output)
        self.retry_button.setEnabled(bool(job and job.status == JobStatus.FAILED))

    def _refresh_running_state(self) -> None:
        running = self.manager.is_running()
        self.convert_button.setEnabled(bool(self.manager.pending()) and not running)
        self.cancel_button.setEnabled(running)
        if not running and self.manager.jobs:
            completed = sum(1 for job in self.manager.jobs if job.status == JobStatus.COMPLETED)
            failed = sum(1 for job in self.manager.jobs if job.status == JobStatus.FAILED)
            cancelled = sum(1 for job in self.manager.jobs if job.status == JobStatus.CANCELLED)
            self.banner.setText(
                f"Estado: {completed} completado(s), {failed} error(es), "
                f"{cancelled} cancelado(s)."
            )

    def _copy_markdown(self) -> None:
        QApplication.clipboard().setText(self.preview.toPlainText())

    def _open_output_file(self) -> None:
        job = self._selected_job()
        if job and job.output_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(job.output_path)))

    def _open_output_folder(self) -> None:
        job = self._selected_job()
        folder = (
            job.output_path.parent
            if job and job.output_path
            else self.manager.settings.output_dir
        )
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.manager.settings, self)
        if dialog.exec():
            settings = dialog.to_settings()
            self.settings_service.save(settings)
            self.manager.settings = settings
            self.tesseract_adapter = TesseractAdapter(settings.tesseract_path)
            self._refresh_engine_status()

    def _show_message(self, message: str, details: str = "") -> None:
        LOGGER.info("%s %s", message, details)
        box = QMessageBox(self)
        box.setWindowTitle("LocalDoc")
        box.setText(message)
        if details:
            box.setDetailedText(details)
        box.exec()
