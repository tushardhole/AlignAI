"""LLM settings form."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QWidget):
    """Persisted LLM base URL, model name, and API key."""

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 8px;")
        root.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        self.base_url = QLineEdit()
        self.base_url.setPlaceholderText("https://api.openai.com/v1")
        self.model_name = QLineEdit()
        self.model_name.setPlaceholderText("gpt-4o-mini")
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("Leave blank to keep current key")
        form.addRow("LLM base URL", self.base_url)
        form.addRow("Model name", self.model_name)
        form.addRow("API key", self.api_key)
        root.addLayout(form)

        root.addSpacing(16)
        self.btn_save = QPushButton("Save")
        self.btn_back = QPushButton("Back")
        self.btn_back.setProperty("secondary", True)
        root.addWidget(self.btn_save)
        root.addWidget(self.btn_back)
        root.addStretch()
