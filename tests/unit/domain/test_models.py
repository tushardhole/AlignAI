"""Unit tests for domain models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from alignai.domain.models import (
    AlignmentResult,
    AtsScore,
    MatchLabel,
    MatchScore,
)


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
