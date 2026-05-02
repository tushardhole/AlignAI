"""Tests for CreateAlignment use case."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.fakes.fake_agent_runner import FakeAgentRunner
from tests.fakes.recording_pdf_renderer import RecordingPdfRenderer

from alignai.application.create_alignment import CreateAlignment
from alignai.domain.models import (
    AlignmentInputs,
    CoverLetter,
    JobPosting,
    Resume,
)
from alignai.infra.sqlite_alignment_repository import SqliteAlignmentRepository
from alignai.infra.text_cleanup import clean


@pytest.mark.asyncio
async def test_create_alignment_persists_row_and_pdfs_execute(tmp_path: Path) -> None:
    runner = FakeAgentRunner()
    repo = SqliteAlignmentRepository(tmp_path / "db.sqlite")
    renderer = RecordingPdfRenderer()
    uc = CreateAlignment(
        runner,
        repo,
        renderer,
        tmp_path,
        sanitize_text=clean,
    )
    jp = JobPosting(
        url="https://example.com/job/1",
        title="Engineer",
        description="Build systems.",
        source="url",
    )
    inputs = AlignmentInputs(
        resume=Resume(id="r1", content="resume"),
        cover_letter=CoverLetter(id="c1", content="cover"),
        job_posting=jp,
    )
    align = await uc.execute(inputs)
    assert align.ats_score.value == 82
    rows = repo.list()
    assert len(rows) == 1
    assert len(renderer.calls) == 2
