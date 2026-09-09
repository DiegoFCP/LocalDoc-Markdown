from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)

from localdoc.domain.models import AppSettings, FileLimits
from localdoc.ui.components import PrimaryButton, SecondaryButton


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Configuracion")
        self.setMinimumWidth(560)

        self.output_dir = QLineEdit(str(settings.output_dir))
        self.tesseract_path = QLineEdit(str(settings.tesseract_path or ""))
        self.ocr_enabled = QCheckBox("Habilitar OCR cuando Tesseract este disponible")
        self.ocr_enabled.setChecked(settings.ocr_enabled)
        self.ocr_language = QLineEdit(settings.ocr_language)
        self.max_files = QSpinBox()
        self.max_files.setRange(1, 1000)
        self.max_files.setValue(settings.file_limits.max_files)
        self.max_size = QSpinBox()
        self.max_size.setRange(1, 2048)
        self.max_size.setValue(settings.file_limits.max_file_size_mb)
        self.timeout = QSpinBox()
        self.timeout.setRange(10, 3600)
        self.timeout.setValue(settings.conversion_timeout_seconds)

        form = QFormLayout()
        form.addRow("Carpeta de salida", self._path_row(self.output_dir, self._choose_output_dir))
        form.addRow("OCR", self.ocr_enabled)
        form.addRow("Idioma OCR", self.ocr_language)
        form.addRow("Ruta Tesseract", self._path_row(self.tesseract_path, self._choose_tesseract))
        form.addRow("Maximo de archivos", self.max_files)
        form.addRow("Maximo MB por archivo", self.max_size)
        form.addRow("Timeout por archivo", self.timeout)

        buttons = QHBoxLayout()
        save = PrimaryButton("Guardar", tooltip="Guardar configuracion")
        cancel = SecondaryButton("Cancelar", tooltip="Cerrar sin guardar cambios")
        save.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        buttons.addStretch(1)
        buttons.addWidget(cancel)
        buttons.addWidget(save)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

    def to_settings(self) -> AppSettings:
        tesseract_text = self.tesseract_path.text().strip()
        return AppSettings(
            output_dir=Path(self.output_dir.text()).expanduser(),
            ocr_enabled=self.ocr_enabled.isChecked(),
            ocr_language=self.ocr_language.text().strip() or "spa+eng",
            tesseract_path=Path(tesseract_text) if tesseract_text else None,
            file_limits=FileLimits(
                max_files=self.max_files.value(),
                max_file_size_mb=self.max_size.value(),
            ),
            conversion_timeout_seconds=self.timeout.value(),
        )

    def _path_row(self, line_edit: QLineEdit, callback) -> QHBoxLayout:
        row = QHBoxLayout()
        button = SecondaryButton("Elegir", tooltip="Seleccionar ruta")
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
