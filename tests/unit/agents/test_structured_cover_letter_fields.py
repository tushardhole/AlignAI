"""Tests for StructuredCoverLetterFields Pydantic model normalization."""

from alignai.agents.structured_cover_letter_fields import StructuredCoverLetterFields


def test_canonical_input() -> None:
    data = {
        "candidate_name": "John Doe",
        "paragraphs": [
            "I am excited about this role.",
            "My experience aligns well.",
        ],
    }
    result = StructuredCoverLetterFields.model_validate(data)
    assert result.candidate_name == "John Doe"
    assert len(result.paragraphs) == 2


def test_camel_case_keys() -> None:
    data = {
        "candidateName": "Jane Smith",
        "bodyParagraphs": ["First paragraph.", "Second paragraph."],
    }
    result = StructuredCoverLetterFields.model_validate(data)
    assert result.candidate_name == "Jane Smith"
    assert len(result.paragraphs) == 2


def test_body_string_split_into_paragraphs() -> None:
    data = {
        "name": "Test User",
        "body": (
            "I am writing to express my interest.\n\n"
            "I have extensive experience in backend development.\n\n"
            "I look forward to discussing this opportunity."
        ),
    }
    result = StructuredCoverLetterFields.model_validate(data)
    assert result.candidate_name == "Test User"
    assert len(result.paragraphs) == 3


def test_greeting_and_closing_stripped() -> None:
    data = {
        "candidate_name": "Alex",
        "content": (
            "Dear Hiring Manager,\n\n"
            "I am interested in this position and have the required skills.\n\n"
            "My background in cloud infrastructure is directly relevant.\n\n"
            "Regards,\n"
            "Alex"
        ),
    }
    result = StructuredCoverLetterFields.model_validate(data)
    assert not any("Dear" in p for p in result.paragraphs)
    assert not any("Regards" in p for p in result.paragraphs)
    assert len(result.paragraphs) == 2


def test_empty_input_defaults() -> None:
    data: dict[str, str] = {}
    result = StructuredCoverLetterFields.model_validate(data)
    assert result.candidate_name == ""
    assert result.paragraphs == []


def test_contact_name_alias() -> None:
    data = {
        "contactName": "Bob Builder",
        "paragraphs": ["I can fix it."],
    }
    result = StructuredCoverLetterFields.model_validate(data)
    assert result.candidate_name == "Bob Builder"
