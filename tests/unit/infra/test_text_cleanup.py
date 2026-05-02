"""Unit tests for deterministic text cleanup."""

from __future__ import annotations

from alignai.infra.text_cleanup import clean


class TestClean:
    def test_em_dash_between_words(self) -> None:
        text = "The woman's expression didn't change—but something behind it did."
        assert "but something" in clean(text)

    def test_collapses_double_underscore(self) -> None:
        assert clean("hello__world") == "hello world"

    def test_empty_string(self) -> None:
        assert clean("") == ""

    def test_preserves_numeric_en_dash_range(self) -> None:
        raw = "Salary 2019\u20132024"
        assert clean(raw) == raw
