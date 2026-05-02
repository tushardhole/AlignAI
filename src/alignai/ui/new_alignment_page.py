"""New alignment form: job URL and base document hints."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)


class NewAlignmentPage(QWidget):
    """Fields for job URL and replacing base resume/cover."""

    def __init__(self) -> None:
        super().__init__()
        layout = QFormLayout(self)
        self.job_url = QLineEdit()
        self.resume_hint = QLabel("")
        self.cover_hint = QLabel("")
        self.btn_resume = QPushButton("Replace base resume…")
        self.btn_cover = QPushButton("Replace base cover letter…")
        self.btn_run = QPushButton("Fetch job & align")
        self.btn_back = QPushButton("Back")
        layout.addRow("Job URL", self.job_url)
        layout.addRow(self.btn_resume, self.resume_hint)
        layout.addRow(self.btn_cover, self.cover_hint)
        layout.addRow(self.btn_run)
        layout.addRow(self.btn_back)
