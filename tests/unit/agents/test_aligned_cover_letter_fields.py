"""Tests for AlignedCoverLetterFields LLM shape coercion."""

from __future__ import annotations

from alignai.agents.aligned_cover_letter_fields import AlignedCoverLetterFields


def test_cover_letter_coerces_cover_letter_key() -> None:
    raw = {"coverLetter": "Sincerely, Jane"}
    out = AlignedCoverLetterFields.model_validate(raw)
    assert out.content == "Sincerely, Jane"


def test_cover_letter_preserves_content() -> None:
    out = AlignedCoverLetterFields.model_validate({"content": "Hello"})
    assert out.content == "Hello"


def test_cover_letter_coerces_nested_cover_letter_object() -> None:
    raw = {
        "coverLetter": {
            "name": "Tushar Dhole",
            "introduction": "Backend engineer.",
            "closing": "Thanks",
        }
    }
    out = AlignedCoverLetterFields.model_validate(raw)
    assert "Tushar Dhole" in out.content
    assert "Backend engineer" in out.content
    assert "Thanks" in out.content
