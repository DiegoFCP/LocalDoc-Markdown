from __future__ import annotations

from PySide6.QtWidgets import QApplication

from localdoc.ui.assets import branding_path, branding_pixmap
from localdoc.ui.components import GhostButton, IconButton, PrimaryButton, SecondaryButton
from localdoc.ui.icons import file_type_icon, icon, status_icon
from localdoc.ui.theme import ThemeManager, build_stylesheet
from localdoc.ui.tokens import DARK_TOKENS, LIGHT_TOKENS, ThemeMode


def test_light_theme_stylesheet_uses_accessible_primary_color() -> None:
    stylesheet = build_stylesheet(LIGHT_TOKENS)

    assert "#FFFCF8" in stylesheet
    assert "#D96846" in stylesheet
    assert "#FFF0E8" in stylesheet
    assert "QPushButton:focus" in stylesheet
    assert "QPushButton#PrimaryButton" in stylesheet


def test_dark_theme_stylesheet_uses_dark_palette() -> None:
    stylesheet = build_stylesheet(DARK_TOKENS)

    assert "#17130F" in stylesheet
    assert "#FFF7F0" in stylesheet
    assert "#FF745C" in stylesheet


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
        SecondaryButton("Cancelar", tooltip="Cancelar conversión"),
        GhostButton("Configuración", tooltip="Abrir configuración"),
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


def test_functional_icons_are_available(qtbot) -> None:
    assert not icon("upload", "coral").isNull()
    assert not file_type_icon("PDF").isNull()
    assert not status_icon("completed").isNull()


def test_branding_assets_are_available(qtbot) -> None:
    expected_assets = [
        "localdoc-app-icon.png",
        "localdoc-upload-illustration.png",
        "localdoc-conversion-complete.png",
        "localdoc.ico",
    ]

    for filename in expected_assets:
        assert branding_path(filename).exists()

    assert not branding_pixmap("localdoc-app-icon.png", 32).isNull()
    assert not branding_pixmap("localdoc-upload-illustration.png", 64).isNull()
    assert not branding_pixmap("localdoc-conversion-complete.png", 64).isNull()


def test_button_components_accept_functional_icons(qtbot) -> None:
    button = PrimaryButton(
        "Convertir",
        tooltip="Convertir archivos pendientes",
        icon_name="upload",
        icon_color="coral",
    )
    qtbot.addWidget(button)

    assert not button.icon().isNull()
