from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from localdoc.application.conversion_manager import ConversionManager
from localdoc.application.settings_service import SettingsService
from localdoc.domain.models import P0_EXTENSIONS, ConversionJob
from localdoc.infrastructure.tesseract_adapter import TesseractAdapter
from localdoc.ui.components import GhostButton, NavigationTabs
from localdoc.ui.dialogs.settings_dialog import SettingsDialog
from localdoc.ui.theme import ThemeManager
from localdoc.ui.views import ConverterView, HistoryView


class UiBridge(QObject):
    job_changed = Signal(object)


class MainWindow(QMainWindow):
    def __init__(
        self,
        manager: ConversionManager,
        settings_service: SettingsService,
        tesseract_adapter: TesseractAdapter,
    ) -> None:
        super().__init__()
        self.manager = manager
        self.settings_service = settings_service
        self.tesseract_adapter = tesseract_adapter
        self.bridge = UiBridge()
        self.bridge.job_changed.connect(self._on_job_changed)
        self.manager.on_job_changed = self.bridge.job_changed.emit

        self.setWindowTitle("LocalDoc")
        self.resize(1180, 760)
        self.setMinimumSize(1000, 650)
        self._apply_window_icon()

        self._build_ui()
        self._install_shortcuts()
        self._refresh_engine_status()

        self.timer = QTimer(self)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self._refresh_running_state)
        self.timer.start()

    @property
    def table(self):
        return self.converter_view.table

    @property
    def preview(self):
        return self.converter_view.preview.editor

    @property
    def convert_button(self):
        return self.converter_view.convert_button

    @property
    def cancel_button(self):
        return self.converter_view.cancel_button

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_top_bar())

        self.stack = QStackedWidget()
        self.converter_view = ConverterView(self.manager)
        self.history_view = HistoryView(self.manager.history_service)
        self.converter_view.browse_requested.connect(self._browse_files)
        self.stack.addWidget(self.converter_view)
        self.stack.addWidget(self.history_view)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)

    def _build_top_bar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("TopBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(12)

        symbol = QLabel("LD")
        symbol.setObjectName("BrandSymbol")
        symbol.setAccessibleName("Logo LocalDoc")
        brand = QLabel("LocalDoc")
        brand.setObjectName("Brand")

        self.navigation = NavigationTabs()
        self.navigation.current_changed.connect(self._switch_view)

        self.engine_status = QLabel("Motor: verificando")
        self.engine_status.setObjectName("Pill")
        self.ocr_status = QLabel("OCR: verificando")
        self.ocr_status.setObjectName("Pill")
        self.settings_button = GhostButton(
            "Configuracion",
            tooltip="Abrir configuracion",
            accessible_name="Configuracion",
        )
        self.settings_button.clicked.connect(self._open_settings)

        layout.addWidget(symbol)
        layout.addWidget(brand)
        layout.addWidget(self.navigation)
        layout.addStretch(1)
        layout.addWidget(self.engine_status)
        layout.addWidget(self.ocr_status)
        layout.addWidget(self.settings_button)
        return bar

    def _install_shortcuts(self) -> None:
        shortcuts = [
            ("Ctrl+O", self._browse_files),
            ("Ctrl+Return", self.converter_view.start_conversion),
            ("Ctrl+,", self._open_settings),
            ("Ctrl+H", lambda: self._switch_view(1)),
            ("Ctrl+1", lambda: self._switch_view(0)),
            ("Ctrl+2", lambda: self._switch_view(1)),
        ]
        for key, callback in shortcuts:
            action = QAction(self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(callback)
            self.addAction(action)

    def _switch_view(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.navigation.set_current_index(index)
        if index == 1:
            self.history_view.refresh()

    def _refresh_engine_status(self) -> None:
        self.engine_status.setText("Motor listo")
        if self.tesseract_adapter.is_available():
            languages = self.tesseract_adapter.available_languages()
            label = "OCR disponible"
            if languages:
                label = f"OCR disponible: {', '.join(languages[:3])}"
            self.ocr_status.setText(label)
        else:
            self.ocr_status.setText("OCR no disponible")

    def _browse_files(self) -> None:
        patterns = " ".join(f"*{extension}" for extension in sorted(P0_EXTENSIONS))
        selected, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecciona documentos",
            "",
            f"Archivos compatibles ({patterns});;Todos los archivos (*.*)",
        )
        self._add_paths([Path(path) for path in selected])

    def _add_paths(self, paths: list[Path]) -> None:
        self.converter_view.add_paths(paths)

    def _on_job_changed(self, job: ConversionJob) -> None:
        self.converter_view.refresh_job(job)
        self.history_view.refresh()

    def _refresh_running_state(self) -> None:
        self.converter_view.refresh_running_state()

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.manager.settings, self.tesseract_adapter, self)
        if dialog.exec():
            settings = dialog.to_settings()
            self.settings_service.save(settings)
            self.manager.settings = settings
            self.tesseract_adapter = TesseractAdapter(settings.tesseract_path)
            self._apply_theme(settings.theme_mode)
            self._refresh_engine_status()

    def _apply_theme(self, theme_mode: str) -> None:
        from PySide6.QtWidgets import QApplication

        instance = QApplication.instance()
        if instance is not None:
            ThemeManager.from_value(theme_mode).apply(instance)

    def _apply_window_icon(self) -> None:
        icon_path = Path(__file__).parent / "resources" / "branding" / "localdoc.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
