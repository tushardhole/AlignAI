"""Playwright-rendered DOM + trafilatura job description fetcher."""

from __future__ import annotations

import trafilatura
from playwright.async_api import async_playwright

from alignai.domain.models import JobPosting, UnreadableJob

_MIN_EXTRACTED_LEN = 120


class PlaywrightJobFetcher:
    """Uses headless Chromium when static HTML has no extractable text."""

    def __init__(self, min_text_len: int = _MIN_EXTRACTED_LEN) -> None:
        self._min_len = min_text_len

    async def fetch(self, url: str) -> JobPosting | UnreadableJob:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    page = await browser.new_page()
                    await page.goto(url, wait_until="networkidle", timeout=60_000)
                    html = await page.content()
                finally:
                    await browser.close()
        except TimeoutError as exc:
            return UnreadableJob(url=url, reason=f"playwright:timeout:{exc}")
        except (OSError, RuntimeError) as exc:
            return UnreadableJob(url=url, reason=f"playwright:{exc}")

        downloaded = trafilatura.extract(
            html,
            url=url,
            include_comments=False,
            include_tables=True,
        )
        if not downloaded or len(downloaded.strip()) < self._min_len:
            return UnreadableJob(url=url, reason="playwright:insufficient_text")
        meta = trafilatura.metadata.extract_metadata(html)
        doc_title = meta.title if meta and meta.title else "Job posting"
        return JobPosting(
            url=url,
            title=doc_title,
            description=downloaded.strip(),
            source="url",
        )
