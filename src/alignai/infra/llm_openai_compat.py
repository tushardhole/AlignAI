"""OpenAI-compatible chat client for credential checks and simple completions."""

from __future__ import annotations

from typing import Any, cast

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError

from alignai.domain.ports import LlmMessage


class OpenAiCompatibleClient:
    """Thin wrapper around AsyncOpenAI chat completions."""

    def __init__(self, *, base_url: str, api_key: str, model: str) -> None:
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self._model = model

    async def complete(
        self,
        messages: list[LlmMessage],
        *,
        max_tokens: int = 256,
    ) -> str:
        try:
            payload = [{"role": m.role, "content": m.content} for m in messages]
            resp = await self._client.chat.completions.create(
                model=self._model,
                messages=cast(Any, payload),
                max_tokens=max_tokens,
            )
        except (APIConnectionError, APIStatusError, RateLimitError) as exc:
            raise ValueError(str(exc)) from exc
        if not resp.choices:
            raise ValueError("empty completion choices")
        choice = resp.choices[0].message.content
        return choice or ""
