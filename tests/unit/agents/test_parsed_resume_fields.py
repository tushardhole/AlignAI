"""Tests for ParsedResumeFields LLM shape coercion."""

from __future__ import annotations

from alignai.agents.parsed_resume_fields import ParsedResumeFields


def test_parsed_resume_coerces_semantic_json_resume() -> None:
    raw = {
        "name": "TUSHAR DHOLE",
        "contact": [
            {"type": "Phone", "value": "+1 551-325-8740"},
            {"type": "Email", "value": "tushardhole@hotmail.com"},
        ],
        "summary": "Senior backend engineer with 12+ years.",
        "skills": {
            "Languages": ["Java", "Kotlin"],
            "Cloud": ["GCP", "Kubernetes"],
        },
        "experience": [
            {
                "position": "Senior Backend Engineer",
                "company": "HelloFresh, Berlin",
                "date": "Jun 2023 – Dec 2024",
                "responsibilities": [
                    "Owned design and delivery of HelloPay.",
                    "Migrated messaging from RabbitMQ to Kafka.",
                ],
            }
        ],
    }
    got = ParsedResumeFields.model_validate(raw)
    assert len(got.sections) >= 4
    headings = {s.heading for s in got.sections}
    assert "Contact" in headings
    assert "Summary" in headings
    assert "Skills" in headings
    assert "Experience" in headings
    exp_sec = next(s for s in got.sections if s.heading == "Experience")
    assert "HelloFresh" in exp_sec.content
    assert "Kafka" in exp_sec.content


def test_parsed_resume_section_list_unchanged() -> None:
    got = ParsedResumeFields.model_validate(
        {
            "sections": [
                {"heading": "Experience", "content": "Acme — Engineer"},
                {"heading": "Education", "content": "BS CS"},
            ]
        }
    )
    assert len(got.sections) == 2
    assert got.sections[0].heading == "Experience"


def test_parsed_resume_experience_and_education_as_dicts() -> None:
    raw = {
        "experiences": {
            "Senior Backend Engineer (IC5)": {
                "Company": "HelloFresh, Berlin",
                "Dates": "Jun 2023 – Dec 2024",
                "Points": ["Shipped payments platform.", "Migrated to Kafka."],
            }
        },
        "education": {
            "Master of Science, Data Science": "Saint Peter's University, NJ",
            "Bachelor of Engineering": "YCCE, Nagpur",
        },
        "certifications": {"AWS Certified Cloud Practitioner": ""},
    }
    got = ParsedResumeFields.model_validate(raw)
    headings = [s.heading for s in got.sections]
    assert "Experience" in headings
    assert "Education" in headings
    assert "Certifications" in headings
    exp_sec = next(s for s in got.sections if s.heading == "Experience")
    assert "HelloFresh" in exp_sec.content
    assert "Kafka" in exp_sec.content


def test_parsed_resume_education_and_employment_pascal_keys() -> None:
    raw = {
        "Education": [
            {
                "Title": "Master of Science, Data Science",
                "Institution": "Saint Peter's University",
                "Location": "Jersey City, NJ",
            },
            {
                "Title": "Bachelor of Engineering",
                "Institution": "YCCE",
                "Location": "Nagpur",
            },
        ],
        "Employment": [
            {
                "Company": "PMG",
                "JobTitle": "AI & Software Engineer III",
                "Duration": "Ongoing",
                "Responsibilities": [
                    "Ship features on the Alli platform.",
                    "Review code across Alli.",
                ],
            }
        ],
    }
    got = ParsedResumeFields.model_validate(raw)
    headings = [s.heading for s in got.sections]
    assert "Education" in headings
    assert "Experience" in headings
    edu = next(s for s in got.sections if s.heading == "Education")
    assert "Saint Peter" in edu.content
    assert "YCCE" in edu.content
    exp = next(s for s in got.sections if s.heading == "Experience")
    assert "PMG" in exp.content
    assert "Alli" in exp.content


def test_parsed_resume_profile_summary_skills_experience_loose_shape() -> None:
    raw = {
        "Profile": {
            "Name": "Jane Doe",
            "Title": "Senior Engineer",
            "Contact Information": "NY • +1-555-0100 • j@ex.com",
        },
        "Summary": {
            "blurb": "Backend engineer with 10+ years in distributed systems.",
        },
        "Skills": {
            "Languages": "Java, Kotlin",
            "Cloud": "GCP, Kubernetes",
        },
        "Experience": [
            {
                "Employer": "HelloFresh",
                "Title": "Senior Backend Engineer",
                "Duration": "2023–2024",
                "Description": "Shipped payments.\nOwned Kafka migration.",
            }
        ],
    }
    got = ParsedResumeFields.model_validate(raw)
    headings = [s.heading for s in got.sections]
    assert "Profile" in headings
    assert "Summary" in headings
    assert "Skills" in headings
    assert "Experience" in headings
    prof = next(s for s in got.sections if s.heading == "Profile")
    assert "Jane Doe" in prof.content
    exp = next(s for s in got.sections if s.heading == "Experience")
    assert "HelloFresh" in exp.content
    assert "Kafka" in exp.content


def test_parsed_resume_heading_content_aliases() -> None:
    got = ParsedResumeFields.model_validate(
        {
            "sections": [
                {"Title": "Skills", "Body": "Python"},
            ]
        }
    )
    assert len(got.sections) == 1
    assert got.sections[0].heading == "Skills"
    assert got.sections[0].content == "Python"
