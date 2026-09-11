from __future__ import annotations

from functools import lru_cache

from PySide6.QtCore import QByteArray, QSize
from PySide6.QtGui import QIcon, QPixmap

ICON_COLORS = {
    "blue": "#D96846",
    "purple": "#D96846",
    "coral": "#D96846",
    "mint": "#2F7D5B",
    "green": "#2F7D5B",
    "orange": "#D96846",
    "red": "#B84A33",
    "slate": "#686159",
    "muted": "#817870",
}

FILE_TYPE_COLORS = {
    "PDF": "coral",
    "DOCX": "coral",
    "DOC": "coral",
    "XLSX": "mint",
    "XLS": "mint",
    "PPTX": "orange",
    "PPT": "orange",
    "IMG": "coral",
    "PNG": "coral",
    "JPG": "coral",
    "JPEG": "coral",
    "TXT": "slate",
    "HTML": "orange",
    "HTM": "orange",
}


def icon(name: str, color: str = "slate", size: int = 18) -> QIcon:
    pixmap = _pixmap(name, _resolve_color(color), size)
    return QIcon(pixmap)


def file_type_icon(label: str, size: int = 26) -> QIcon:
    color = FILE_TYPE_COLORS.get(label.upper(), "slate")
    pixmap = _pixmap("file", _resolve_color(color), size, label[:4].upper())
    return QIcon(pixmap)


def status_icon(status: str, size: int = 18) -> QIcon:
    color = {
        "queued": "muted",
        "processing": "coral",
        "completed": "green",
        "failed": "red",
        "cancelled": "muted",
    }.get(status, "slate")
    glyph = {
        "queued": "clock",
        "processing": "spinner",
        "completed": "check",
        "failed": "error",
        "cancelled": "minus",
    }.get(status, "circle")
    return icon(glyph, color, size)


@lru_cache(maxsize=128)
def _pixmap(name: str, color: str, size: int, label: str = "") -> QPixmap:
    svg = _svg(name, color, label).encode("utf-8")
    pixmap = QPixmap(QSize(size, size))
    pixmap.loadFromData(QByteArray(svg), "SVG")
    return pixmap


def _resolve_color(color: str) -> str:
    return ICON_COLORS.get(color, color)


def _svg(name: str, color: str, label: str = "") -> str:
    if name == "file":
        return f"""<svg xmlns="http://www.w3.org/2000/svg"
 width="32" height="32" viewBox="0 0 32 32">
<rect x="5" y="3" width="22" height="26" rx="6"
 fill="{color}" fill-opacity=".14"/>
<path d="M11 9h7l4 4v10H11z" fill="none" stroke="{color}" stroke-width="2"
 stroke-linejoin="round"/>
<path d="M18 9v5h5" fill="none" stroke="{color}" stroke-width="2"
 stroke-linejoin="round"/>
<text x="16" y="23" text-anchor="middle" font-family="Segoe UI, Arial"
 font-size="7" font-weight="700" fill="{color}">{label}</text>
</svg>"""
    paths = {
        "upload": (
            '<path d="M12 18V6m0 0L7 11m5-5 5 5"/>'
            '<path d="M5 18v2h14v-2"/>'
        ),
        "add": '<path d="M12 5v14M5 12h14"/>',
        "history": (
            '<path d="M4 12a8 8 0 1 0 2.3-5.7L4 8.6"/>'
            '<path d="M4 4v5h5"/><path d="M12 8v5l3 2"/>'
        ),
        "settings": (
            '<circle cx="12" cy="12" r="3"/>'
            '<path d="M19 13.5v-3l-2.1-.5-.8-1.9 1.1-1.8-2.1-2.1'
            '-1.8 1.1-1.9-.8L10.9 1h-3l-.5 2.1-1.9.8-1.8-1.1'
            '-2.1 2.1 1.1 1.8-.8 1.9L0 10.5v3l2.1.5.8 1.9'
            '-1.1 1.8 2.1 2.1 1.8-1.1 1.9.8.5 2.1h3l.5-2.1'
            ' 1.9-.8 1.8 1.1 2.1-2.1-1.1-1.8.8-1.9z"'
            ' transform="translate(2 1) scale(.85)"/>'
        ),
        "folder": (
            '<path d="M3 7h7l2 2h9v9a3 3 0 0 1-3 3H6a3 3'
            ' 0 0 1-3-3z"/>'
        ),
        "copy": (
            '<rect x="8" y="8" width="11" height="13" rx="2"/>'
            '<path d="M5 16V5h11"/>'
        ),
        "open": (
            '<path d="M8 6H5a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11'
            ' a2 2 0 0 0 2-2v-3"/>'
            '<path d="M13 3h8v8"/><path d="M11 13 21 3"/>'
        ),
        "more": (
            '<circle cx="5" cy="12" r="1.5"/>'
            '<circle cx="12" cy="12" r="1.5"/>'
            '<circle cx="19" cy="12" r="1.5"/>'
        ),
        "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
        "error": (
            '<circle cx="12" cy="12" r="9"/>'
            '<path d="M12 7v6"/><path d="M12 17h.01"/>'
        ),
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v6l4 2"/>',
        "spinner": '<path d="M21 12a9 9 0 1 1-9-9"/>',
        "shield": (
            '<path d="M12 3 20 6v6c0 5-3.4 8-8 9-4.6-1-8-4-8-9V6z"/>'
            '<path d="m8.5 12 2.3 2.3 4.8-5"/>'
        ),
        "search": (
            '<circle cx="10.5" cy="10.5" r="6.5"/>'
            '<path d="m16 16 5 5"/>'
        ),
        "filter": '<path d="M4 6h16M7 12h10M10 18h4"/>',
        "minus": '<path d="M5 12h14"/>',
        "circle": '<circle cx="12" cy="12" r="8"/>',
    }
    body = paths.get(name, paths["circle"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg"
 width="24" height="24" viewBox="0 0 24 24">
<g fill="none" stroke="{color}" stroke-width="2"
 stroke-linecap="round" stroke-linejoin="round">{body}</g>
</svg>"""
