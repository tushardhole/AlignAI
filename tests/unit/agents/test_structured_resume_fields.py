"""Tests for StructuredResumeFields Pydantic model normalization."""

from alignai.agents.structured_resume_fields import StructuredResumeFields


def test_snake_case_input() -> None:
    data = {
        "name": "John Doe",
        "email": "john@example.com",
        "skills_by_category": {"Languages": ["Python", "Go"]},
        "experience": [
            {
                "title": "Engineer",
                "company": "Acme",
                "dates": "2020-2024",
                "bullets": ["Built systems"],
                "meta": [{"label": "Tech", "value": "Python, Go"}],
            }
        ],
        "education": [{"degree": "BS CS", "school": "MIT", "graduation_date": "2020"}],
    }
    result = StructuredResumeFields.model_validate(data)
    assert result.name == "John Doe"
    assert result.skills_by_category == {"Languages": ["Python", "Go"]}
    assert len(result.experience) == 1
    assert result.experience[0]["title"] == "Engineer"
    assert result.experience[0]["meta"][0]["label"] == "Tech"


def test_camel_case_input() -> None:
    data = {
        "candidateName": "Jane Smith",
        "emailAddress": "jane@test.com",
        "phoneNumber": "555-1234",
        "skillsByCategory": {"Frontend": ["React", "Vue"]},
        "workExperience": [
            {
                "jobTitle": "Developer",
                "employer": "BigCo",
                "dateRange": "2019-2023",
                "achievements": ["Shipped v2"],
            }
        ],
    }
    result = StructuredResumeFields.model_validate(data)
    assert result.name == "Jane Smith"
    assert result.email == "jane@test.com"
    assert result.phone == "555-1234"
    assert result.skills_by_category == {"Frontend": ["React", "Vue"]}
    assert result.experience[0]["title"] == "Developer"
    assert result.experience[0]["company"] == "BigCo"


def test_missing_fields_default_to_empty() -> None:
    data = {"name": "Minimal"}
    result = StructuredResumeFields.model_validate(data)
    assert result.name == "Minimal"
    assert result.email == ""
    assert result.experience == []
    assert result.education == []
    assert result.skills_by_category == {}
    assert result.affiliations == []


def test_flat_skills_list_wrapped_in_category() -> None:
    data = {"name": "Test", "skills": ["Python", "AWS", "Docker"]}
    result = StructuredResumeFields.model_validate(data)
    assert result.skills_by_category == {"Skills": ["Python", "AWS", "Docker"]}


def test_meta_extracted_from_tech_field() -> None:
    data = {
        "name": "Test",
        "experience": [
            {
                "title": "Dev",
                "company": "Co",
                "dates": "2022",
                "bullets": ["Did stuff"],
                "tech": "Python, FastAPI",
            }
        ],
    }
    result = StructuredResumeFields.model_validate(data)
    assert result.experience[0]["meta"][0]["label"] == "Tech"
    assert result.experience[0]["meta"][0]["value"] == "Python, FastAPI"


def test_links_as_objects() -> None:
    data = {
        "name": "Test",
        "links": [
            {"url": "https://github.com/test", "display": "github.com/test"},
            {"href": "https://linkedin.com/in/test", "text": "linkedin.com/in/test"},
        ],
    }
    result = StructuredResumeFields.model_validate(data)
    assert len(result.links) == 2
    assert result.links[0]["url"] == "https://github.com/test"
    assert result.links[1]["url"] == "https://linkedin.com/in/test"


def test_links_as_strings() -> None:
    data = {"name": "Test", "links": ["https://github.com/user"]}
    result = StructuredResumeFields.model_validate(data)
    assert result.links[0]["url"] == "https://github.com/user"
