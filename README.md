# AlignAI

> AI-powered resume and cover-letter aligner with a Telegram bot interface.

AlignAI takes your base résumé, a cover-letter template, and a job-posting URL (or pasted text),
then uses an agentic pipeline (OpenAI Agents SDK) to produce a tailored résumé and cover letter,
ATS score, and match score — delivered as PDFs either through the desktop UI or your Telegram bot.

---

## Architecture

```
src/alignai/
  domain/       ← pure dataclasses + Protocol interfaces (no I/O)
  application/  ← use cases
  agents/       ← OpenAI Agents SDK orchestration
  infra/        ← adapters (HTTP, SQLite, Playwright, keyring…)
  ui/           ← PySide6 desktop views
  main.py       ← DI root + entry-point
```

Dependency rules are enforced by `import-linter` (see `pyproject.toml`).

## Quick-start (development)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
pytest -m "not integration"
```

## Coding rules

See [`CLAUDE.md`](CLAUDE.md) (mirrored to [`.cursorrules`](.cursorrules)).

## Documentation

| Doc | Description |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Layer diagram, threading model |
| [`docs/USAGE.md`](docs/USAGE.md) | Desktop + bot walkthroughs |
| [`docs/AI_ENGINEERING.md`](docs/AI_ENGINEERING.md) | Tools, MCP, multi-agent rationale |

## License

MIT
