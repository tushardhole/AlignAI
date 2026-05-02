"""Telegram chat orchestration for link capture, /align, and paste fallback."""

from __future__ import annotations

import re
from dataclasses import dataclass

from alignai.application.create_alignment import CreateAlignment
from alignai.application.telegram_outcome import TelegramOutcome
from alignai.domain.models import (
    AlignmentInputs,
    JobPosting,
    UnreadableJob,
)
from alignai.domain.ports import DocumentRepository, JobFetcher

_URL_RE = re.compile(r"https?://\S+")


@dataclass
class _ChatState:
    pending_job_url: str | None = None
    awaiting_paste: bool = False


class HandleTelegramMessage:
    """Stateful handler keyed by Telegram chat id."""

    def __init__(
        self,
        job_fetcher: JobFetcher,
        documents: DocumentRepository,
        create_alignment: CreateAlignment,
    ) -> None:
        self._job_fetcher = job_fetcher
        self._documents = documents
        self._create_alignment = create_alignment
        self._states: dict[int, _ChatState] = {}

    async def handle_text(
        self,
        chat_id: int,
        text: str,
        *,
        offline_backlog: bool = False,
    ) -> TelegramOutcome:
        raw = text.strip()
        st = self._states.setdefault(chat_id, _ChatState())
        prefix = ""
        if offline_backlog:
            prefix = "AlignAI was offline when you sent this; running it now.\n\n"

        if raw.lower() in {"/help", "help"}:
            return self._apply_prefix(
                prefix,
                TelegramOutcome(
                    messages=(
                        "Send a job posting URL. Then send /align after I acknowledge. "
                        "Configure base resume and cover letter in the desktop app once.",
                    ),
                ),
            )

        if raw.lower().startswith("/align"):
            inner = await self._run_align(chat_id)
            return self._apply_prefix(prefix, inner)

        match = _URL_RE.search(raw)
        if match:
            url = match.group(0).rstrip(").,]")
            st.pending_job_url = url
            st.awaiting_paste = False
            msg = "Please type /align to align your profile for this job description."
            return self._apply_prefix(prefix, TelegramOutcome(messages=(msg,)))

        if st.awaiting_paste and len(raw) > 80:
            jp = JobPosting(
                url=st.pending_job_url or "pasted",
                title="Pasted job description",
                description=raw,
                source="pasted",
            )
            st.awaiting_paste = False
            inner = await self._run_pipeline(chat_id, jp)
            return self._apply_prefix(prefix, inner)

        return self._apply_prefix(
            prefix,
            TelegramOutcome(messages=("Send a job URL, then /align.",)),
        )

    @staticmethod
    def _apply_prefix(prefix: str, inner: TelegramOutcome) -> TelegramOutcome:
        if not prefix:
            return inner
        msgs = list(inner.messages)
        if msgs:
            msgs[0] = prefix + msgs[0]
        else:
            msgs = [prefix.rstrip()]
        return TelegramOutcome(messages=tuple(msgs), alignment=inner.alignment)

    async def _run_align(self, chat_id: int) -> TelegramOutcome:
        st = self._states.setdefault(chat_id, _ChatState())
        if st.awaiting_paste:
            return TelegramOutcome(
                messages=("Paste the full job description as your next message.",),
            )
        if not st.pending_job_url:
            return TelegramOutcome(
                messages=("Send a job link first, then /align.",),
            )
        fetched = await self._job_fetcher.fetch(st.pending_job_url)
        if isinstance(fetched, UnreadableJob):
            st.awaiting_paste = True
            return TelegramOutcome(
                messages=(
                    "I couldn't read that page. Paste the job description as your next message.",
                ),
            )
        return await self._run_pipeline(chat_id, fetched)

    async def _run_pipeline(self, chat_id: int, jp: JobPosting) -> TelegramOutcome:
        resume = self._documents.get_resume()
        cover = self._documents.get_cover_letter()
        if resume is None or cover is None:
            return TelegramOutcome(
                messages=(
                    "Configure your base resume and cover letter "
                    "in the AlignAI desktop app once, then try again.",
                ),
            )
        inputs = AlignmentInputs(resume=resume, cover_letter=cover, job_posting=jp)
        alignment = await self._create_alignment.execute(inputs)
        summary = (
            f"Done.\nATS: {alignment.ats_score.value}/100\n"
            f"Match: {alignment.match_score.value}/5 ({alignment.match_label.value})"
        )
        self._states.pop(chat_id, None)
        return TelegramOutcome(messages=(summary,), alignment=alignment)
