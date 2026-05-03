"""Chunked resume alignment prompt and shape hints."""

from __future__ import annotations

from alignai.agents import chunked_resume_alignment as m


def test_resume_parser_shape_prefers_sections_and_experience_array() -> None:
    s = m._RESUME_PARSER_JSON_OBJECT_SHAPE
    assert "sections" in s
    assert "Experience" in s
    assert '[{"Employer":"Acme"' in s.replace(" ", "")
    assert "INVALID" in s and "VALID" in s


def test_merger_hint_requests_single_content_string() -> None:
    h = m._MERGER_OUTPUT_HINT
    assert '"content"' in h
    assert "nested JSON" in h.lower() or "nested" in h.lower()
