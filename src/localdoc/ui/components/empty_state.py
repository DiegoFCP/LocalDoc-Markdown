from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EmptyState(QWidget):
    def __init__(self, title: str, description: str, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)
        self.title = QLabel(title)
        self.title.setObjectName("CardTitle")
        self.description = QLabel(description)
        self.description.setObjectName("Muted")
        self.description.setWordWrap(True)
        layout.addWidget(self.title)
        layout.addWidget(self.description)
