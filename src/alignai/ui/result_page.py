"""Alignment result summary."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class ResultPage(QWidget):
    """Shows scores and paths after alignment."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.summary = QLabel("")
        layout.addWidget(self.summary)
        self.btn_home = QPushButton("Back to home")
        layout.addWidget(self.btn_home)
