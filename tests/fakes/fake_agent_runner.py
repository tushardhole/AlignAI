"""Fake AgentRunner for fast application-layer tests."""

from __future__ import annotations

from alignai.domain.models import AlignmentInputs, AlignmentResult, MatchLabel


class FakeAgentRunner:
    """Returns a deterministic AlignmentResult without calling remote LLMs."""

    async def run(self, inputs: AlignmentInputs) -> AlignmentResult:
        del inputs
        return AlignmentResult(
            aligned_resume_content="Aligned resume body.",
            aligned_cover_letter_content="Aligned cover letter body.",
            structured_resume={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "555-0100",
                "location": "San Francisco, CA",
                "summary": "Experienced engineer.",
                "links": [],
                "skills_by_category": {"Languages": ["Python", "Go"]},
                "experience": [
                    {
                        "title": "Engineer",
                        "company": "Acme",
                        "dates": "2020-2024",
                        "bullets": ["Built systems"],
                        "meta": [],
                    }
                ],
                "education": [{"degree": "BS CS", "school": "MIT", "graduation_date": "2020"}],
                "certifications": [],
                "projects": [],
                "projects_title": "",
                "volunteer": [],
                "affiliations": [],
                "awards": [],
                "publications": [],
                "extra_sections": [],
            },
            structured_cover_letter={
                "candidate_name": "John Doe",
                "paragraphs": ["I am interested in this role.", "I have relevant experience."],
            },
            ats_score=82,
            match_score=4,
            match_label=MatchLabel.GOOD_MATCH,
        )
