from __future__ import annotations

APP_STYLESHEET = """
QMainWindow, QWidget {
    background: #FFFCF8;
    color: #24211D;
    font-family: "Plus Jakarta Sans", "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QFrame#TopBar {
    background: #FFFCF8;
    border-bottom: 1px solid #E8DED6;
}

QLabel#Brand {
    font-size: 24px;
    font-weight: 700;
}

QLabel#HeroTitle {
    font-size: 28px;
    font-weight: 700;
}

QLabel#Muted {
    color: #766B61;
}

QLabel#Pill {
    background: #FFF0E8;
    border: 1px solid #E8DED6;
    border-radius: 8px;
    padding: 6px 10px;
}

QPushButton {
    border: 1px solid #D6C8BE;
    border-radius: 8px;
    padding: 8px 12px;
    background: #FFFFFF;
}

QPushButton:hover {
    background: #FFF0E8;
}

QPushButton#PrimaryButton {
    background: #D96846;
    border-color: #D96846;
    color: #FFFFFF;
    font-weight: 700;
}

QPushButton#PrimaryButton:hover {
    background: #C65B3B;
}

QFrame#DropZone {
    background: #FFF0E8;
    border: 2px dashed #D96846;
    border-radius: 8px;
}

QTableWidget {
    background: #FFFFFF;
    border: 1px solid #E8DED6;
    border-radius: 8px;
    gridline-color: #EEE5DE;
    selection-background-color: #FFF0E8;
    selection-color: #24211D;
}

QHeaderView::section {
    background: #FFFCF8;
    border: 0;
    border-bottom: 1px solid #E8DED6;
    padding: 8px;
    font-weight: 700;
}

QTextEdit {
    background: #FFFFFF;
    border: 1px solid #E8DED6;
    border-radius: 8px;
    font-family: "JetBrains Mono", Consolas, monospace;
}

QLineEdit, QSpinBox {
    background: #FFFFFF;
    border: 1px solid #D6C8BE;
    border-radius: 8px;
    padding: 7px;
}
"""

