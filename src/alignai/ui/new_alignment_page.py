"""New alignment form: job URL and base document hints."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class NewAlignmentPage(QWidget):
    """Fields for job URL and replacing base resume/cover."""

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)

        title = QLabel("New Alignment")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 8px;")
        root.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        self.job_url = QLineEdit()
        self.job_url.setPlaceholderText("Paste the job listing URL")
        self.resume_hint = QLabel("")
        self.cover_hint = QLabel("")
        self.btn_resume = QPushButton("Replace base resume…")
        self.btn_resume.setProperty("secondary", True)
        self.btn_cover = QPushButton("Replace base cover letter…")
        self.btn_cover.setProperty("secondary", True)
        form.addRow("Job URL", self.job_url)
        form.addRow(self.btn_resume, self.resume_hint)
        form.addRow(self.btn_cover, self.cover_hint)
        root.addLayout(form)

        root.addSpacing(12)
        self.btn_run = QPushButton("Align Match")
        self.btn_run.setStyleSheet("font-size: 15px; padding: 10px 28px; min-height: 24px;")
        root.addWidget(self.btn_run)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)
        root.addWidget(self._progress)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #64748B; font-size: 12px;")
        self._status.setVisible(False)
        root.addWidget(self._status)

        root.addSpacing(8)
        self.btn_back = QPushButton("Back")
        self.btn_back.setProperty("secondary", True)
        root.addWidget(self.btn_back)
        root.addStretch()

    def set_loading(self, loading: bool) -> None:
        self._progress.setVisible(loading)
        self._status.setVisible(loading)
        if loading:
            self._status.setText("Aligning - this may take a minute…")
        self.btn_run.setEnabled(not loading)
        self.btn_resume.setEnabled(not loading)
        self.btn_cover.setEnabled(not loading)
        self.btn_back.setEnabled(not loading)
        self.job_url.setEnabled(not loading)
