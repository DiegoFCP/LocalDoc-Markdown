from __future__ import annotations

from PySide6.QtWidgets import QApplication

from localdoc.ui.components import GhostButton, IconButton, PrimaryButton, SecondaryButton
from localdoc.ui.theme import ThemeManager, build_stylesheet
from localdoc.ui.tokens import DARK_TOKENS, LIGHT_TOKENS, ThemeMode


def test_light_theme_stylesheet_uses_accessible_primary_color() -> None:
    stylesheet = build_stylesheet(LIGHT_TOKENS)

    assert "#286BF4" in stylesheet
    assert "#FF654F" in stylesheet
    assert "#EAF2FF" in stylesheet
    assert "QPushButton:focus" in stylesheet
    assert "QPushButton#PrimaryButton" in stylesheet


def test_dark_theme_stylesheet_uses_dark_palette() -> None:
    stylesheet = build_stylesheet(DARK_TOKENS)

    assert "#10131C" in stylesheet
    assert "#EEF2FA" in stylesheet
    assert "#8B6CFF" in stylesheet


def test_theme_manager_resolves_explicit_modes() -> None:
    assert ThemeManager(ThemeMode.LIGHT).resolve_mode() == ThemeMode.LIGHT
    assert ThemeManager(ThemeMode.DARK).resolve_mode() == ThemeMode.DARK
    assert ThemeManager.from_value("missing").mode == ThemeMode.SYSTEM


def test_theme_manager_applies_stylesheet(qtbot) -> None:
    app = QApplication.instance()
    assert app is not None

    ThemeManager(ThemeMode.LIGHT).apply(app)

    assert "QPushButton#PrimaryButton" in app.styleSheet()


def test_button_components_set_roles_and_accessibility(qtbot) -> None:
    buttons = [
        PrimaryButton("Convertir", tooltip="Convertir archivos pendientes"),
        SecondaryButton("Cancelar", tooltip="Cancelar conversion"),
        GhostButton("Configuracion", tooltip="Abrir configuracion"),
        IconButton("...", tooltip="Mas acciones"),
    ]
    for button in buttons:
        qtbot.addWidget(button)

    assert buttons[0].objectName() == "PrimaryButton"
    assert buttons[1].objectName() == "SecondaryButton"
    assert buttons[2].objectName() == "GhostButton"
    assert buttons[3].objectName() == "IconButton"
    assert all(button.accessibleName() for button in buttons)
    assert all(button.toolTip() for button in buttons)
