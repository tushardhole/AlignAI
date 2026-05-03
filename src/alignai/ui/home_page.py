"""Home screen: alignment history table."""

from __future__ import annotations

from pathlib import Path

from collections.abc import Callable

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from alignai.application.list_alignments import ListAlignments
from alignai.domain.models import AlignmentId
from alignai.ui.styles import MATCH_LABEL_COLORS

_LINK_COLOR = QColor("#2563EB")


class HomePage(QWidget):
    """Past alignments table and navigation buttons."""

    def __init__(
        self,
        list_alignments: ListAlignments,
        on_delete: Callable[[AlignmentId], None] | None = None,
    ) -> None:
        super().__init__()
        self._list_uc = list_alignments
        self._on_delete_callback = on_delete
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

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            ["Job", "Job link", "Resume PDF", "Cover PDF", "Match", "ATS", "Label", ""]
        )
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnWidth(7, 80)
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
            self.table.setRowHeight(row, 36)
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
            btn_delete = QPushButton("Delete")
            btn_delete.setProperty("secondary", True)
            btn_delete.setMaximumSize(70, 28)
            btn_delete.clicked.connect(
                lambda checked, aid=align.id: self._on_delete_clicked(aid)
            )
            self.table.setCellWidget(row, 7, btn_delete)

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

    def _on_delete_clicked(self, alignment_id: AlignmentId) -> None:
        reply = QMessageBox.warning(
            self,
            "Delete Alignment",
            "Are you sure you want to delete this alignment?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if self._on_delete_callback:
            self._on_delete_callback(alignment_id)
            self.refresh_table()
