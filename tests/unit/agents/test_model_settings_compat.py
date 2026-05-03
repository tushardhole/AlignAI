"""Tests for provider-specific ModelSettings helpers."""

from __future__ import annotations

from alignai.agents.model_settings_compat import (
    json_object_instruction_suffix,
    merged_json_object_model_settings,
    use_json_object_for_structured_output,
)


def test_use_json_object_when_groq_base_url() -> None:
    assert use_json_object_for_structured_output(
        llm_base_url="https://api.groq.com/openai/v1",
        settings_json_object_flag=None,
    )


def test_use_json_object_when_disabled_for_openai() -> None:
    assert not use_json_object_for_structured_output(
        llm_base_url="https://api.openai.com/v1",
        settings_json_object_flag=None,
    )


def test_use_json_object_when_settings_flag() -> None:
    assert use_json_object_for_structured_output(
        llm_base_url="https://api.openai.com/v1",
        settings_json_object_flag="1",
    )


def test_merged_json_object_sets_response_format_and_output_budget() -> None:
    ms = merged_json_object_model_settings()
    assert ms.extra_body is not None
    assert ms.extra_body.get("response_format") == {"type": "json_object"}
    assert ms.max_tokens == 16_384


def test_json_object_instruction_suffix_contains_json_token() -> None:
    text = json_object_instruction_suffix().lower()
    assert "json" in text
