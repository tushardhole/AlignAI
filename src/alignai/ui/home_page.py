"""Home screen: alignment history table."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from alignai.application.list_alignments import ListAlignments
from alignai.ui.styles import MATCH_LABEL_COLORS

_LINK_COLOR = QColor("#2563EB")


class HomePage(QWidget):
    """Past alignments table and navigation buttons."""

    def __init__(
        self,
        list_alignments: ListAlignments,
    ) -> None:
        super().__init__()
        self._list_uc = list_alignments
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        top = QHBoxLayout()
        title = QLabel("Past Alignments")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.btn_new = QPushButton("+ New Alignment")
        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setProperty("secondary", True)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.btn_settings)
        top.addWidget(self.btn_new)
        layout.addLayout(top)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Job", "Job link", "Resume PDF", "Cover PDF", "Match", "ATS", "Label"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self.table)
        self.refresh_table()

    def refresh_table(self) -> None:
        rows = self._list_uc.execute()
        self.table.setRowCount(0)
        for align in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            title = align.job_posting.title
            disp = title if len(title) <= 40 else title[:37] + "…"
            link = align.job_posting.url

            resume_path = align.aligned_resume.file_path
            cover_path = align.aligned_cover_letter.file_path
            resume_name = Path(resume_path).name if resume_path else ""
            cv_name = Path(cover_path).name if cover_path else ""

            self.table.setItem(row, 0, QTableWidgetItem(disp))
            self.table.setItem(row, 1, QTableWidgetItem(link[:100]))
            self.table.setItem(row, 2, self._link_item(resume_name, resume_path))
            self.table.setItem(row, 3, self._link_item(cv_name, cover_path))
            self.table.setItem(row, 4, QTableWidgetItem(str(align.match_score.value)))
            self.table.setItem(row, 5, QTableWidgetItem(str(align.ats_score.value)))
            label_item = QTableWidgetItem(str(align.match_label.value))
            label_color = MATCH_LABEL_COLORS.get(align.match_label.value, "#6B7280")
            label_item.setForeground(QColor(label_color))
            bold = QFont()
            bold.setBold(True)
            label_item.setFont(bold)
            self.table.setItem(row, 6, label_item)

    @staticmethod
    def _link_item(text: str, path: Path | None) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        if path:
            item.setForeground(_LINK_COLOR)
            font = item.font()
            font.setUnderline(True)
            item.setFont(font)
            item.setData(Qt.ItemDataRole.UserRole, str(path))
        return item

    def _on_cell_clicked(self, row: int, col: int) -> None:
        if col not in (2, 3):
            return
        item = self.table.item(row, col)
        if item is None:
            return
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if path_str:
            path = Path(path_str)
            if path.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
