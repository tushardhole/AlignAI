# Usage

## Desktop application

1. Install (`pip install -e ".[dev]"`) and run `alignai` (or `python -m alignai.main`).
2. Complete onboarding: OpenAI-compatible base URL, model name, API key; optional Telegram bot token (stored in OS keyring).
3. Set **base résumé** and **cover letter** via **Settings** or the New Alignment screen (PDF/DOCX).
4. **New Alignment**: paste a job URL. AlignAI fetches the listing (`httpx` + trafilatura, then Playwright if needed). If the page is unreadable, paste the full job description when prompted.
5. Results show ATS score, match score/label, and paths to generated PDFs.

### Unreadable job pages

When extraction yields too little text, the app asks you to paste the job description. The same pipeline runs with `JobPosting(source="pasted")`.

### Offline desktop + Telegram

Telegram cannot deliver replies while AlignAI is not running. When you restart the app, the bot processes backlog updates and prefixes messages with *AlignAI was offline when you sent this; running it now.* when the message predates the current polling session.

### Optional always-on presence proxy

For users who want an instant “start the desktop app” reply without hosting the full bot, see [`tools/telegram_presence_proxy/README.md`](../tools/telegram_presence_proxy/README.md) (architecture stub; not required for the MVP).

## Telegram bot

1. Create a bot via [@BotFather](https://t.me/BotFather) and paste the token during onboarding (keyring: `telegram_bot_token`).
2. Send a job posting URL in chat. The bot asks you to send `/align`.
3. `/align` runs the same alignment pipeline as the desktop app (base documents must be configured once in the desktop UI).
4. If the job URL cannot be read, paste the job text as your next message.

## Screenshots

*(Placeholder: add UI screenshots for home table, new alignment, result, and settings.)*
