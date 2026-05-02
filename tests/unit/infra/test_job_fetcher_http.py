"""HTTP job fetcher tested against local HTML fixtures."""

from __future__ import annotations

import pytest

from alignai.domain.models import JobPosting, UnreadableJob
from alignai.infra.job_fetcher_http import HttpTrafilaturaJobFetcher


@pytest.mark.asyncio
async def test_readable_meta_returns_job_posting(job_pages_http_server: str) -> None:
    fetcher = HttpTrafilaturaJobFetcher()
    got = await fetcher.fetch(f"{job_pages_http_server}/readable_meta.html")
    assert isinstance(got, JobPosting)
    assert len(got.description) >= 120
    assert "Engineer" in got.title or "Engineer" in got.description


@pytest.mark.parametrize(
    ("page", "reason_substring"),
    [
        ("image_only.html", "insufficient"),
        ("cf_block.html", "insufficient"),
        ("iframe_xorg.html", "insufficient"),
    ],
)
@pytest.mark.asyncio
async def test_sparse_pages_unreadable(
    job_pages_http_server: str,
    page: str,
    reason_substring: str,
) -> None:
    fetcher = HttpTrafilaturaJobFetcher()
    got = await fetcher.fetch(f"{job_pages_http_server}/{page}")
    assert isinstance(got, UnreadableJob)
    assert reason_substring in got.reason


@pytest.mark.asyncio
async def test_jsonly_page_insufficient_without_js(job_pages_http_server: str) -> None:
    """JS-rendered body is invisible to trafilatura → retry via Playwright in chain."""
    fetcher = HttpTrafilaturaJobFetcher()
    got = await fetcher.fetch(f"{job_pages_http_server}/jsonly_linkedin.html")
    assert isinstance(got, UnreadableJob)
