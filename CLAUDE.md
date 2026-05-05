# AlignAI — Coding Rules

<!-- .cursorrules is a symlink to this file — edit CLAUDE.md only -->

> **Self-review gate:** before every commit, run `python scripts/preflight.py`.
> The script enforces all rules below and will exit non-zero (blocking the
> commit) if any violation is found. The pre-commit hook also calls it
> automatically.

---

## Architecture: Hexagonal / Clean

```text
domain/        ← pure Python: dataclasses + Protocol interfaces, ZERO I/O
application/   ← use cases; depends only on domain
agents/        ← OpenAI Agents SDK wiring; may depend on domain + application
infra/         ← adapters (HTTP, SQLite, Playwright, keyring …)
ui/            ← PySide6 views; depends only on application + domain
main.py        ← DI root; the ONLY place that imports concrete infra/agents
```

### Dependency rules (enforced by `import-linter` in CI and pre-commit)

| Layer | May import |
| --- | --- |
| `domain` | stdlib, third-party pure libs |
| `application` | `domain` |
| `agents` | `domain`, `application`, OpenAI Agents SDK |
| `infra` | `domain`, `application` |
| `ui` | `domain`, `application` |
| `main` | all of the above |

**Violations are a hard CI failure.** Do not use `# noqa` to bypass
import-linter.

---

## Structure rules

- **One public class per file.** Helper dataclasses / enums used only within
  the same file are allowed. Private helpers prefixed with `_` are fine.
- **≤ 200 lines per class** (excluding docstrings and blank lines).
  `preflight.py` enforces this.
- **Method names are verbs** (`fetch`, `save`, `render`, `handle`).
  **Class names are nouns** (`JobFetcher`, `AlignmentRepository`).
- All cross-layer collaborators injected via constructor (Protocol
  interface). No module-level singletons, no `global`, no `importlib`
  hacks.

---

## Type safety

- **`strict = true`** mypy; no `Any` except where unavoidable (document why
  with a comment).
- All LLM I/O boundaries use **Pydantic v2 models** with explicit
  `model_config`.
- Domain entities use **`@dataclass(frozen=True)`**.
- No bare `except:` or `except Exception:` — catch specific exception types.

---

## Testing

- Every new public function/method in `domain/` or `application/` needs a
  test.
- Coverage gate: **≥ 85%** on `domain` and `application` (enforced by
  `pytest-cov`).
- Use `FakeLlmClient` (replays fixtures from `tests/fixtures/recorded_llm/`)
  for unit tests.
- Flexible LLM assertions (ranges/sets, not exact strings):

  ```python
  assert 75 <= result.ats_score <= 90
  assert result.match_label in {"Strong Match", "Good Match"}
  ```

- Integration tests marked `@pytest.mark.integration`; excluded from default
  `pytest` run.

---

## Commits & PRs

- **Conventional Commits:** `feat:`, `fix:`, `refactor:`, `test:`, `docs:`,
  `chore:`.
- One logical change per commit.
- PRs **≤ ~400 lines diff** (excluding lock files and generated files).
- PR description must reference the relevant plan phase (e.g.
  `phase: skeleton`).

---

## Pre-commit hooks (run automatically on `git commit`)

1. `ruff format` — auto-formats.
2. `ruff check --fix` — lints and auto-fixes safe issues.
3. `mypy` — type checks `src/alignai` and `scripts/`.
4. `lint-imports` — enforces layer isolation contracts.
5. `python scripts/preflight.py` — final gate (file size, missing tests,
   layering).
6. Standard hooks: trailing whitespace, end-of-file, YAML/TOML validity, no
   merge conflicts, no debug statements, no large files (> 500 KB).

---

## Text cleanup rule

Every LLM-produced string **must** pass through `infra.text_cleanup.clean()`
before being persisted or rendered. The cleaner handles em-dashes, en-dashes
(preserving numeric ranges), double underscores, and collapsed whitespace.
See `infra/text_cleanup.py` for the regex specification and its unit tests.

---

## Alignment Prompts & Rules Documentation

All LLM agent instructions live in `src/alignai/agents/prompts/` as
separate `.txt` files. `docs/alignment_rules.md` is the single source of
truth for how alignment works.

**When modifying prompts or alignment logic:**

1. **Edit prompt text**: Modify the corresponding `.txt` file in
   `prompts/` directory
2. **Change chunking threshold (currently 12,000 chars)**: Update three
   places:
   - `src/alignai/agents/align_ai_runner.py` line ~21:
     `_DEFAULT_CHUNK_THRESHOLD`
   - `docs/alignment_rules.md`: "Single-Pass vs Chunked Decision"
     section
   - Commit message should reference all three locations
3. **Add/remove JSON fields in schema**:
   - Corresponding schema hint file in `prompts/schema_hints/`
   - Pydantic model in `src/alignai/agents/structured_*.py`
   - `docs/alignment_rules.md` Agent Rules section
4. **Modify agent behavior**: Update prompt AND update corresponding
   rule in `alignment_rules.md`

**CRITICAL**: `docs/alignment_rules.md` must stay in sync with code.
Update it whenever you change:

- Any prompt instruction
- Chunking decision logic or thresholds
- Character truncation limits
- Agent rules or behavior

This ensures documentation stays in sync with code and all developers
understand the alignment strategy, when chunking happens, and what each
agent does.

---

## Secrets

- Never commit secrets. Use `keyring` for tokens (Telegram, LLM API key).
- Non-secret settings (base URL, model name) live in a JSON file under
  `platformdirs.user_config_dir("AlignAI")`.
- `.env` files are gitignored; use them only for local dev overrides, never
  in tests.
