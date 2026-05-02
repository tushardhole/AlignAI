"""Chunked resume alignment (parser → section agents → merger)."""

from __future__ import annotations

import asyncio

from agents import Agent, Runner

from alignai.agents.job_brief_fields import JobBriefFields
from alignai.agents.merged_resume_fields import MergedResumeFields
from alignai.agents.parsed_resume_fields import ParsedResumeFields, ResumeSectionFields
from alignai.agents.section_aligned_fields import SectionAlignedFields
from alignai.domain.models import JobPosting


def _brief_lines(brief: JobBriefFields) -> str:
    return (
        f"Title: {brief.title}\n"
        f"Summary: {brief.summary}\n"
        f"Must-have skills: {', '.join(brief.must_have_skills)}\n"
        f"Nice-to-have skills: {', '.join(brief.nice_to_have_skills)}"
    )


class ChunkedResumeAligner:
    """Three-phase resume alignment when content exceeds the chunking threshold."""

    def __init__(self, model: str) -> None:
        self._model = model

    async def run(self, resume_text: str, jp: JobPosting, brief: JobBriefFields) -> str:
        parsed = await self._parse_resume(resume_text)
        tasks = [self._align_section(sec, jp, brief) for sec in parsed.sections]
        bodies = await asyncio.gather(*tasks)
        parts: list[tuple[str, str]] = [
            (sec.heading, body) for sec, body in zip(parsed.sections, bodies, strict=True)
        ]
        return await self._merge(parts, jp, brief)

    async def _parse_resume(self, resume_text: str) -> ParsedResumeFields:
        agent = Agent(
            name="ResumeParser",
            instructions=(
                "Split the resume into ordered sections. "
                "Headings should mirror typical resume sections."
            ),
            model=self._model,
            output_type=ParsedResumeFields,
        )
        result = await Runner.run(agent, f"Resume:\n\n{resume_text}")
        return result.final_output_as(ParsedResumeFields, raise_if_incorrect_type=True)

    async def _align_section(
        self,
        section: ResumeSectionFields,
        jp: JobPosting,
        brief: JobBriefFields,
    ) -> str:
        agent = Agent(
            name="ResumeSectionAligner",
            instructions=(
                "Rewrite only this section for the target role. "
                "Keep employers, dates, and degrees accurate."
            ),
            model=self._model,
            output_type=SectionAlignedFields,
        )
        prompt = (
            f"Section heading: {section.heading}\n"
            f"Section content:\n{section.content}\n\n"
            f"Structured brief:\n{_brief_lines(brief)}\n\n"
            f"Job description:\n{jp.description[:12000]}"
        )
        result = await Runner.run(agent, prompt)
        out = result.final_output_as(SectionAlignedFields, raise_if_incorrect_type=True)
        return out.aligned_content

    async def _merge(
        self,
        parts: list[tuple[str, str]],
        jp: JobPosting,
        brief: JobBriefFields,
    ) -> str:
        stitched = "\n\n".join(f"{h}\n{c}" for h, c in parts)
        agent = Agent(
            name="ResumeMerger",
            instructions=(
                "Integrate into one cohesive resume. Remove redundancy; never invent employers."
            ),
            model=self._model,
            output_type=MergedResumeFields,
        )
        prompt = (
            f"Draft resume:\n{stitched}\n\n"
            f"Target brief:\n{_brief_lines(brief)}\n"
            f"Posting excerpt:\n{jp.description[:4000]}"
        )
        result = await Runner.run(agent, prompt)
        merged = result.final_output_as(MergedResumeFields, raise_if_incorrect_type=True)
        return merged.content
