from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from localdoc.domain.enums import JobStatus
from localdoc.ui.assets import branding_pixmap
from localdoc.ui.icons import status_icon


class StatusBadge(QLabel):
    def __init__(self, text: str = "", tone: str = "Info", parent=None) -> None:
        super().__init__(text, parent)
        self.setObjectName(f"StatusBadge{tone}")


class StatusBanner(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusBannerInfo")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)
        self.icon = QLabel()
        self.icon.setAccessibleName("Icono de estado")
        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(2)
        self.title = QLabel("Sin selección")
        self.title.setObjectName("CardTitle")
        self.description = QLabel("Selecciona un archivo para ver su estado.")
        self.description.setObjectName("Muted")
        self.description.setWordWrap(True)
        content.addWidget(self.title)
        content.addWidget(self.description)
        layout.addWidget(self.icon)
        layout.addLayout(content, 1)

    def set_status(self, status: JobStatus | None) -> None:
        content = {
            None: ("Sin selección", "Selecciona un archivo para ver su estado.", "Info"),
            JobStatus.QUEUED: ("En espera", "Este archivo esta listo para convertirse.", "Info"),
            JobStatus.PROCESSING: (
                "Convirtiendo",
                "Estamos convirtiendo este documento.",
                "Warning",
            ),
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
        if status == JobStatus.COMPLETED:
            self.icon.setPixmap(branding_pixmap("localdoc-conversion-complete.png", 58))
        elif status == JobStatus.PROCESSING:
            self.icon.setPixmap(branding_pixmap("localdoc-upload-illustration.png", 58))
        else:
            icon_key = status.value if status else "queued"
            self.icon.setPixmap(status_icon(icon_key, 24).pixmap(QSize(24, 24)))
        self.title.setText(title)
        self.description.setText(description)
        self.style().unpolish(self)
        self.style().polish(self)
