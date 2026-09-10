from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel


class InlineNotification(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__("", parent)
        self.setObjectName("InlineNotification")
        self.setWordWrap(True)
        self.hide()

    def show_message(self, text: str, timeout_ms: int = 3500) -> None:
        self.setText(text)
        self.show()
        if timeout_ms > 0:
            QTimer.singleShot(timeout_ms, self.hide)
