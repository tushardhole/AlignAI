"""Tests for list, set documents, verify credentials, and telegram flow."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from docx import Document as DocxWriter
from tests.fakes.fake_agent_runner import FakeAgentRunner
from tests.fakes.recording_pdf_renderer import RecordingPdfRenderer

from alignai.application.create_alignment import CreateAlignment
from alignai.application.handle_telegram_message import HandleTelegramMessage
from alignai.application.list_alignments import ListAlignments
from alignai.application.set_base_documents import SetBaseDocuments
from alignai.application.verify_credentials import VerifyCredentials
from alignai.domain.models import (
    AlignedCoverLetter,
    AlignedResume,
    Alignment,
    AlignmentId,
    AtsScore,
    CoverLetter,
    JobPosting,
    MatchLabel,
    MatchScore,
    Resume,
)
from alignai.domain.ports import LlmMessage
from alignai.infra.document_repository import FilesystemDocumentRepository
from alignai.infra.json_settings_store import JsonSettingsStore
from alignai.infra.pdf_input_pypdf import PdfDocxTextExtractor
from alignai.infra.sqlite_alignment_repository import SqliteAlignmentRepository
from alignai.infra.text_cleanup import clean


def _write_docx(path: Path, text: str) -> None:
    doc = DocxWriter()
    doc.add_paragraph(text)
    doc.save(str(path))


class _StubTelegramVerifier:
    async def verify_bot_token(self, token: str) -> bool:
        return token == "good-token"


class _OkLlm:
    async def complete(
        self,
        messages: list[LlmMessage],
        *,
        max_tokens: int = 256,
    ) -> str:
        del messages, max_tokens
        return "ok"


class _BadLlm:
    async def complete(
        self,
        messages: list[LlmMessage],
        *,
        max_tokens: int = 256,
    ) -> str:
        del messages, max_tokens
        raise ValueError("bad")


class FakeJobFetcher:
    def __init__(self, result: object) -> None:
        self._result = result

    async def fetch(self, url: str) -> object:
        del url
        return self._result


@pytest.mark.asyncio
async def test_list_alignments_returns_saved_rows_execute(tmp_path: Path) -> None:
    repo = SqliteAlignmentRepository(tmp_path / "a.sqlite")
    jp = JobPosting(url="u", title="t", description="d")
    row = Alignment(
        id=AlignmentId("id1"),
        job_posting=jp,
        aligned_resume=AlignedResume(content="r"),
        aligned_cover_letter=AlignedCoverLetter(content="c"),
        ats_score=AtsScore(80),
        match_score=MatchScore(4),
        match_label=MatchLabel.GOOD_MATCH,
        created_at=datetime.now(UTC),
    )
    repo.save(row)
    uc = ListAlignments(repo)
    assert len(uc.execute()) == 1


def test_set_base_documents_copies_files_save_resume(tmp_path: Path) -> None:
    settings = JsonSettingsStore(tmp_path / "s.json")
    ext = PdfDocxTextExtractor()
    docs = FilesystemDocumentRepository(tmp_path / "data", settings, ext)
    resume_src = tmp_path / "in.docx"
    _write_docx(resume_src, "Experience at Acme")
    uc = SetBaseDocuments(docs)
    uc.save_resume(resume_src)
    loaded = docs.get_resume()
    assert loaded is not None
    assert loaded.file_path is not None
    assert loaded.file_path.exists()
    assert "Acme" in loaded.content


def test_set_base_documents_stores_cover_save_cover_letter(tmp_path: Path) -> None:
    settings = JsonSettingsStore(tmp_path / "s2.json")
    ext = PdfDocxTextExtractor()
    docs = FilesystemDocumentRepository(tmp_path / "data2", settings, ext)
    cover_src = tmp_path / "cover_in.docx"
    _write_docx(cover_src, "Dear hiring manager")
    uc = SetBaseDocuments(docs)
    uc.save_cover_letter(cover_src)
    loaded = docs.get_cover_letter()
    assert loaded is not None
    assert loaded.file_path is not None
    assert loaded.file_path.exists()
    assert "hiring" in loaded.content


@pytest.mark.asyncio
async def test_verify_credentials_llm_ok_verify_llm() -> None:
    uc = VerifyCredentials(_OkLlm(), _StubTelegramVerifier())
    assert await uc.verify_llm() is True


@pytest.mark.asyncio
async def test_verify_credentials_llm_fail_verify_llm() -> None:
    uc = VerifyCredentials(_BadLlm(), _StubTelegramVerifier())
    assert await uc.verify_llm() is False


@pytest.mark.asyncio
async def test_verify_telegram_verify_telegram() -> None:
    uc = VerifyCredentials(_OkLlm(), _StubTelegramVerifier())
    assert await uc.verify_telegram("good-token") is True
    assert await uc.verify_telegram("bad") is False


@pytest.mark.asyncio
async def test_telegram_flow_url_and_align_handle_text(tmp_path: Path) -> None:
    settings = JsonSettingsStore(tmp_path / "s.json")
    ext = PdfDocxTextExtractor()
    docs = FilesystemDocumentRepository(tmp_path / "data", settings, ext)
    resume_file = tmp_path / "r.docx"
    cover_file = tmp_path / "c.docx"
    _write_docx(resume_file, "Resume body for testing.")
    _write_docx(cover_file, "Cover letter body.")
    docs.save_resume(Resume(id="r", content="", file_path=resume_file))
    docs.save_cover_letter(CoverLetter(id="c", content="", file_path=cover_file))

    jp = JobPosting(url="https://jobs.example.com/1", title="Role", description="Do things")
    repo = SqliteAlignmentRepository(tmp_path / "db.sqlite")
    create_uc = CreateAlignment(
        FakeAgentRunner(),
        repo,
        RecordingPdfRenderer(),
        tmp_path,
        sanitize_text=clean,
    )
    handler = HandleTelegramMessage(FakeJobFetcher(jp), docs, create_uc)

    out = await handler.handle_text(1, "https://jobs.example.com/1")
    assert "Please type /align" in out.messages[0]

    out2 = await handler.handle_text(1, "/align")
    assert out2.alignment is not None
    assert out2.alignment.ats_score.value == 82
