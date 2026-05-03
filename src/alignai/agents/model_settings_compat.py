"""Model settings for OpenAI-compatible APIs that reject json_schema response_format."""

from __future__ import annotations

from urllib.parse import urlparse

from agents.model_settings import ModelSettings
from agents.models.default_models import get_default_model_settings

_JSON_OBJECT_HOSTS = {"api.groq.com"}


def use_json_object_for_structured_output(
    *,
    llm_base_url: str | None,
    settings_json_object_flag: str | None,
) -> bool:
    """Whether to force ``response_format: json_object`` (Groq and similar providers)."""
    if settings_json_object_flag == "1":
        return True
    host = urlparse(llm_base_url or "").hostname or ""
    return host in _JSON_OBJECT_HOSTS


def merged_json_object_model_settings() -> ModelSettings:
    """Defaults merged with JSON body fields that override SDK ``response_format``.

    The Agents SDK sets ``chat.completions.create(..., response_format=json_schema)`` and raises
    if ``extra_args`` repeats that key. ``extra_body`` is merged into the HTTP JSON second, so
    ``response_format: json_object`` replaces the schema form for Groq-compatible hosts.
    """
    return get_default_model_settings().resolve(
        ModelSettings(
            extra_body={"response_format": {"type": "json_object"}},
            max_tokens=16_384,
        )
    )


def json_object_instruction_suffix() -> str:
    """Text appended to system instructions when using ``json_object`` response format.

    Several OpenAI-compatible APIs return 400 unless the word *json* appears somewhere in the
    messages when ``response_format.type`` is ``json_object``.
    """
    return (
        "\n\nRespond with a single JSON object only (valid JSON, no markdown fences). "
        "The schema is enforced by the API; do not add commentary outside that JSON object. "
        "Strict JSON strings: use straight apostrophes in words (e.g. Peter's) with no "
        "backslash before them; never write \\'. Only escape double quotes as \\\" and "
        "backslashes as \\\\. No trailing commas. "
        "Finish the entire object: match all brackets and braces and close with a final }."
    )
