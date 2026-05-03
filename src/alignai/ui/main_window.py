"""Qt main window: home table, new alignment flow, settings."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
)

from alignai.application.create_alignment import CreateAlignment
from alignai.application.list_alignments import ListAlignments
from alignai.application.set_base_documents import SetBaseDocuments
from alignai.domain.models import (
    Alignment,
    AlignmentInputs,
    CoverLetter,
    JobPosting,
    Resume,
    UnreadableJob,
)
from alignai.domain.ports import DocumentRepository, JobFetcher
from alignai.ui.async_runner_thread import AsyncRunnerThread
from alignai.ui.home_page import HomePage
from alignai.ui.new_alignment_page import NewAlignmentPage
from alignai.ui.result_page import ResultPage
from alignai.ui.settings_page import SettingsPage


@dataclass
class MainDeps:
    """Services constructed in main.py."""

    create_alignment: CreateAlignment
    list_alignments: ListAlignments
    set_base_documents: SetBaseDocuments
    documents: DocumentRepository
    job_fetcher: JobFetcher


class MainWindow(QMainWindow):
    """Primary navigation shell."""

    def __init__(
        self,
        deps: MainDeps,
        settings_get: Callable[[str], str | None],
        settings_set: Callable[[str, str], None],
        secrets_get: Callable[[str], str | None],
        secrets_set: Callable[[str, str], None],
        rebuild_llm: Callable[[], CreateAlignment],
    ) -> None:
        super().__init__()
        self._deps = deps
        self._settings_get = settings_get
        self._settings_set = settings_set
        self._secrets_get = secrets_get
        self._secrets_set = secrets_set
        self._rebuild_llm = rebuild_llm
        self.setWindowTitle("AlignAI")
        self.resize(1000, 640)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._home_page = HomePage(deps.list_alignments)
        self._new_page = NewAlignmentPage()
        self._result_page = ResultPage()
        self._settings_page = SettingsPage()

        self._stack.addWidget(self._home_page)
        self._stack.addWidget(self._new_page)
        self._stack.addWidget(self._result_page)
        self._stack.addWidget(self._settings_page)

        self._home_page.btn_new.clicked.connect(self._go_new)
        self._home_page.btn_settings.clicked.connect(self._go_settings)
        self._new_page.btn_resume.clicked.connect(self._pick_resume)
        self._new_page.btn_cover.clicked.connect(self._pick_cover)
        self._new_page.btn_run.clicked.connect(self._start_alignment)
        self._new_page.btn_back.clicked.connect(self._go_home)
        self._result_page.btn_home.clicked.connect(self._go_home)
        self._settings_page.btn_save.clicked.connect(self._save_settings)
        self._settings_page.btn_back.clicked.connect(self._go_home)

        self._settings_page.base_url.setText(self._settings_get("llm_base_url") or "")
        self._settings_page.model_name.setText(self._settings_get("llm_model") or "")

        self._pending_url = ""
        self._pending_resume: Resume | None = None
        self._pending_cover: CoverLetter | None = None

        self._refresh_doc_hints()

    def refresh_table(self) -> None:
        self._home_page.refresh_table()

    def _go_home(self) -> None:
        self._stack.setCurrentWidget(self._home_page)

    def _go_settings(self) -> None:
        self._settings_page.api_key.clear()
        self._stack.setCurrentWidget(self._settings_page)

    def _go_new(self) -> None:
        self._refresh_doc_hints()
        self._stack.setCurrentWidget(self._new_page)

    def _refresh_doc_hints(self) -> None:
        r = self._deps.documents.get_resume()
        c = self._deps.documents.get_cover_letter()
        self._new_page.resume_hint.setText(r.file_path.name if r and r.file_path else "(none)")
        self._new_page.cover_hint.setText(c.file_path.name if c and c.file_path else "(none)")

    def _pick_resume(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Resume", "", "Documents (*.pdf *.docx)")
        if path:
            self._deps.set_base_documents.save_resume(Path(path))
            self._refresh_doc_hints()

    def _pick_cover(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Cover letter",
            "",
            "Documents (*.pdf *.docx)",
        )
        if path:
            self._deps.set_base_documents.save_cover_letter(Path(path))
            self._refresh_doc_hints()

    def _start_alignment(self) -> None:
        url = self._new_page.job_url.text().strip()
        if not url:
            QMessageBox.warning(self, "AlignAI", "Enter a job URL.")
            return
        resume = self._deps.documents.get_resume()
        cover = self._deps.documents.get_cover_letter()
        if resume is None or cover is None:
            QMessageBox.warning(
                self,
                "AlignAI",
                "Select base resume and cover letter first.",
            )
            return

        self._pending_url = url
        self._pending_resume = resume
        self._pending_cover = cover
        self._new_page.set_loading(True)

        async def fetch_only() -> object:
            return await self._deps.job_fetcher.fetch(url)

        self._fetch_thr = AsyncRunnerThread(fetch_only())
        self._fetch_thr.finished_ok.connect(self._after_fetch)
        self._fetch_thr.failed.connect(self._on_async_fail)
        self._fetch_thr.start()

    @Slot(object)
    def _after_fetch(self, got: object) -> None:
        url = self._pending_url
        resume = self._pending_resume
        cover = self._pending_cover
        if resume is None or cover is None:
            self._new_page.set_loading(False)
            return
        if isinstance(got, UnreadableJob):
            self._new_page.set_loading(False)
            text, ok = QInputDialog.getMultiLineText(
                self,
                "Paste job description",
                "We could not read this listing. Paste the full job text:",
            )
            if not ok or len(text.strip()) < 80:
                QMessageBox.warning(self, "AlignAI", "Alignment cancelled.")
                return
            jp = JobPosting(
                url=url,
                title="Pasted job",
                description=text.strip(),
                source="pasted",
            )
            self._new_page.set_loading(True)
            self._run_execute(jp, resume, cover)
            return

        if not isinstance(got, JobPosting):
            self._new_page.set_loading(False)
            QMessageBox.warning(self, "AlignAI", "Unexpected fetch result.")
            return

        self._run_execute(got, resume, cover)

    def _run_execute(self, jp: JobPosting, resume: Resume, cover: CoverLetter) -> None:
        async def align() -> Alignment:
            inputs = AlignmentInputs(resume=resume, cover_letter=cover, job_posting=jp)
            return await self._deps.create_alignment.execute(inputs)

        self._align_thr = AsyncRunnerThread(align())
        self._align_thr.finished_ok.connect(self._show_alignment_result)
        self._align_thr.failed.connect(self._on_async_fail)
        self._align_thr.start()

    @Slot(object)
    def _show_alignment_result(self, align: object) -> None:
        self._new_page.set_loading(False)
        if not isinstance(align, Alignment):
            return
        self._result_page.show_result(
            ats_score=align.ats_score.value,
            match_score=align.match_score.value,
            match_label=align.match_label.value,
            resume_path=align.aligned_resume.file_path,
            cover_path=align.aligned_cover_letter.file_path,
        )
        self.refresh_table()
        self._stack.setCurrentWidget(self._result_page)

    @Slot(str)
    def _on_async_fail(self, msg: str) -> None:
        self._new_page.set_loading(False)
        QMessageBox.critical(self, "AlignAI", msg)

    def _save_settings(self) -> None:
        self._settings_set("llm_base_url", self._settings_page.base_url.text())
        self._settings_set("llm_model", self._settings_page.model_name.text())
        api_key = self._settings_page.api_key.text().strip()
        if api_key:
            self._secrets_set("llm_api_key", api_key)
        self._deps.create_alignment = self._rebuild_llm()
        QMessageBox.information(self, "AlignAI", "Saved — changes take effect immediately.")
