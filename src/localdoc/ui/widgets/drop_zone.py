from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from localdoc.ui.components import SecondaryButton


class DropZone(QFrame):
    files_dropped = Signal(list)
    browse_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        title = QLabel("Arrastra tus documentos aqui")
        title.setObjectName("HeroTitle")
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 20px;")

        subtitle = QLabel("Procesamiento 100% local. Tus archivos permanecen en tu equipo.")
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)

        button = SecondaryButton(
            "Seleccionar archivos",
            tooltip="Seleccionar documentos locales para convertir",
        )
        button.clicked.connect(self.browse_requested.emit)

        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(button)
        layout.addStretch(1)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]
        if paths:
            self.files_dropped.emit(paths)
        event.acceptProposedAction()
