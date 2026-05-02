"""Code-orchestrated multi-agent alignment using the OpenAI Agents SDK."""

from __future__ import annotations

import asyncio

from agents import Agent, Runner, set_default_openai_api, set_default_openai_client
from openai import AsyncOpenAI

from alignai.agents.aligned_cover_letter_fields import AlignedCoverLetterFields
from alignai.agents.aligned_resume_fields import AlignedResumeFields
from alignai.agents.ats_score_fields import AtsScoreFields
from alignai.agents.chunked_resume_alignment import ChunkedResumeAligner
from alignai.agents.job_brief_fields import JobBriefFields
from alignai.agents.match_score_fields import MatchScoreFields
from alignai.domain.models import AlignmentInputs, AlignmentResult, CoverLetter, JobPosting, Resume
from alignai.domain.ports import SettingsStore

_DEFAULT_CHUNK_THRESHOLD = 12000


class AlignAiAgentRunner:
    """Runs specialist agents (structured outputs) with asyncio orchestration."""

    def __init__(
        self,
        client: AsyncOpenAI,
        model: str,
        settings: SettingsStore,
    ) -> None:
        self._client = client
        self._model = model
        self._settings = settings

    async def run(self, inputs: AlignmentInputs) -> AlignmentResult:
        set_default_openai_client(self._client, use_for_tracing=False)
        set_default_openai_api("chat_completions")

        jp = inputs.job_posting
        brief = await self._run_job_brief(jp)
        threshold_raw = self._settings.get("chunked_alignment_threshold")
        threshold = int(threshold_raw) if threshold_raw else _DEFAULT_CHUNK_THRESHOLD
        combined = len(inputs.resume.content) + len(jp.description)
        if combined > threshold:
            chunker = ChunkedResumeAligner(self._model)
            resume_text = await chunker.run(inputs.resume.content, jp, brief)
        else:
            resume_text = await self._run_single_resume(inputs.resume, jp, brief)
        cover_text = await self._run_cover(inputs.cover_letter, jp, brief)
        ats_coro = self._run_ats(resume_text, cover_text, jp)
        match_coro = self._run_match(resume_text, cover_text, jp)
        ats_out, match_out = await asyncio.gather(ats_coro, match_coro)
        return AlignmentResult(
            aligned_resume_content=resume_text,
            aligned_cover_letter_content=cover_text,
            ats_score=ats_out.score,
            match_score=match_out.score,
            match_label=match_out.label,
        )

    async def _run_job_brief(self, jp: JobPosting) -> JobBriefFields:
        agent = Agent(
            name="JobAnalyst",
            instructions=(
                "Extract structured facts from the job posting. "
                "Do not invent requirements not implied by the text."
            ),
            model=self._model,
            output_type=JobBriefFields,
        )
        prompt = (
            f"Job URL or source field: {jp.url}\n"
            f"Working title hint: {jp.title}\n\n"
            f"Posting body:\n{jp.description}"
        )
        result = await Runner.run(agent, prompt)
        return result.final_output_as(JobBriefFields, raise_if_incorrect_type=True)

    async def _run_single_resume(
        self,
        resume: Resume,
        jp: JobPosting,
        brief: JobBriefFields,
    ) -> str:
        agent = Agent(
            name="ResumeAligner",
            instructions=(
                "Rewrite the resume for this job. Keep facts truthful. "
                "Plain UTF-8 text only (no markdown fences)."
            ),
            model=self._model,
            output_type=AlignedResumeFields,
        )
        brief_txt = (
            f"Title: {brief.title}\nSummary: {brief.summary}\n"
            f"Must-have: {', '.join(brief.must_have_skills)}\n"
            f"Nice-to-have: {', '.join(brief.nice_to_have_skills)}"
        )
        prompt = (
            f"Candidate resume:\n{resume.content}\n\n"
            f"Structured brief:\n{brief_txt}\n\n"
            f"Job description:\n{jp.description}"
        )
        result = await Runner.run(agent, prompt)
        out = result.final_output_as(AlignedResumeFields, raise_if_incorrect_type=True)
        return out.content

    async def _run_cover(
        self,
        cover: CoverLetter,
        jp: JobPosting,
        brief: JobBriefFields,
    ) -> str:
        agent = Agent(
            name="CoverLetterAligner",
            instructions=(
                "Write a tailored cover letter in plain text. "
                "Professional tone; no Dear Hiring Manager placeholders."
            ),
            model=self._model,
            output_type=AlignedCoverLetterFields,
        )
        brief_txt = (
            f"Title: {brief.title}\nSummary: {brief.summary}\n"
            f"Must-have: {', '.join(brief.must_have_skills)}"
        )
        prompt = (
            f"Base cover letter:\n{cover.content}\n\n"
            f"Structured brief:\n{brief_txt}\n\n"
            f"Job description:\n{jp.description}"
        )
        result = await Runner.run(agent, prompt)
        out = result.final_output_as(AlignedCoverLetterFields, raise_if_incorrect_type=True)
        return out.content

    async def _run_ats(
        self,
        resume_text: str,
        cover_text: str,
        jp: JobPosting,
    ) -> AtsScoreFields:
        agent = Agent(
            name="ATSScorer",
            instructions="Estimate ATS compatibility using the full 1-100 scale.",
            model=self._model,
            output_type=AtsScoreFields,
        )
        prompt = (
            f"Resume:\n{resume_text[:12000]}\n\n"
            f"Cover letter:\n{cover_text[:8000]}\n\n"
            f"Job:\n{jp.description[:8000]}"
        )
        result = await Runner.run(agent, prompt)
        return result.final_output_as(AtsScoreFields, raise_if_incorrect_type=True)

    async def _run_match(
        self,
        resume_text: str,
        cover_text: str,
        jp: JobPosting,
    ) -> MatchScoreFields:
        agent = Agent(
            name="MatchScorer",
            instructions=("Score overall fit 1-5 and pick the closest MatchLabel enum value."),
            model=self._model,
            output_type=MatchScoreFields,
        )
        prompt = (
            f"Resume:\n{resume_text[:12000]}\n\n"
            f"Cover letter:\n{cover_text[:8000]}\n\n"
            f"Job:\n{jp.description[:8000]}"
        )
        result = await Runner.run(agent, prompt)
        return result.final_output_as(MatchScoreFields, raise_if_incorrect_type=True)
