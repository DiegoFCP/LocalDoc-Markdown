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
    background="#F7F9FF",
    surface="#FFFFFF",
    surface_alt="#F3F6FC",
    surface_accent="#EFF6FF",
    text_primary="#17204A",
    text_secondary="#59627A",
    text_muted="#7D879D",
    border="#DDE5F0",
    border_strong="#C8D4E4",
    accent="#286BF4",
    accent_primary="#286BF4",
    accent_hover="#1758D9",
    accent_soft="#EAF2FF",
    success="#1FA46F",
    success_soft="#E5F8EF",
    warning="#E6A11A",
    warning_soft="#FFF7E5",
    danger="#D94D4D",
    danger_soft="#FFF0ED",
    info="#7047EB",
    info_soft="#F0EBFF",
    focus="#286BF4",
)

DARK_COLORS = ColorTokens(
    background="#10131C",
    surface="#171C28",
    surface_alt="#1D2331",
    surface_accent="#1E2D47",
    text_primary="#EEF2FA",
    text_secondary="#B8C1D3",
    text_muted="#8793A8",
    border="#2A3242",
    border_strong="#3A455A",
    accent="#5A8DFF",
    accent_primary="#5A8DFF",
    accent_hover="#78A4FF",
    accent_soft="#1B2A46",
    success="#39D3A5",
    success_soft="#17382F",
    warning="#F1B84B",
    warning_soft="#3A2D16",
    danger="#FF735F",
    danger_soft="#3B201F",
    info="#8B6CFF",
    info_soft="#261F45",
    focus="#8B6CFF",
)

LIGHT_TOKENS = DesignTokens(colors=LIGHT_COLORS)
DARK_TOKENS = DesignTokens(colors=DARK_COLORS)
