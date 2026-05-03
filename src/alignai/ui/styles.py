"""Application-wide Qt stylesheet and theme constants."""

from __future__ import annotations

MATCH_LABEL_COLORS: dict[str, str] = {
    "Strong Match": "#16A34A",
    "Good Match": "#0891B2",
    "Fair Match": "#D97706",
    "Low Match": "#EA580C",
    "Weak Match": "#DC2626",
    "Poor Match": "#991B1B",
    "Zero Match": "#6B7280",
}

APP_STYLESHEET = """
QMainWindow {
    background-color: #F1F5F9;
}

QWidget {
    font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

QPushButton {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #1D4ED8;
}

QPushButton:pressed {
    background-color: #1E40AF;
}

QPushButton:disabled {
    background-color: #94A3B8;
    color: #E2E8F0;
}

QPushButton[secondary="true"] {
    background-color: #E2E8F0;
    color: #334155;
}

QPushButton[secondary="true"]:hover {
    background-color: #CBD5E1;
}

QLineEdit {
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    background-color: white;
    color: #1E293B;
}

QLineEdit:focus {
    border: 2px solid #2563EB;
    padding: 7px 11px;
}

QLabel {
    font-size: 13px;
    color: #334155;
    background-color: transparent;
}

QTableWidget {
    border: 1px solid #E2E8F0;
    border-radius: 4px;
    background-color: white;
    gridline-color: #F1F5F9;
    font-size: 12px;
    selection-background-color: #EFF6FF;
    selection-color: #1E293B;
}

QTableWidget::item {
    padding: 6px;
}

QHeaderView::section {
    background-color: #F8FAFC;
    border: none;
    border-bottom: 2px solid #E2E8F0;
    padding: 8px 6px;
    font-weight: 600;
    font-size: 12px;
    color: #64748B;
}

QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #E2E8F0;
    max-height: 6px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #2563EB;
    border-radius: 4px;
}

QScrollBar:vertical {
    border: none;
    background-color: #F1F5F9;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #CBD5E1;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94A3B8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""


def match_label_style(label_text: str) -> str:
    color = MATCH_LABEL_COLORS.get(label_text, "#6B7280")
    return (
        f"color: {color}; font-weight: 700; font-size: 13px;"
        f" padding: 2px 8px; border: 2px solid {color}; border-radius: 10px;"
    )


def ats_score_color(score: int) -> str:
    if score >= 80:
        return "#16A34A"
    if score >= 60:
        return "#0891B2"
    if score >= 40:
        return "#D97706"
    if score >= 20:
        return "#EA580C"
    return "#DC2626"


def score_badge_style(color: str) -> str:
    return (
        f"background-color: {color}; color: white; font-weight: 700;"
        " font-size: 15px; padding: 6px 14px; border-radius: 12px;"
    )
