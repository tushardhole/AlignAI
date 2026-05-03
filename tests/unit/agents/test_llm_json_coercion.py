"""Unit tests for LLM JSON coercion helpers."""

from __future__ import annotations

from alignai.agents.llm_json_coercion import (
    coerce_int,
    coerce_match_label,
    coerce_str,
    coerce_str_list,
    find_value,
)
from alignai.domain.models import MatchLabel


class TestFindValue:
    def test_exact_key(self) -> None:
        assert find_value({"score": 85}, "score") == 85

    def test_case_insensitive(self) -> None:
        assert find_value({"Score": 85}, "score") == 85

    def test_camel_case(self) -> None:
        assert find_value({"atsScore": 90}, "ats_score", "atsScore") == 90

    def test_screaming_snake(self) -> None:
        assert find_value({"ATS_SCORE": 90}, "ats_score") == 90

    def test_first_alias_wins(self) -> None:
        data = {"content": "a", "text": "b"}
        assert find_value(data, "content", "text") == "a"

    def test_missing_returns_none(self) -> None:
        assert find_value({"foo": 1}, "bar") is None

    def test_hyphenated_key(self) -> None:
        assert find_value({"ats-score": 80}, "ats_score") == 80


class TestCoerceStr:
    def test_string_passthrough(self) -> None:
        assert coerce_str("hello") == "hello"

    def test_list_joins(self) -> None:
        assert coerce_str(["a", "b"]) == "a\nb"

    def test_dict_formats(self) -> None:
        result = coerce_str({"name": "Alice"})
        assert "name: Alice" in result

    def test_int_converts(self) -> None:
        assert coerce_str(42) == "42"


class TestCoerceInt:
    def test_int_passthrough(self) -> None:
        assert coerce_int(85, 1, 100) == 85

    def test_string_number(self) -> None:
        assert coerce_int("85", 1, 100) == 85

    def test_float_truncates(self) -> None:
        assert coerce_int(85.7, 1, 100) == 85

    def test_clamps_high(self) -> None:
        assert coerce_int(150, 1, 100) == 100

    def test_clamps_low(self) -> None:
        assert coerce_int(-5, 1, 100) == 1

    def test_extracts_from_dict(self) -> None:
        assert coerce_int({"score": 75, "explanation": "good"}, 1, 100) == 75

    def test_string_with_text(self) -> None:
        assert coerce_int("Score: 85/100", 1, 100) == 85

    def test_fallback_to_low(self) -> None:
        assert coerce_int("no numbers here", 1, 100) == 1


class TestCoerceStrList:
    def test_list_passthrough(self) -> None:
        assert coerce_str_list(["a", "b"]) == ["a", "b"]

    def test_comma_separated(self) -> None:
        assert coerce_str_list("Python, Java, SQL") == [
            "Python",
            "Java",
            "SQL",
        ]

    def test_numbered_list(self) -> None:
        result = coerce_str_list("1. Python\n2. Java\n3. SQL")
        assert result == ["Python", "Java", "SQL"]

    def test_single_string(self) -> None:
        assert coerce_str_list("Python") == ["Python"]

    def test_nested_dict_with_list(self) -> None:
        assert coerce_str_list({"skills": ["a", "b"]}) == ["a", "b"]


class TestCoerceMatchLabel:
    def test_exact_value(self) -> None:
        assert coerce_match_label("Strong Match") == MatchLabel.STRONG_MATCH

    def test_lowercase(self) -> None:
        assert coerce_match_label("strong match") == MatchLabel.STRONG_MATCH

    def test_underscore_form(self) -> None:
        assert coerce_match_label("strong_match") == MatchLabel.STRONG_MATCH

    def test_no_space(self) -> None:
        assert coerce_match_label("strongmatch") == MatchLabel.STRONG_MATCH

    def test_screaming_snake(self) -> None:
        assert coerce_match_label("GOOD_MATCH") == MatchLabel.GOOD_MATCH

    def test_partial_first_word(self) -> None:
        assert coerce_match_label("strong") == MatchLabel.STRONG_MATCH

    def test_fallback_by_score(self) -> None:
        assert coerce_match_label("", 5) == MatchLabel.STRONG_MATCH
        assert coerce_match_label("", 1) == MatchLabel.WEAK_MATCH

    def test_all_labels_reachable(self) -> None:
        for label in MatchLabel:
            assert coerce_match_label(label.value) == label

    def test_passthrough_enum(self) -> None:
        assert coerce_match_label(MatchLabel.FAIR_MATCH) == MatchLabel.FAIR_MATCH
