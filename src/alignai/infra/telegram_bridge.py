"""Bridge PTB long-polling to HandleTelegramMessage."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


class TelegramBotService:
    """Runs python-telegram-bot with async handlers."""

    def __init__(
        self,
        bot_token: str,
        handler: Any,
    ) -> None:
        self._token = bot_token
        self._handler = handler
        self._app: Any = None
        self._poll_started_at: datetime | None = None

    def run_polling_blocking(self) -> None:
        """Block the current thread running Telegram long-poll (use from a worker thread)."""
        self._poll_started_at = datetime.now(UTC)
        app = self.build_application()
        app.run_polling(close_loop=False, stop_signals=None)

    def build_application(self) -> Any:
        app = Application.builder().token(self._token).build()
        app.add_handler(CommandHandler("align", self._on_align))
        app.add_handler(CommandHandler("help", self._on_help))
        app.add_handler(CommandHandler("start", self._on_help))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_text))
        self._app = app
        return app

    async def _on_align(
        self,
        update: Update,
        _context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        await self._dispatch(update, "/align")

    async def _on_help(
        self,
        update: Update,
        _context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        await self._dispatch(update, "/help")

    async def _on_text(
        self,
        update: Update,
        _context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if update.effective_chat is None or update.message is None:
            return
        text = update.message.text or ""
        await self._dispatch(update, text)

    def _is_offline_backlog(self, update: Update) -> bool:
        """True when the message was sent before this polling session started."""
        if self._poll_started_at is None or update.message is None:
            return False
        msg_time = update.message.date
        if msg_time.tzinfo is None:
            msg_time = msg_time.replace(tzinfo=UTC)
        return msg_time < self._poll_started_at

    async def _dispatch(self, update: Update, text: str) -> None:
        if update.effective_chat is None or update.message is None:
            return
        chat_id = update.effective_chat.id
        offline_backlog = self._is_offline_backlog(update)
        outcome = await self._handler.handle_text(
            chat_id,
            text,
            offline_backlog=offline_backlog,
        )
        for msg in outcome.messages:
            await update.message.reply_text(msg)
        if outcome.alignment is None:
            return
        align = outcome.alignment
        r_path = align.aligned_resume.file_path
        c_path = align.aligned_cover_letter.file_path
        if r_path and Path(r_path).exists():
            with Path(r_path).open("rb") as doc:
                await update.message.reply_document(document=doc, filename=r_path.name)
        if c_path and Path(c_path).exists():
            with Path(c_path).open("rb") as doc:
                await update.message.reply_document(document=doc, filename=c_path.name)
