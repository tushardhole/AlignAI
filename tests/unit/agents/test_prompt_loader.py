"""Tests for prompt loader utility."""

import pytest

from alignai.agents.prompts import load_prompt, load_schema_hint


class TestPromptLoader:
    """Test load_prompt function."""

    def test_load_prompt_returns_content(self) -> None:
        """load_prompt returns non-empty content for valid prompt."""
        content = load_prompt("job_analyst")
        assert isinstance(content, str)
        assert len(content) > 0
        assert "ATS analyst" in content or "extract" in content.lower()

    def test_load_prompt_caches_results(self) -> None:
        """load_prompt caches results (same object on second call)."""
        content1 = load_prompt("job_analyst")
        content2 = load_prompt("job_analyst")
        # Both should be identical strings
        assert content1 == content2

    def test_load_prompt_missing_raises_error(self) -> None:
        """load_prompt raises FileNotFoundError for missing prompt."""
        with pytest.raises(FileNotFoundError, match="not found"):
            load_prompt("nonexistent_prompt")

    def test_load_all_prompts(self) -> None:
        """All expected prompts can be loaded."""
        prompts = [
            "job_analyst",
            "resume_aligner",
            "cover_letter_aligner",
            "ats_scorer",
            "match_scorer",
            "resume_structurer",
            "cover_letter_structurer",
            "resume_parser",
            "resume_section_aligner",
            "resume_merger",
        ]
        for name in prompts:
            content = load_prompt(name)
            assert isinstance(content, str)
            assert len(content) > 0


class TestSchemaHintLoader:
    """Test load_schema_hint function."""

    def test_load_schema_hint_returns_content(self) -> None:
        """load_schema_hint returns non-empty content for valid hint."""
        content = load_schema_hint("job_brief_shape")
        assert isinstance(content, str)
        assert len(content) > 0
        assert "JSON" in content

    def test_load_schema_hint_caches_results(self) -> None:
        """load_schema_hint caches results."""
        content1 = load_schema_hint("job_brief_shape")
        content2 = load_schema_hint("job_brief_shape")
        assert content1 == content2

    def test_load_schema_hint_missing_raises_error(self) -> None:
        """load_schema_hint raises FileNotFoundError for missing hint."""
        with pytest.raises(FileNotFoundError, match="not found"):
            load_schema_hint("nonexistent_hint")

    def test_load_all_schema_hints(self) -> None:
        """All expected schema hints can be loaded."""
        hints = [
            "job_brief_shape",
            "resume_structure",
            "cover_letter_structure",
            "resume_parser_shape",
            "merger_output",
        ]
        for name in hints:
            content = load_schema_hint(name)
            assert isinstance(content, str)
            assert len(content) > 0
