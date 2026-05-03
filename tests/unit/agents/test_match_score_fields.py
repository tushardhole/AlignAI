"""Tests for MatchScoreFields LLM shape coercion."""

from __future__ import annotations

from alignai.agents.llm_json_coercion import coerce_match_label
from alignai.agents.match_score_fields import MatchScoreFields
from alignai.domain.models import MatchLabel


def test_match_score_coerces_very_strong_label_phrase() -> None:
    out = MatchScoreFields.model_validate(
        {"score": 5, "matchLabel": "Very Strong Match"},
    )
    assert out.score == 5
    assert out.label == MatchLabel.STRONG_MATCH


def test_coerce_match_label_unknown_string_uses_score_hint() -> None:
    assert coerce_match_label("Mystery Bucket", 3) == MatchLabel.FAIR_MATCH
