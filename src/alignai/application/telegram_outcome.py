"""Structured bot replies from HandleTelegramMessage."""

from __future__ import annotations

from dataclasses import dataclass

from alignai.domain.models import Alignment


@dataclass(frozen=True)
class TelegramOutcome:
    """Work for the bot bridge to send (text replies + optional alignment artifacts)."""

    messages: tuple[str, ...]
    alignment: Alignment | None = None
