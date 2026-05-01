"""Unit tests for domain models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from alignai.domain.models import (
    AlignmentResult,
    AtsScore,
    MatchLabel,
    MatchScore,
    ParsedResume,
    Resume,
    ResumeSection,
)


class TestResumeSection:
    def test_fields_stored(self) -> None:
        section = ResumeSection(heading="Experience", content="5 years at Acme")
        assert section.heading == "Experience"
        assert section.content == "5 years at Acme"

    def test_frozen(self) -> None:
        section = ResumeSection(heading="Education", content="BSc CS")
        with pytest.raises((AttributeError, TypeError)):
            section.heading = "Skills"  # type: ignore[misc]

    def test_equality(self) -> None:
        a = ResumeSection(heading="Skills", content="Python, SQL")
        b = ResumeSection(heading="Skills", content="Python, SQL")
        assert a == b

    def test_inequality_on_different_content(self) -> None:
        a = ResumeSection(heading="Skills", content="Python")
        b = ResumeSection(heading="Skills", content="Java")
        assert a != b


class TestParsedResume:
    def test_fields_stored(self) -> None:
        sections = (
            ResumeSection(heading="Summary", content="Experienced engineer"),
            ResumeSection(heading="Experience", content="5 years at Acme"),
        )
        parsed = ParsedResume(resume_id="r1", sections=sections)
        assert parsed.resume_id == "r1"
        assert len(parsed.sections) == 2
        assert parsed.sections[0].heading == "Summary"

    def test_frozen(self) -> None:
        parsed = ParsedResume(
            resume_id="r1",
            sections=(ResumeSection(heading="Summary", content="text"),),
        )
        with pytest.raises((AttributeError, TypeError)):
            parsed.resume_id = "r2"  # type: ignore[misc]

    def test_empty_sections_allowed(self) -> None:
        parsed = ParsedResume(resume_id="r1", sections=())
        assert parsed.sections == ()

    def test_sections_is_tuple(self) -> None:
        section = ResumeSection(heading="Skills", content="Python")
        parsed = ParsedResume(resume_id="r1", sections=(section,))
        assert isinstance(parsed.sections, tuple)


class TestResumeWithSections:
    def test_sections_defaults_to_none(self) -> None:
        resume = Resume(id="r1", content="raw text")
        assert resume.sections is None

    def test_sections_can_be_set(self) -> None:
        sections = (
            ResumeSection(heading="Experience", content="5 years"),
            ResumeSection(heading="Education", content="BSc CS"),
        )
        resume = Resume(id="r1", content="raw text", sections=sections)
        assert resume.sections is not None
        assert len(resume.sections) == 2

    def test_backward_compatible_without_sections(self) -> None:
        resume = Resume(id="r2", content="some content")
        assert resume.id == "r2"
        assert resume.content == "some content"
        assert resume.file_path is None
        assert resume.sections is None

    def test_frozen(self) -> None:
        resume = Resume(id="r1", content="text")
        with pytest.raises((AttributeError, TypeError)):
            resume.sections = ()  # type: ignore[misc]


class TestAtsScore:
    def test_valid_boundary_low(self) -> None:
        assert AtsScore(1).value == 1

    def test_valid_boundary_high(self) -> None:
        assert AtsScore(100).value == 100

    def test_valid_midrange(self) -> None:
        assert AtsScore(75).value == 75

    def test_below_minimum_raises(self) -> None:
        with pytest.raises(ValueError, match="AtsScore must be 1"):
            AtsScore(0)

    def test_above_maximum_raises(self) -> None:
        with pytest.raises(ValueError, match="AtsScore must be 1"):
            AtsScore(101)

    def test_frozen(self) -> None:
        score = AtsScore(50)
        with pytest.raises((AttributeError, TypeError)):
            score.value = 60  # type: ignore[misc]


class TestMatchScore:
    def test_valid_boundary_low(self) -> None:
        assert MatchScore(1).value == 1

    def test_valid_boundary_high(self) -> None:
        assert MatchScore(5).value == 5

    def test_below_minimum_raises(self) -> None:
        with pytest.raises(ValueError, match="MatchScore must be 1"):
            MatchScore(0)

    def test_above_maximum_raises(self) -> None:
        with pytest.raises(ValueError, match="MatchScore must be 1"):
            MatchScore(6)

    def test_frozen(self) -> None:
        score = MatchScore(3)
        with pytest.raises((AttributeError, TypeError)):
            score.value = 4  # type: ignore[misc]


class TestMatchLabel:
    def test_all_five_labels_exist(self) -> None:
        labels = {label.value for label in MatchLabel}
        assert labels == {
            "Strong Match",
            "Good Match",
            "Fair Match",
            "Weak Match",
            "Poor Match",
        }

    def test_str_enum_equality(self) -> None:
        assert MatchLabel.STRONG_MATCH == "Strong Match"
        assert MatchLabel.GOOD_MATCH == "Good Match"


class TestAlignmentResult:
    def test_valid_construction(self) -> None:
        result = AlignmentResult(
            aligned_resume_content="Resume text",
            aligned_cover_letter_content="Cover letter text",
            ats_score=82,
            match_score=4,
            match_label=MatchLabel.GOOD_MATCH,
        )
        assert result.ats_score == 82
        assert result.match_score == 4
        assert result.match_label == MatchLabel.GOOD_MATCH

    def test_ats_score_too_low_raises(self) -> None:
        with pytest.raises(ValidationError):
            AlignmentResult(
                aligned_resume_content="r",
                aligned_cover_letter_content="c",
                ats_score=0,
                match_score=3,
                match_label=MatchLabel.FAIR_MATCH,
            )

    def test_ats_score_too_high_raises(self) -> None:
        with pytest.raises(ValidationError):
            AlignmentResult(
                aligned_resume_content="r",
                aligned_cover_letter_content="c",
                ats_score=101,
                match_score=3,
                match_label=MatchLabel.FAIR_MATCH,
            )

    def test_match_score_too_low_raises(self) -> None:
        with pytest.raises(ValidationError):
            AlignmentResult(
                aligned_resume_content="r",
                aligned_cover_letter_content="c",
                ats_score=80,
                match_score=0,
                match_label=MatchLabel.FAIR_MATCH,
            )

    def test_match_score_too_high_raises(self) -> None:
        with pytest.raises(ValidationError):
            AlignmentResult(
                aligned_resume_content="r",
                aligned_cover_letter_content="c",
                ats_score=80,
                match_score=6,
                match_label=MatchLabel.FAIR_MATCH,
            )

    def test_immutable(self) -> None:
        result = AlignmentResult(
            aligned_resume_content="r",
            aligned_cover_letter_content="c",
            ats_score=80,
            match_score=4,
            match_label=MatchLabel.STRONG_MATCH,
        )
        with pytest.raises(ValidationError):
            result.ats_score = 50  # type: ignore[misc]
