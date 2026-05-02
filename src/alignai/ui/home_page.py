"""Home screen: alignment history table."""

from __future__ import annotations

from pathlib import Path

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


class HomePage(QWidget):
    """Past alignments table and navigation buttons."""

    def __init__(
        self,
        list_alignments: ListAlignments,
    ) -> None:
        super().__init__()
        self._list_uc = list_alignments
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        title = QLabel("Past alignments")
        title.setStyleSheet("font-size:18px;font-weight:bold;")
        self.btn_new = QPushButton("+ New Alignment")
        self.btn_settings = QPushButton("Settings")
        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.btn_settings)
        top.addWidget(self.btn_new)
        layout.addLayout(top)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            [
                "Job",
                "Job link",
                "Resume PDF",
                "Cover PDF",
                "Match",
                "ATS",
                "Label",
            ]
        )
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
            resume_name = (
                Path(align.aligned_resume.file_path).name if align.aligned_resume.file_path else ""
            )
            cv_name = (
                Path(align.aligned_cover_letter.file_path).name
                if align.aligned_cover_letter.file_path
                else ""
            )
            self.table.setItem(row, 0, QTableWidgetItem(disp))
            self.table.setItem(row, 1, QTableWidgetItem(link[:100]))
            self.table.setItem(row, 2, QTableWidgetItem(resume_name))
            self.table.setItem(row, 3, QTableWidgetItem(cv_name))
            self.table.setItem(row, 4, QTableWidgetItem(str(align.match_score.value)))
            self.table.setItem(row, 5, QTableWidgetItem(str(align.ats_score.value)))
            self.table.setItem(row, 6, QTableWidgetItem(str(align.match_label.value)))
