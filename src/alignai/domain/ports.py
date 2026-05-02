"""Domain port interfaces (Protocol definitions).

Every cross-layer dependency is expressed as a Protocol here.
Concrete implementations live in infra/ or agents/; main.py is the
sole place that wires them together. Nothing in domain/ or application/
may import from infra/, agents/, or ui/.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from pathlib import Path

    from alignai.domain.models import (
        Alignment,
        AlignmentId,
        AlignmentInputs,
        AlignmentResult,
        CoverLetter,
        JobPosting,
        ParsedResume,
        Resume,
        UnreadableJob,
    )


@dataclass(frozen=True)
class LlmMessage:
    """A single message in an LLM conversation."""

    role: str
    content: str


@runtime_checkable
class JobFetcher(Protocol):
    """Fetches a job posting from a URL using any available strategy."""

    async def fetch(self, url: str) -> JobPosting | UnreadableJob: ...


@runtime_checkable
class DocumentRepository(Protocol):
    """Stores and retrieves the user's base Resume and CoverLetter documents."""

    def get_resume(self) -> Resume | None: ...

    def save_resume(self, resume: Resume) -> None: ...

    def get_cover_letter(self) -> CoverLetter | None: ...

    def save_cover_letter(self, cover_letter: CoverLetter) -> None: ...


@runtime_checkable
class AlignmentRepository(Protocol):
    """Persists and queries completed Alignment records."""

    def save(self, alignment: Alignment) -> AlignmentId: ...

    def list(self) -> list[Alignment]: ...

    def get(self, alignment_id: AlignmentId) -> Alignment | None: ...


@runtime_checkable
class LlmClient(Protocol):
    """Minimal LLM HTTP client used for credential verification and ad-hoc calls."""

    async def complete(
        self,
        messages: list[LlmMessage],
        *,
        max_tokens: int = 256,
    ) -> str: ...


@runtime_checkable
class PdfRenderer(Protocol):
    """Renders an HTML string to a PDF file via headless Chromium."""

    async def render(self, html: str, output_path: Path) -> Path: ...


@runtime_checkable
class NotificationChannel(Protocol):
    """Sends text messages and document attachments to a recipient."""

    async def send(self, recipient_id: str, text: str) -> None: ...

    async def send_document(
        self,
        recipient_id: str,
        path: Path,
        caption: str = "",
    ) -> None: ...


@runtime_checkable
class SettingsStore(Protocol):
    """Reads and writes non-secret application settings."""

    def get(self, key: str, default: str | None = None) -> str | None: ...

    def set(self, key: str, value: str) -> None: ...


@runtime_checkable
class AgentRunner(Protocol):
    """Runs the multi-agent alignment pipeline and returns structured output."""

    async def run(self, inputs: AlignmentInputs) -> AlignmentResult: ...


@runtime_checkable
class TelegramCredentialsVerifier(Protocol):
    """Checks that a Telegram bot token is accepted by the Bot API."""

    async def verify_bot_token(self, token: str) -> bool: ...


@runtime_checkable
class ResumeParser(Protocol):
    """Structurally parses a resume into ordered sections for chunked alignment."""

    async def parse(self, resume: Resume) -> ParsedResume: ...
