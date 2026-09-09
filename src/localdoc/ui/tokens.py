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
    background="#FFFCF8",
    surface="#FFFFFF",
    surface_alt="#FFF7F2",
    surface_accent="#FFF0E8",
    text_primary="#24211D",
    text_secondary="#665E57",
    text_muted="#82776D",
    border="#E8DED6",
    border_strong="#D6C8BE",
    accent="#D96846",
    accent_primary="#B65437",
    accent_hover="#A54830",
    accent_soft="#FFF0E8",
    success="#2F7D5B",
    success_soft="#EAF6EF",
    warning="#A86511",
    warning_soft="#FFF5E5",
    danger="#B94A42",
    danger_soft="#FDEEEE",
    info="#446A8C",
    info_soft="#EEF5FA",
    focus="#1D4ED8",
)

DARK_COLORS = ColorTokens(
    background="#171513",
    surface="#211E1B",
    surface_alt="#29241F",
    surface_accent="#33241E",
    text_primary="#F4EEE9",
    text_secondary="#C6BDB5",
    text_muted="#998F87",
    border="#3B342E",
    border_strong="#51463D",
    accent="#E07856",
    accent_primary="#E07856",
    accent_hover="#EE8C6E",
    accent_soft="#33241E",
    success="#65B68A",
    success_soft="#1F3328",
    warning="#D99A43",
    warning_soft="#3A2A18",
    danger="#D96A62",
    danger_soft="#3B211F",
    info="#79A6CC",
    info_soft="#1E2B35",
    focus="#9CC3FF",
)

LIGHT_TOKENS = DesignTokens(colors=LIGHT_COLORS)
DARK_TOKENS = DesignTokens(colors=DARK_COLORS)
