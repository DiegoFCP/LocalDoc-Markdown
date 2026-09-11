from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from localdoc.domain.models import AppSettings, FileLimits
from localdoc.infrastructure.tesseract_adapter import TesseractAdapter
from localdoc.ui.components import PrimaryButton, SecondaryButton


class SettingsDialog(QDialog):
    def __init__(
        self,
        settings: AppSettings,
        tesseract_adapter: TesseractAdapter | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.tesseract_adapter = tesseract_adapter
        self.setWindowTitle("Configuración")
        self.setMinimumWidth(620)

        self.output_dir = QLineEdit(str(settings.output_dir))
        self.output_dir.setAccessibleName("Carpeta de salida")
        self.tesseract_path = QLineEdit(str(settings.tesseract_path or ""))
        self.tesseract_path.setAccessibleName("Ruta Tesseract")
        self.ocr_enabled = QCheckBox("Habilitar OCR")
        self.ocr_enabled.setChecked(settings.ocr_enabled)
        self.ocr_enabled.setAccessibleName("Habilitar OCR")
        self.ocr_language = QComboBox()
        self.ocr_language.setEditable(True)
        self.ocr_language.addItems(["spa+eng", "spa", "eng"])
        self.ocr_language.setCurrentText(settings.ocr_language)
        self.ocr_language.setAccessibleName("Idioma OCR")
        self.theme_mode = QComboBox()
        self.theme_mode.addItem("Sistema", "system")
        self.theme_mode.addItem("Claro", "light")
        self.theme_mode.addItem("Oscuro", "dark")
        index = self.theme_mode.findData(settings.theme_mode)
        self.theme_mode.setCurrentIndex(index if index >= 0 else 0)
        self.theme_mode.setAccessibleName("Tema")
        self.max_files = QSpinBox()
        self.max_files.setRange(1, 1000)
        self.max_files.setValue(settings.file_limits.max_files)
        self.max_size = QSpinBox()
        self.max_size.setRange(1, 2048)
        self.max_size.setValue(settings.file_limits.max_file_size_mb)
        self.timeout = QSpinBox()
        self.timeout.setRange(10, 3600)
        self.timeout.setValue(settings.conversion_timeout_seconds)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        title = QLabel("Configuración")
        title.setObjectName("HeroTitle")
        title.setStyleSheet("font-size: 22px;")
        layout.addWidget(title)
        layout.addWidget(self._section("General", self._general_form()))
        layout.addWidget(self._section("Apariencia", self._appearance_form()))
        layout.addWidget(self._section("OCR", self._ocr_form()))
        layout.addWidget(self._section("Procesamiento", self._processing_form()))
        layout.addLayout(self._buttons())

    def to_settings(self) -> AppSettings:
        tesseract_text = self.tesseract_path.text().strip()
        return AppSettings(
            output_dir=Path(self.output_dir.text()).expanduser(),
            ocr_enabled=self.ocr_enabled.isChecked(),
            ocr_language=self.ocr_language.currentText().strip() or "spa+eng",
            tesseract_path=Path(tesseract_text) if tesseract_text else None,
            theme_mode=str(self.theme_mode.currentData() or "system"),
            file_limits=FileLimits(
                max_files=self.max_files.value(),
                max_file_size_mb=self.max_size.value(),
            ),
            conversion_timeout_seconds=self.timeout.value(),
        )

    def _section(self, title: str, body: QWidget) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel(title.upper())
        heading.setObjectName("Muted")
        layout.addWidget(heading)
        layout.addWidget(body)
        return section

    def _general_form(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Carpeta de salida", self._path_row(self.output_dir, self._choose_output_dir))
        body = QWidget()
        body.setLayout(form)
        return body

    def _appearance_form(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Tema", self.theme_mode)
        body = QWidget()
        body.setLayout(form)
        return body

    def _ocr_form(self) -> QWidget:
        form = QFormLayout()
        status = "No detectado"
        if self.tesseract_adapter and self.tesseract_adapter.is_available():
            status = "Detectado"
        self.tesseract_status = QLabel(status)
        self.tesseract_status.setObjectName("CardTitle")
        form.addRow("Estado", self.tesseract_status)
        form.addRow("OCR", self.ocr_enabled)
        form.addRow("Idioma", self.ocr_language)
        form.addRow("Tesseract", self._path_row(self.tesseract_path, self._choose_tesseract))
        body = QWidget()
        body.setLayout(form)
        return body

    def _processing_form(self) -> QWidget:
        form = QFormLayout()
        form.addRow("Maximo archivos", self.max_files)
        form.addRow("Maximo MB/archivo", self.max_size)
        form.addRow("Timeout", self.timeout)
        body = QWidget()
        body.setLayout(form)
        return body

    def _buttons(self) -> QHBoxLayout:
        buttons = QHBoxLayout()
        save = PrimaryButton(
            "Guardar",
            tooltip="Guardar configuracion",
            icon_name="check",
            icon_color="#FFFFFF",
        )
        cancel = SecondaryButton(
            "Cancelar",
            tooltip="Cerrar sin guardar cambios",
            icon_name="minus",
            icon_color="slate",
        )
        save.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        buttons.addStretch(1)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        return buttons

    def _path_row(self, line_edit: QLineEdit, callback) -> QHBoxLayout:
        row = QHBoxLayout()
        button = SecondaryButton(
            "Cambiar",
            tooltip="Seleccionar ruta",
            icon_name="folder",
            icon_color="coral",
        )
        button.clicked.connect(callback)
        row.addWidget(line_edit)
        row.addWidget(button)
        return row

    def _choose_output_dir(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Selecciona carpeta de salida")
        if selected:
            self.output_dir.setText(selected)

    def _choose_tesseract(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona tesseract.exe",
            r"C:\Program Files\Tesseract-OCR",
            "Tesseract (tesseract.exe);;Ejecutables (*.exe);;Todos los archivos (*.*)",
        )
        if selected:
            self.tesseract_path.setText(selected)
