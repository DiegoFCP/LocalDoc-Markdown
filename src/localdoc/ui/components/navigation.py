from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QWidget

from localdoc.ui.components.buttons import GhostButton


class NavigationTabs(QWidget):
    current_changed = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.convert_button = self._add_tab("Convertir", 0, "Ir a conversion")
        self.history_button = self._add_tab("Historial", 1, "Ir al historial")
        layout.addWidget(self.convert_button)
        layout.addWidget(self.history_button)
        self.group.idClicked.connect(self.current_changed.emit)
        self.set_current_index(0)

    def set_current_index(self, index: int) -> None:
        button = self.group.button(index)
        if button:
            button.setChecked(True)
            self._refresh_tab_state()

    def _add_tab(self, text: str, tab_id: int, tooltip: str) -> GhostButton:
        button = GhostButton(text, tooltip=tooltip)
        button.setCheckable(True)
        self.group.addButton(button, tab_id)
        button.toggled.connect(self._refresh_tab_state)
        return button

    def _refresh_tab_state(self) -> None:
        for button in self.group.buttons():
            button.setProperty("active", button.isChecked())
            button.style().unpolish(button)
            button.style().polish(button)
