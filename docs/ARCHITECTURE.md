# Architecture

AlignAI follows **hexagonal (ports and adapters)** layering so domain logic stays free of I/O and UI frameworks.

## Layers

| Layer | Role | Imports allowed |
| --- | --- | --- |
| `domain` | Entities, value objects, `Protocol` ports | stdlib, pure libs |
| `application` | Use cases (`execute`-style APIs) | `domain` only |
| `agents` | OpenAI Agents SDK orchestration | `domain`, `application`, SDK |
| `infra` | SQLite, HTTP, Playwright, keyring, Telegram PTB | `domain`, `application` |
| `ui` | PySide6 views | `domain`, `application` |
| `main.py` | Composition root / dependency injection | all concrete adapters |

`import-linter` and `scripts/preflight.py` enforce this graph.

## Threading model

```text
┌─────────────────────────────────────────────────────────┐
│  Qt main thread: QApplication event loop + MainWindow    │
└─────────────────────────────────────────────────────────┘
          │
          ├── AsyncRunnerThread: asyncio alignment / fetch
          │     (QThread + QEventLoop integration via helpers)
          │
          └── BlockingRunnerThread: Telegram `run_polling`
                (long-poll loop; shares DI graph built in main.py)
```

Agent work runs off the UI thread via `AsyncRunnerThread`. Optional Telegram polling runs on a dedicated worker thread started after the window is shown.

## Persistence

- **SQLite**: alignment index (`SqliteAlignmentRepository`).
- **Filesystem** under `platformdirs.user_data_path("AlignAI")`: base résumé/cover PDFs or DOCX, rendered outputs.

See [`USAGE.md`](USAGE.md) for operational notes.
