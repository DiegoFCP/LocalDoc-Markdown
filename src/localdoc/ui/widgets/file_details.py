from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLabel, QWidget

from localdoc.domain.models import ConversionJob
from localdoc.ui.models.queue_table_model import STATUS_LABELS, format_size


class FileDetails(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.rows: dict[str, QLabel] = {}
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for label in (
            "Tipo",
            "Tamano",
            "Hash",
            "Fecha",
            "Duracion",
            "Intentos",
            "Ruta origen",
            "Ruta salida",
            "OCR",
            "Estado",
        ):
            value = QLabel("-")
            value.setWordWrap(True)
            self.rows[label] = value
            layout.addRow(label, value)

    def set_job(self, job: ConversionJob | None) -> None:
        if job is None:
            for value in self.rows.values():
                value.setText("-")
            return
        duration = f"{job.duration_seconds:.2f}s" if job.duration_seconds is not None else "-"
        self.rows["Tipo"].setText(job.extension.upper() or "-")
        self.rows["Tamano"].setText(format_size(job.size_bytes))
        self.rows["Hash"].setText(job.source_hash or "-")
        self.rows["Fecha"].setText(job.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        self.rows["Duracion"].setText(duration)
        self.rows["Intentos"].setText(str(job.attempts))
        self.rows["Ruta origen"].setText(str(job.source_path))
        self.rows["Ruta salida"].setText(str(job.output_path) if job.output_path else "-")
        self.rows["OCR"].setText("Si" if job.uses_ocr else "No")
        self.rows["Estado"].setText(STATUS_LABELS[job.status])
