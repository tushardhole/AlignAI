"""Use case: verify LLM and Telegram credentials."""

from __future__ import annotations

from alignai.domain.ports import LlmClient, LlmMessage, TelegramCredentialsVerifier


class VerifyCredentials:
    """Probes third-party APIs with minimal traffic."""

    def __init__(
        self,
        llm_client: LlmClient,
        telegram_verifier: TelegramCredentialsVerifier,
    ) -> None:
        self._llm_client = llm_client
        self._telegram_verifier = telegram_verifier

    async def verify_llm(self) -> bool:
        try:
            await self._llm_client.complete(
                [LlmMessage(role="user", content="ping")],
                max_tokens=2,
            )
        except ValueError:
            return False
        return True

    async def verify_telegram(self, bot_token: str) -> bool:
        return await self._telegram_verifier.verify_bot_token(bot_token)
