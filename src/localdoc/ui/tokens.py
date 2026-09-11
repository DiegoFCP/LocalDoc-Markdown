from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ThemeMode(StrEnum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


@dataclass(frozen=True)
class ColorTokens:
    background: str
    surface: str
    surface_alt: str
    surface_accent: str
    text_primary: str
    text_secondary: str
    text_muted: str
    border: str
    border_strong: str
    accent: str
    accent_primary: str
    accent_hover: str
    accent_soft: str
    success: str
    success_soft: str
    warning: str
    warning_soft: str
    danger: str
    danger_soft: str
    info: str
    info_soft: str
    focus: str


@dataclass(frozen=True)
class SpacingTokens:
    space_1: int = 4
    space_2: int = 8
    space_3: int = 12
    space_4: int = 16
    space_5: int = 20
    space_6: int = 24
    space_8: int = 32
    space_10: int = 40
    space_12: int = 48


@dataclass(frozen=True)
class RadiusTokens:
    radius_sm: int = 6
    radius_md: int = 10
    radius_lg: int = 14
    radius_xl: int = 18


@dataclass(frozen=True)
class TypographyTokens:
    brand_family: str = '"Plus Jakarta Sans", "Segoe UI Variable", "Segoe UI", Arial, sans-serif'
    interface_family: str = '"Segoe UI Variable", "Segoe UI", Arial, sans-serif'
    mono_family: str = '"JetBrains Mono", Consolas, monospace'
    display_size: int = 32
    heading_1_size: int = 22
    heading_2_size: int = 18
    card_title_size: int = 16
    body_size: int = 14
    small_size: int = 13
    caption_size: int = 12


@dataclass(frozen=True)
class DesignTokens:
    colors: ColorTokens
    spacing: SpacingTokens = SpacingTokens()
    radius: RadiusTokens = RadiusTokens()
    typography: TypographyTokens = TypographyTokens()


LIGHT_COLORS = ColorTokens(
    background="#FFFCF7",
    surface="#FFFFFF",
    surface_alt="#FFF7F1",
    surface_accent="#FFF1E9",
    text_primary="#101423",
    text_secondary="#5F6675",
    text_muted="#818794",
    border="#E8DFD8",
    border_strong="#DCCFC6",
    accent="#E85D43",
    accent_primary="#D94F38",
    accent_hover="#BF422D",
    accent_soft="#FFF0E8",
    success="#198E63",
    success_soft="#E5F6EC",
    warning="#F47C2B",
    warning_soft="#FFF3E6",
    danger="#D94F38",
    danger_soft="#FFF0E8",
    info="#E85D43",
    info_soft="#FFF0E8",
    focus="#E85D43",
)

DARK_COLORS = ColorTokens(
    background="#17130F",
    surface="#211B17",
    surface_alt="#2B231D",
    surface_accent="#33231D",
    text_primary="#FFF7F0",
    text_secondary="#D8C9BE",
    text_muted="#AA9A90",
    border="#40342C",
    border_strong="#5A493E",
    accent="#FF745C",
    accent_primary="#FF745C",
    accent_hover="#FF8A75",
    accent_soft="#40241E",
    success="#35C995",
    success_soft="#183A2E",
    warning="#FF9D4D",
    warning_soft="#3F2B17",
    danger="#FF745C",
    danger_soft="#42241F",
    info="#FF745C",
    info_soft="#40241E",
    focus="#FF745C",
)

LIGHT_TOKENS = DesignTokens(colors=LIGHT_COLORS)
DARK_TOKENS = DesignTokens(colors=DARK_COLORS)
