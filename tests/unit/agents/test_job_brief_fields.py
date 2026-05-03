"""Tests for JobBriefFields coercion (LLM json_object quirks)."""

from __future__ import annotations

from alignai.agents.job_brief_fields import JobBriefFields


def test_job_brief_coerces_pascal_case_pm_g_style_payload() -> None:
    raw = {
        "Title": "AI & Software Engineer III",
        "Company": "PMG",
        "JobType": "Full-time",
        "Category": "Software Engineering",
        "YearsOfExperience": "3+ years",
        "JobLocation": "Global",
        "Languages": ["NodeJS", "Python", "Go", "React"],
        "Frameworks": ["Beego", "Django"],
        "CloudProviders": ["AWS"],
        "RequiredSkills": [
            "high-performance framework",
            "system design principles",
            "SOLID software engineering practices",
            "RESTful APIs",
        ],
        "DesiredSkills": ["familiarity with Alli", "AI-powered tools"],
        "DegreeLevel": "Unknown",
        "Certifications": "None",
        "WorkTypes": ["remote work possible"],
        "HiringManager": "Unknown",
        "InterviewProcess": "In-person and/or video interviews",
    }
    got = JobBriefFields.model_validate(raw)
    assert got.title == "AI & Software Engineer III"
    assert "PMG" in got.summary
    assert "Python" in got.must_have_skills
    assert "RESTful APIs" in got.must_have_skills
    assert "AI-powered tools" in got.nice_to_have_skills


def test_job_brief_coerces_snake_case_pm_g_required_blocks() -> None:
    raw = {
        "job_title": "AI & Software Engineer III",
        "required_languages": ["NodeJS", "Python", "Go", "React"],
        "required_frameworks": ["Beego", "Django"],
        "required_experience": {
            "software_development": 3,
            "high_performance_frameworks": 2,
            "cloud_providers": 1,
            "project_life_cycle": 1,
        },
        "required_skills": [
            "written_and_spoken_english",
            "system_design_principles",
            "RESTful_APIs",
        ],
        "required_education": None,
        "required_certifications": None,
        "required_work_experience": {
            "previous_employment": None,
            "previous_roles": ["AI & Software Engineer"],
        },
        "job_location": "global",
        "company_name": "PMG",
        "company_description": "a global independent marketing services and technology company",
    }
    got = JobBriefFields.model_validate(raw)
    assert got.title == "AI & Software Engineer III"
    assert "PMG" in got.summary
    assert "Python" in got.must_have_skills
    assert any("years in software development" in s.lower() for s in got.must_have_skills)


def test_job_brief_canonical_keys_unchanged() -> None:
    got = JobBriefFields.model_validate(
        {
            "title": "Engineer",
            "summary": "Build things.",
            "must_have_skills": ["Python"],
            "nice_to_have_skills": ["Rust"],
        }
    )
    assert got.title == "Engineer"
    assert got.summary == "Build things."
    assert got.must_have_skills == ["Python"]
    assert got.nice_to_have_skills == ["Rust"]


def test_job_brief_coerces_camel_case_job_title_and_skills_lists() -> None:
    raw = {
        "jobTitle": "AI & Software Engineer III",
        "company": "PMG",
        "location": "Jersey City, NJ",
        "experience": "12+ years",
        "skills": ["Java", "Python", "AWS"],
        "education": [
            {
                "degree": "Master of Science",
                "fieldOfStudy": "Data Science",
                "institution": "Saint Peter's University",
            },
        ],
        "certifications": ["AWS Certified Cloud Practitioner"],
        "responsibilities": [
            "Design, develop, and deploy features on the Alli platform",
            "Collaborate with cross-functional teams",
        ],
    }
    got = JobBriefFields.model_validate(raw)
    assert got.title == "AI & Software Engineer III"
    assert "PMG" in got.summary
    assert "Jersey City" in got.summary
    assert "Java" in got.must_have_skills
    assert "AWS Certified" in " ".join(got.must_have_skills)
    assert any("Alli" in s for s in got.must_have_skills)


def test_job_brief_coerces_skills_object_required_and_nice_arrays() -> None:
    raw = {
        "title": "Engineer",
        "skills": {
            "required": ["Python", "Go"],
            "niceToHave": ["Beego", "Django"],
        },
    }
    got = JobBriefFields.model_validate(raw)
    assert "Python" in got.must_have_skills
    assert "Beego" in got.nice_to_have_skills
