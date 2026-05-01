"""Tests for domain port Protocols (module import + value objects used by Protocols)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from alignai.domain import ports
from alignai.domain.models import JobPosting, ParsedResume, Resume, ResumeSection, UnreadableJob

if TYPE_CHECKING:
    from pathlib import Path


class TestLlmMessage:
    def test_fields(self) -> None:
        msg = ports.LlmMessage(role="user", content="hello")
        assert msg.role == "user"
        assert msg.content == "hello"

    def test_frozen(self) -> None:
        msg = ports.LlmMessage(role="system", content="ping")
        with pytest.raises((AttributeError, TypeError)):
            msg.role = "user"  # type: ignore[misc]


class TestRuntimeCheckableProtocols:
    """Import-time loads port definitions; runtime checks accept compliant stubs."""

    class _DummyJobFetcher:
        async def fetch(self, url: str) -> JobPosting | UnreadableJob:
            raise NotImplementedError

    def test_job_fetcher_protocol(self) -> None:
        assert isinstance(self._DummyJobFetcher(), ports.JobFetcher)

    def test_resume_parser_protocol(self) -> None:
        dummy_resume = Resume(id="x", content="c")
        parsed = ParsedResume(
            resume_id=dummy_resume.id,
            sections=(ResumeSection(heading="Summary", content="text"),),
        )

        class Impl:
            async def parse(self, resume: Resume) -> ParsedResume:
                assert resume.id == dummy_resume.id
                return parsed

        assert isinstance(Impl(), ports.ResumeParser)

    def test_pdf_renderer_protocol(self) -> None:
        class R:
            async def render(self, html: str, output_path: Path) -> Path:
                raise NotImplementedError

        assert isinstance(R(), ports.PdfRenderer)
