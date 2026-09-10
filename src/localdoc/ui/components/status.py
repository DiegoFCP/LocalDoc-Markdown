from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from localdoc.domain.enums import JobStatus


class StatusBadge(QLabel):
    def __init__(self, text: str = "", tone: str = "Info", parent=None) -> None:
        super().__init__(text, parent)
        self.setObjectName(f"StatusBadge{tone}")


class StatusBanner(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusBannerInfo")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)
        self.title = QLabel("Sin seleccion")
        self.title.setObjectName("CardTitle")
        self.description = QLabel("Selecciona un archivo para ver su estado.")
        self.description.setObjectName("Muted")
        self.description.setWordWrap(True)
        layout.addWidget(self.title)
        layout.addWidget(self.description)

    def set_status(self, status: JobStatus | None) -> None:
        content = {
            None: ("Sin seleccion", "Selecciona un archivo para ver su estado.", "Info"),
            JobStatus.QUEUED: ("En espera", "Este archivo esta listo para convertirse.", "Info"),
            JobStatus.PROCESSING: ("Procesando", "Estamos convirtiendo este documento.", "Warning"),
            JobStatus.COMPLETED: (
                "Conversion completada",
                "Tu documento ya esta en formato Markdown.",
                "Success",
            ),
            JobStatus.FAILED: (
                "No se pudo convertir",
                "Revisa los detalles e intenta nuevamente.",
                "Danger",
            ),
            JobStatus.CANCELLED: ("Cancelado", "La conversion fue cancelada.", "Muted"),
        }
        title, description, tone = content[status]
        self.setObjectName(f"StatusBanner{tone}")
        self.title.setText(title)
        self.description.setText(description)
        self.style().unpolish(self)
        self.style().polish(self)
