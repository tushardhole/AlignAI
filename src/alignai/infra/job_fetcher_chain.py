"""Chain HTTP fetch then Playwright fallback."""

from __future__ import annotations

from alignai.domain.models import JobPosting, UnreadableJob
from alignai.infra.job_fetcher_http import HttpTrafilaturaJobFetcher
from alignai.infra.job_fetcher_playwright import PlaywrightJobFetcher


class ChainedJobFetcher:
    """Tries lightweight HTTP extraction before launching a browser."""

    def __init__(
        self,
        primary: HttpTrafilaturaJobFetcher | None = None,
        fallback: PlaywrightJobFetcher | None = None,
    ) -> None:
        self._primary = primary or HttpTrafilaturaJobFetcher()
        self._fallback = fallback or PlaywrightJobFetcher()

    async def fetch(self, url: str) -> JobPosting | UnreadableJob:
        first = await self._primary.fetch(url)
        if isinstance(first, JobPosting):
            return first
        second = await self._fallback.fetch(url)
        if isinstance(second, JobPosting):
            return second
        return UnreadableJob(
            url=url,
            reason=f"{first.reason};{second.reason}",
        )
