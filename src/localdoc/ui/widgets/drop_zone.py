from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from localdoc.ui.components import SecondaryButton
from localdoc.ui.icons import icon


class DropZone(QFrame):
    files_dropped = Signal(list)
    browse_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("DropZone")
        self.setProperty("dragActive", False)
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        self.icon = QLabel()
        self.icon.setPixmap(icon("upload", "blue", 36).pixmap(QSize(36, 36)))
        self.icon.setAccessibleName("Icono de carga de documentos")
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel("Arrastra tus documentos aqui")
        self.title.setObjectName("HeroTitle")
        self.title.setWordWrap(True)
        self.title.setStyleSheet("font-size: 20px;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("o selecciona archivos desde tu equipo")
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        formats = QLabel("PDF · Word · Excel · PowerPoint · Imagenes")
        formats.setObjectName("Pill")
        formats.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button = SecondaryButton(
            "Seleccionar archivos",
            tooltip="Seleccionar documentos locales para convertir",
            icon_name="add",
            icon_color="blue",
        )
        button.clicked.connect(self.browse_requested.emit)

        layout.addStretch(1)
        layout.addWidget(self.icon)
        layout.addWidget(self.title)
        layout.addWidget(subtitle)
        layout.addWidget(formats)
        layout.addWidget(button)
        layout.addStretch(1)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            self._set_drag_active(True)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self._set_drag_active(False)
        event.accept()

    def dropEvent(self, event) -> None:
        self._set_drag_active(False)
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]
        if paths:
            self.files_dropped.emit(paths)
        event.acceptProposedAction()

    def _set_drag_active(self, active: bool) -> None:
        self.setProperty("dragActive", active)
        self.title.setText(
            "Suelta para agregar tus archivos" if active else "Arrastra tus documentos aqui"
        )
        self.style().unpolish(self)
        self.style().polish(self)
