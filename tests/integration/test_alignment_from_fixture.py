"""Pipeline integration: local job fixture → fetch → align (fake LLM)."""

from __future__ import annotations

from pathlib import Path

import pytest

from alignai.application.create_alignment import CreateAlignment
from alignai.domain.models import AlignmentInputs, CoverLetter, JobPosting, Resume
from alignai.infra.job_fetcher_http import HttpTrafilaturaJobFetcher
from alignai.infra.sqlite_alignment_repository import SqliteAlignmentRepository
from alignai.infra.text_cleanup import clean
from tests.fakes.fake_agent_runner import FakeAgentRunner
from tests.fakes.recording_pdf_renderer import RecordingPdfRenderer


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fixture_job_page_to_sqlite_and_pdfs(
    tmp_path: Path,
    job_pages_http_server: str,
) -> None:
    fetcher = HttpTrafilaturaJobFetcher()
    url = f"{job_pages_http_server}/readable_meta.html"
    fetched = await fetcher.fetch(url)
    assert isinstance(fetched, JobPosting)
    job = fetched
    assert job.source == "url"

    runner = FakeAgentRunner()
    repo = SqliteAlignmentRepository(tmp_path / "align.sqlite")
    renderer = RecordingPdfRenderer()
    uc = CreateAlignment(
        runner,
        repo,
        renderer,
        tmp_path,
        sanitize_text=clean,
    )
    inputs = AlignmentInputs(
        resume=Resume(id="r1", content="resume body"),
        cover_letter=CoverLetter(id="c1", content="cover body"),
        job_posting=job,
    )
    align = await uc.execute(inputs)
    assert align.ats_score.value == 82
    rows = repo.list()
    assert len(rows) == 1
    assert len(renderer.calls) == 2
