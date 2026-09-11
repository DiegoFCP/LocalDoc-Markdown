from __future__ import annotations

import multiprocessing
import sys

from PySide6.QtWidgets import QApplication

from localdoc.application.factory import build_conversion_manager, build_settings_service
from localdoc.infrastructure.logging_config import configure_logging
from localdoc.infrastructure.paths import get_default_paths
from localdoc.infrastructure.tesseract_adapter import TesseractAdapter
from localdoc.ui.assets import branding_path
from localdoc.ui.main_window import MainWindow
from localdoc.ui.theme import ThemeManager


def main() -> int:
    multiprocessing.freeze_support()
    paths = get_default_paths()
    paths.ensure()
    configure_logging(paths)

    settings_service = build_settings_service(paths)
    manager = build_conversion_manager(paths)
    app = QApplication(sys.argv)
    app.setApplicationName("LocalDoc")
    icon_path = branding_path("localdoc.ico")
    if icon_path.exists():
        from PySide6.QtGui import QIcon

        app.setWindowIcon(QIcon(str(icon_path)))
    ThemeManager.from_value(manager.settings.theme_mode).apply(app)

    window = MainWindow(
        manager=manager,
        settings_service=settings_service,
        tesseract_adapter=TesseractAdapter(manager.settings.tesseract_path),
    )
    window.show()
    return app.exec()
