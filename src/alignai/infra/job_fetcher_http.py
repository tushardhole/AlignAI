"""HTTP + trafilatura job description fetcher."""

from __future__ import annotations

import httpx
import trafilatura

from alignai.domain.models import JobPosting, UnreadableJob

_MIN_EXTRACTED_LEN = 120


class HttpTrafilaturaJobFetcher:
    """Fetches a URL and extracts main text with trafilatura."""

    def __init__(self, min_text_len: int = _MIN_EXTRACTED_LEN) -> None:
        self._min_len = min_text_len

    async def fetch(self, url: str) -> JobPosting | UnreadableJob:
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=httpx.Timeout(30.0),
                headers={"User-Agent": "AlignAI/1.0 (job fetcher)"},
            ) as client:
                response = await client.get(url)
        except httpx.HTTPError as exc:
            return UnreadableJob(url=url, reason=f"http_error:{exc}")
        if response.status_code >= 400:
            return UnreadableJob(url=url, reason=f"http_status:{response.status_code}")
        body = response.text
        downloaded = trafilatura.extract(
            body,
            url=url,
            include_comments=False,
            include_tables=True,
        )
        if not downloaded or len(downloaded.strip()) < self._min_len:
            return UnreadableJob(url=url, reason="trafilatura:insufficient_text")
        title = trafilatura.metadata.extract_metadata(body) or None
        doc_title = title.title if title and title.title else "Job posting"
        return JobPosting(
            url=url,
            title=doc_title,
            description=downloaded.strip(),
            source="url",
        )
