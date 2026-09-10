from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

PREVIEW_LIMIT = 200_000


class MarkdownPreview(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.notice = QLabel("")
        self.notice.setObjectName("Muted")
        self.notice.setWordWrap(True)
        self.editor = QTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setPlaceholderText("Selecciona un archivo convertido para ver su Markdown.")
        layout.addWidget(self.notice)
        layout.addWidget(self.editor, 1)

    def clear(self) -> None:
        self.notice.setText("")
        self.editor.clear()

    def to_plain_text(self) -> str:
        return self.editor.toPlainText()

    def load_path(self, path: Path | None) -> None:
        if not path or not path.exists():
            self.notice.setText("")
            self.editor.clear()
            return
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > PREVIEW_LIMIT:
            text = text[:PREVIEW_LIMIT]
            self.notice.setText(
                "Vista previa limitada por tamano. Abre el archivo para ver el contenido completo."
            )
        else:
            self.notice.setText("")
        self.editor.setPlainText(text)
