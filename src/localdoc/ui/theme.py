from __future__ import annotations

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from localdoc.ui.tokens import DARK_TOKENS, LIGHT_TOKENS, DesignTokens, ThemeMode


class ThemeManager:
    def __init__(self, mode: ThemeMode = ThemeMode.SYSTEM) -> None:
        self.mode = mode

    @classmethod
    def from_value(cls, value: str | ThemeMode) -> ThemeManager:
        try:
            mode = value if isinstance(value, ThemeMode) else ThemeMode(value)
        except ValueError:
            mode = ThemeMode.SYSTEM
        return cls(mode)

    def resolve_mode(self, app: QApplication | None = None) -> ThemeMode:
        if self.mode != ThemeMode.SYSTEM:
            return self.mode
        if app is None:
            app = QApplication.instance()
        if app is None:
            return ThemeMode.LIGHT
        window_color = app.palette().color(QPalette.ColorRole.Window)
        brightness = (
            window_color.red() * 0.299
            + window_color.green() * 0.587
            + window_color.blue() * 0.114
        )
        return ThemeMode.DARK if brightness < 128 else ThemeMode.LIGHT

    def tokens(self, app: QApplication | None = None) -> DesignTokens:
        return DARK_TOKENS if self.resolve_mode(app) == ThemeMode.DARK else LIGHT_TOKENS

    def stylesheet(self, app: QApplication | None = None) -> str:
        return build_stylesheet(self.tokens(app))

    def apply(self, app: QApplication) -> None:
        app.setStyleSheet(self.stylesheet(app))


def build_stylesheet(tokens: DesignTokens) -> str:
    colors = tokens.colors
    spacing = tokens.spacing
    radius = tokens.radius
    typography = tokens.typography
    return f"""
QMainWindow, QWidget {{
    background: {colors.background};
    color: {colors.text_primary};
    font-family: {typography.interface_family};
    font-size: {typography.body_size}px;
}}

QFrame#TopBar {{
    background: {colors.background};
    border-bottom: 1px solid {colors.border};
}}

QLabel#Brand {{
    font-family: {typography.brand_family};
    font-size: {typography.display_size - 8}px;
    font-weight: 700;
}}

QLabel#HeroTitle {{
    font-family: {typography.brand_family};
    font-size: {typography.display_size - 4}px;
    font-weight: 700;
}}

QLabel#Muted {{
    color: {colors.text_muted};
}}

QLabel#Pill {{
    background: {colors.accent_soft};
    color: {colors.text_secondary};
    border: 1px solid {colors.border};
    border-radius: {radius.radius_md}px;
    padding: {spacing.space_2}px {spacing.space_3}px;
}}

QPushButton {{
    background: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border_strong};
    border-radius: {radius.radius_sm}px;
    padding: {spacing.space_2}px {spacing.space_4}px;
    min-height: 20px;
}}

QPushButton:hover {{
    background: {colors.surface_accent};
    border-color: {colors.accent};
}}

QPushButton:pressed {{
    background: {colors.surface_alt};
}}

QPushButton:focus, QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus,
QTableWidget:focus, QTableView:focus, QTabBar:focus {{
    border: 2px solid {colors.focus};
}}

QPushButton:disabled {{
    background: {colors.surface_alt};
    color: {colors.text_muted};
    border-color: {colors.border};
}}

QPushButton#PrimaryButton {{
    background: {colors.accent_primary};
    border-color: {colors.accent_primary};
    color: #FFFFFF;
    font-weight: 700;
}}

QPushButton#PrimaryButton:hover {{
    background: {colors.accent_hover};
    border-color: {colors.accent_hover};
}}

QPushButton#SecondaryButton {{
    background: {colors.surface};
    border-color: {colors.border_strong};
}}

QPushButton#GhostButton {{
    background: transparent;
    border-color: transparent;
    color: {colors.text_secondary};
}}

QPushButton#GhostButton:hover {{
    background: {colors.surface_alt};
    border-color: {colors.border};
}}

QPushButton#GhostButton[active="true"] {{
    background: {colors.surface_accent};
    border-color: {colors.border};
    color: {colors.text_primary};
    font-weight: 700;
}}

QPushButton#DestructiveButton {{
    color: {colors.danger};
    border-color: {colors.danger};
    background: {colors.danger_soft};
}}

QPushButton#IconButton {{
    min-width: 34px;
    max-width: 40px;
    padding-left: {spacing.space_2}px;
    padding-right: {spacing.space_2}px;
}}

QFrame#DropZone {{
    background: {colors.surface_accent};
    border: 2px dashed {colors.accent};
    border-radius: {radius.radius_md}px;
}}

QFrame#DropZone[dragActive="true"] {{
    background: {colors.warning_soft};
    border-color: {colors.accent_primary};
}}

QTableWidget {{
    background: {colors.surface};
    border: 1px solid {colors.border};
    border-radius: {radius.radius_md}px;
    gridline-color: {colors.border};
    selection-background-color: {colors.accent_soft};
    selection-color: {colors.text_primary};
}}

QTableView {{
    background: {colors.surface};
    border: 1px solid {colors.border};
    border-radius: {radius.radius_md}px;
    gridline-color: {colors.border};
    selection-background-color: {colors.accent_soft};
    selection-color: {colors.text_primary};
    alternate-background-color: {colors.surface_alt};
}}

QHeaderView::section {{
    background: {colors.background};
    color: {colors.text_primary};
    border: 0;
    border-bottom: 1px solid {colors.border};
    padding: {spacing.space_2}px;
    font-weight: 700;
}}

QTextEdit {{
    background: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    border-radius: {radius.radius_md}px;
    font-family: {typography.mono_family};
    font-size: {typography.small_size}px;
}}

QLineEdit, QSpinBox {{
    background: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border_strong};
    border-radius: {radius.radius_sm}px;
    padding: {spacing.space_2}px;
}}

QComboBox {{
    background: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border_strong};
    border-radius: {radius.radius_sm}px;
    padding: {spacing.space_2}px;
}}

QCheckBox {{
    color: {colors.text_primary};
}}

QFrame#SurfacePanel {{
    background: {colors.surface};
    border-left: 1px solid {colors.border};
}}

QLabel#CardTitle {{
    font-size: {typography.card_title_size}px;
    font-weight: 700;
}}

QLabel#InlineNotification {{
    background: {colors.info_soft};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    border-radius: {radius.radius_sm}px;
    padding: {spacing.space_2}px {spacing.space_3}px;
}}

QWidget#StatusBannerInfo {{
    background: {colors.info_soft};
    border: 1px solid {colors.info};
    border-radius: {radius.radius_md}px;
}}

QWidget#StatusBannerWarning {{
    background: {colors.warning_soft};
    border: 1px solid {colors.warning};
    border-radius: {radius.radius_md}px;
}}

QWidget#StatusBannerSuccess {{
    background: {colors.success_soft};
    border: 1px solid {colors.success};
    border-radius: {radius.radius_md}px;
}}

QWidget#StatusBannerDanger {{
    background: {colors.danger_soft};
    border: 1px solid {colors.danger};
    border-radius: {radius.radius_md}px;
}}

QWidget#StatusBannerMuted {{
    background: {colors.surface_alt};
    border: 1px solid {colors.border};
    border-radius: {radius.radius_md}px;
}}

QLabel#BrandSymbol {{
    background: {colors.accent_primary};
    color: #FFFFFF;
    border-radius: {radius.radius_sm}px;
    font-weight: 800;
    padding: 3px 7px;
}}
"""


APP_STYLESHEET = ThemeManager(ThemeMode.LIGHT).stylesheet()
