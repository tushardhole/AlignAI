"""LLM settings form."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class SettingsPage(QWidget):
    """Persisted LLM base URL and model name."""

    def __init__(self) -> None:
        super().__init__()
        layout = QFormLayout(self)
        self.base_url = QLineEdit()
        self.model_name = QLineEdit()
        layout.addRow("LLM base URL", self.base_url)
        layout.addRow("Model name", self.model_name)
        self.btn_save = QPushButton("Save")
        self.btn_back = QPushButton("Back")
        layout.addRow(self.btn_save)
        layout.addRow(self.btn_back)
