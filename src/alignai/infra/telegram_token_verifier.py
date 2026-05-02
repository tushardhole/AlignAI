"""Telegram Bot API token probe."""

from __future__ import annotations

import httpx


class TelegramTokenVerifier:
    """Calls getMe to validate a bot token."""

    async def verify_bot_token(self, token: str) -> bool:
        if not token.strip():
            return False
        url = f"https://api.telegram.org/bot{token}/getMe"
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                response = await client.get(url)
        except httpx.HTTPError:
            return False
        if response.status_code != 200:
            return False
        try:
            payload = response.json()
        except ValueError:
            return False
        return bool(payload.get("ok")) is True
