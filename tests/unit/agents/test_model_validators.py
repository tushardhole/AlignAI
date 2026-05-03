"""Unit tests for Pydantic model validators on agent output types."""

from __future__ import annotations

from alignai.agents.aligned_cover_letter_fields import AlignedCoverLetterFields
from alignai.agents.aligned_resume_fields import AlignedResumeFields
from alignai.agents.ats_score_fields import AtsScoreFields
from alignai.agents.job_brief_fields import JobBriefFields
from alignai.agents.match_score_fields import MatchScoreFields
from alignai.agents.merged_resume_fields import MergedResumeFields
from alignai.agents.parsed_resume_fields import ParsedResumeFields
from alignai.agents.section_aligned_fields import SectionAlignedFields
from alignai.domain.models import MatchLabel


class TestJobBriefFieldsValidator:
    def test_canonical_keys(self) -> None:
        data = {
            "title": "Engineer",
            "summary": "A role",
            "must_have_skills": ["Python"],
            "nice_to_have_skills": ["Go"],
        }
        result = JobBriefFields.model_validate(data)
        assert result.title == "Engineer"
        assert result.must_have_skills == ["Python"]

    def test_camel_case_keys(self) -> None:
        data = {
            "jobTitle": "Engineer",
            "description": "A role",
            "requiredSkills": ["Python", "SQL"],
            "preferredSkills": ["Go"],
        }
        result = JobBriefFields.model_validate(data)
        assert result.title == "Engineer"
        assert result.summary == "A role"
        assert result.must_have_skills == ["Python", "SQL"]

    def test_pascal_case_keys(self) -> None:
        data = {
            "Title": "Engineer",
            "Summary": "A role",
            "Must_Have_Skills": ["Python"],
        }
        result = JobBriefFields.model_validate(data)
        assert result.title == "Engineer"

    def test_comma_separated_skills(self) -> None:
        data = {
            "title": "Dev",
            "summary": "Role",
            "requirements": "Python, Java, SQL",
        }
        result = JobBriefFields.model_validate(data)
        assert "Python" in result.must_have_skills
        assert "SQL" in result.must_have_skills


class TestAlignedResumeFieldsValidator:
    def test_canonical(self) -> None:
        result = AlignedResumeFields.model_validate(
            {"content": "resume text"},
        )
        assert result.content == "resume text"

    def test_pascal_case(self) -> None:
        result = AlignedResumeFields.model_validate(
            {"Content": "resume text"},
        )
        assert result.content == "resume text"

    def test_resume_key(self) -> None:
        result = AlignedResumeFields.model_validate(
            {"Resume": "resume text here"},
        )
        assert result.content == "resume text here"

    def test_aligned_resume_key(self) -> None:
        result = AlignedResumeFields.model_validate(
            {"aligned_resume": "the resume"},
        )
        assert result.content == "the resume"

    def test_single_unknown_string_fallback(self) -> None:
        result = AlignedResumeFields.model_validate(
            {"weird_key": "this is a long enough resume text for fallback"},
        )
        assert "long enough" in result.content

    def test_nested_dict_flattened(self) -> None:
        result = AlignedResumeFields.model_validate(
            {"content": {"summary": "A", "experience": "B"}},
        )
        assert "summary" in result.content
        assert "experience" in result.content


class TestAlignedCoverLetterFieldsValidator:
    def test_canonical(self) -> None:
        result = AlignedCoverLetterFields.model_validate(
            {"content": "letter"},
        )
        assert result.content == "letter"

    def test_cover_letter_key(self) -> None:
        result = AlignedCoverLetterFields.model_validate(
            {"CoverLetter": "my letter text"},
        )
        assert result.content == "my letter text"

    def test_body_key(self) -> None:
        result = AlignedCoverLetterFields.model_validate(
            {"body": "letter body"},
        )
        assert result.content == "letter body"


class TestAtsScoreFieldsValidator:
    def test_canonical(self) -> None:
        result = AtsScoreFields.model_validate({"score": 85})
        assert result.score == 85

    def test_pascal_case(self) -> None:
        result = AtsScoreFields.model_validate({"Score": 85})
        assert result.score == 85

    def test_ats_score_key(self) -> None:
        result = AtsScoreFields.model_validate({"ats_score": 90})
        assert result.score == 90

    def test_camel_case_key(self) -> None:
        result = AtsScoreFields.model_validate({"atsScore": 80})
        assert result.score == 80

    def test_string_score(self) -> None:
        result = AtsScoreFields.model_validate({"score": "85"})
        assert result.score == 85

    def test_float_score(self) -> None:
        result = AtsScoreFields.model_validate({"score": 85.5})
        assert result.score == 85

    def test_clamped_high(self) -> None:
        result = AtsScoreFields.model_validate({"score": 150})
        assert result.score == 100

    def test_nested_score_dict(self) -> None:
        result = AtsScoreFields.model_validate(
            {"ats_score": {"score": 75, "reason": "good"}},
        )
        assert result.score == 75

    def test_fallback_to_first_numeric(self) -> None:
        result = AtsScoreFields.model_validate(
            {"unknown_key": 88},
        )
        assert result.score == 88


class TestMatchScoreFieldsValidator:
    def test_canonical(self) -> None:
        result = MatchScoreFields.model_validate(
            {"score": 4, "label": "Good Match"},
        )
        assert result.score == 4
        assert result.label == MatchLabel.GOOD_MATCH

    def test_case_insensitive_label(self) -> None:
        result = MatchScoreFields.model_validate(
            {"score": 4, "label": "good match"},
        )
        assert result.label == MatchLabel.GOOD_MATCH

    def test_underscore_label(self) -> None:
        result = MatchScoreFields.model_validate(
            {"score": 5, "label": "STRONG_MATCH"},
        )
        assert result.label == MatchLabel.STRONG_MATCH

    def test_camel_case_keys(self) -> None:
        result = MatchScoreFields.model_validate(
            {"matchScore": 3, "matchLabel": "Fair Match"},
        )
        assert result.score == 3
        assert result.label == MatchLabel.FAIR_MATCH

    def test_label_fallback_from_score(self) -> None:
        result = MatchScoreFields.model_validate({"score": 5})
        assert result.score == 5
        assert result.label == MatchLabel.STRONG_MATCH

    def test_string_score(self) -> None:
        result = MatchScoreFields.model_validate(
            {"score": "4", "label": "Good Match"},
        )
        assert result.score == 4


class TestMergedResumeFieldsValidator:
    def test_canonical(self) -> None:
        result = MergedResumeFields.model_validate({"content": "text"})
        assert result.content == "text"

    def test_resume_key(self) -> None:
        result = MergedResumeFields.model_validate(
            {"merged_resume": "full text"},
        )
        assert result.content == "full text"


class TestParsedResumeFieldsValidator:
    def test_canonical(self) -> None:
        result = ParsedResumeFields.model_validate(
            {
                "sections": [
                    {"heading": "Exp", "content": "5 years"},
                ],
            },
        )
        assert len(result.sections) == 1
        assert result.sections[0].heading == "Exp"

    def test_pascal_case_sections_key(self) -> None:
        result = ParsedResumeFields.model_validate(
            {
                "Sections": [
                    {"Heading": "Exp", "Content": "5 years"},
                ],
            },
        )
        assert len(result.sections) == 1

    def test_flat_dict_as_sections(self) -> None:
        result = ParsedResumeFields.model_validate(
            {
                "Experience": "5 years at Acme",
                "Education": "BSc Computer Science",
            },
        )
        assert len(result.sections) == 2
        headings = {s.heading for s in result.sections}
        assert "Experience" in headings
        assert "Education" in headings

    def test_title_as_heading_alias(self) -> None:
        result = ParsedResumeFields.model_validate(
            {
                "sections": [
                    {"title": "Skills", "body": "Python, SQL"},
                ],
            },
        )
        assert result.sections[0].heading == "Skills"
        assert result.sections[0].content == "Python, SQL"


class TestSectionAlignedFieldsValidator:
    def test_canonical(self) -> None:
        result = SectionAlignedFields.model_validate(
            {"aligned_content": "rewritten"},
        )
        assert result.aligned_content == "rewritten"

    def test_content_alias(self) -> None:
        result = SectionAlignedFields.model_validate(
            {"content": "rewritten"},
        )
        assert result.aligned_content == "rewritten"

    def test_camel_case(self) -> None:
        result = SectionAlignedFields.model_validate(
            {"alignedContent": "rewritten section"},
        )
        assert result.aligned_content == "rewritten section"

    def test_single_long_value_fallback(self) -> None:
        result = SectionAlignedFields.model_validate(
            {"bizarre_key": "this is a sufficiently long rewritten section text"},
        )
        assert "sufficiently long" in result.aligned_content
