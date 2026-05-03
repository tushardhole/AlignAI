"""Alignment result summary with score badges and download buttons."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from alignai.ui.styles import (
    ats_score_color,
    match_label_style,
    score_badge_style,
)


class ResultPage(QWidget):
    """Shows scores, match label, and PDF open buttons after alignment."""

    def __init__(self) -> None:
        super().__init__()
        self._resume_path: Path | None = None
        self._cover_path: Path | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(20)

        self._title = QLabel("Alignment Complete")
        self._title.setStyleSheet("font-size: 22px; font-weight: bold;")
        root.addWidget(self._title)

        badges = QHBoxLayout()
        badges.setSpacing(12)
        self._ats_badge = QLabel()
        self._ats_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._match_badge = QLabel()
        self._match_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_badge = QLabel()
        self._label_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badges.addWidget(self._ats_badge)
        badges.addWidget(self._match_badge)
        badges.addWidget(self._label_badge)
        badges.addStretch()
        root.addLayout(badges)

        files = QHBoxLayout()
        files.setSpacing(12)
        self._btn_resume = QPushButton("Open Resume PDF")
        self._btn_cover = QPushButton("Open Cover Letter PDF")
        self._btn_resume.clicked.connect(self._open_resume)
        self._btn_cover.clicked.connect(self._open_cover)
        files.addWidget(self._btn_resume)
        files.addWidget(self._btn_cover)
        files.addStretch()
        root.addLayout(files)

        root.addStretch()
        self.btn_home = QPushButton("Back to home")
        self.btn_home.setProperty("secondary", True)
        root.addWidget(self.btn_home)

    def show_result(
        self,
        ats_score: int,
        match_score: int,
        match_label: str,
        resume_path: Path | None,
        cover_path: Path | None,
    ) -> None:
        ats_color = ats_score_color(ats_score)
        self._ats_badge.setText(f"ATS  {ats_score}/100")
        self._ats_badge.setStyleSheet(score_badge_style(ats_color))
        match_color = ats_score_color(match_score * 20)
        self._match_badge.setText(f"Match  {match_score}/5")
        self._match_badge.setStyleSheet(score_badge_style(match_color))
        self._label_badge.setText(match_label)
        self._label_badge.setStyleSheet(match_label_style(match_label))
        self._resume_path = resume_path
        self._cover_path = cover_path

    def _open_resume(self) -> None:
        self._open_file(self._resume_path)

    def _open_cover(self) -> None:
        self._open_file(self._cover_path)

    @staticmethod
    def _open_file(path: Path | None) -> None:
        if path and path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
