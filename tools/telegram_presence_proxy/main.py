"""Placeholder for an optional cloud Telegram webhook + heartbeat bridge."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info(
        "telegram_presence_proxy stub: deploy your own worker; see README.md in this folder.",
    )


if __name__ == "__main__":
    main()
