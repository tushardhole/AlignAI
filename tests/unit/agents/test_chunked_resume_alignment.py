"""Chunked resume alignment prompt and shape hints."""

from __future__ import annotations

from alignai.agents.prompts import load_schema_hint


def test_resume_parser_shape_prefers_sections_and_experience_array() -> None:
    s = load_schema_hint("resume_parser_shape")
    assert "sections" in s
    assert "Experience" in s
    assert '[{"Employer":"Acme"' in s.replace(" ", "")
    assert "INVALID" in s and "VALID" in s


def test_merger_hint_requests_single_content_string() -> None:
    h = load_schema_hint("merger_output")
    assert '"content"' in h
    assert "nested JSON" in h.lower() or "nested" in h.lower()
