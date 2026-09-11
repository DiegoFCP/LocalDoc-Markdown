from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap

BRANDING_DIR = Path(__file__).parent / "resources" / "branding"


def branding_path(filename: str) -> Path:
    return BRANDING_DIR / filename


def branding_pixmap(filename: str, size: int) -> QPixmap:
    pixmap = QPixmap(str(branding_path(filename)))
    if pixmap.isNull():
        return pixmap
    return pixmap.scaled(
        QSize(size, size),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
