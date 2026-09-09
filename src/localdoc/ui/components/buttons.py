from __future__ import annotations

from PySide6.QtWidgets import QPushButton


class BaseButton(QPushButton):
    object_name = "SecondaryButton"

    def __init__(
        self,
        text: str = "",
        *,
        tooltip: str = "",
        accessible_name: str = "",
        parent=None,
    ) -> None:
        super().__init__(text, parent)
        self.setObjectName(self.object_name)
        if tooltip:
            self.setToolTip(tooltip)
        self.setAccessibleName(accessible_name or text)
        if tooltip:
            self.setAccessibleDescription(tooltip)


class PrimaryButton(BaseButton):
    object_name = "PrimaryButton"


class SecondaryButton(BaseButton):
    object_name = "SecondaryButton"


class GhostButton(BaseButton):
    object_name = "GhostButton"


class DestructiveButton(BaseButton):
    object_name = "DestructiveButton"


class IconButton(BaseButton):
    object_name = "IconButton"

    def __init__(
        self,
        text: str,
        *,
        tooltip: str,
        accessible_name: str = "",
        parent=None,
    ) -> None:
        super().__init__(
            text,
            tooltip=tooltip,
            accessible_name=accessible_name or tooltip,
            parent=parent,
        )
        self.setFixedHeight(36)
