"""LLM prompt loader utility for managing agent instructions and schema hints."""

from __future__ import annotations

from pathlib import Path

_CACHE: dict[str, str] = {}


def load_prompt(name: str) -> str:
    """Load prompt from src/alignai/agents/prompts/{name}.txt

    Args:
        name: Prompt name without .txt extension (e.g., 'job_analyst')

    Returns:
        Prompt content as string

    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    if name in _CACHE:
        return _CACHE[name]

    path = Path(__file__).parent / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")

    content = path.read_text().strip()
    _CACHE[name] = content
    return content


def load_schema_hint(name: str) -> str:
    """Load schema hint from src/alignai/agents/prompts/schema_hints/{name}.txt

    Args:
        name: Schema hint name without .txt extension (e.g., 'job_brief_shape')

    Returns:
        Schema hint content as string

    Raises:
        FileNotFoundError: If schema hint file doesn't exist
    """
    cache_key = f"schema_{name}"
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    path = Path(__file__).parent / "schema_hints" / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Schema hint not found: {path}")

    content = path.read_text().strip()
    _CACHE[cache_key] = content
    return content
