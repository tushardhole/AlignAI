"""Per-step Agents SDK calls for alignment (keeps AlignAiAgentRunner class size in budget)."""

from __future__ import annotations

from agents import Agent, AgentOutputSchema, Runner
from agents.model_settings import ModelSettings

from alignai.agents.aligned_cover_letter_fields import AlignedCoverLetterFields
from alignai.agents.aligned_resume_fields import AlignedResumeFields
from alignai.agents.ats_score_fields import AtsScoreFields
from alignai.agents.job_brief_fields import JobBriefFields
from alignai.agents.match_score_fields import MatchScoreFields
from alignai.agents.prompts import load_prompt, load_schema_hint
from alignai.agents.structured_cover_letter_fields import StructuredCoverLetterFields
from alignai.agents.structured_resume_fields import StructuredResumeFields
from alignai.domain.models import CoverLetter, JobPosting, Resume

_JOB_POSTING_BODY_MAX_CHARS = 18_000


class AlignAiAgentSteps:
    """Runs individual Agent+Runner turns used by AlignAiAgentRunner."""

    def __init__(
        self,
        model: str,
        agent_model_settings: ModelSettings,
        instruction_suffix: str,
    ) -> None:
        self._model = model
        self._agent_model_settings = agent_model_settings
        self._instruction_suffix = instruction_suffix

    async def job_brief(self, jp: JobPosting) -> JobBriefFields:
        agent = Agent(
            name="JobAnalyst",
            instructions=(
                load_prompt("job_analyst")
                + " "
                + load_schema_hint("job_brief_shape")
                + self._instruction_suffix
            ),
            model=self._model,
            model_settings=self._agent_model_settings,
            output_type=JobBriefFields,
        )
        body = jp.description
        truncated = ""
        if len(body) > _JOB_POSTING_BODY_MAX_CHARS:
            body = body[:_JOB_POSTING_BODY_MAX_CHARS]
            truncated = "\n\n[Posting body truncated for length; use only text above.]\n"
        prompt = (
            f"Job URL or source field: {jp.url}\n"
            f"Working title hint: {jp.title}\n\n"
            f"Posting body:\n{body}{truncated}"
        )
        result = await Runner.run(agent, prompt)
        return result.final_output_as(JobBriefFields, raise_if_incorrect_type=True)

    async def single_resume(
        self,
        resume: Resume,
        jp: JobPosting,
        brief: JobBriefFields,
    ) -> str:
        agent = Agent(
            name="ResumeAligner",
            instructions=load_prompt("resume_aligner") + self._instruction_suffix,
            model=self._model,
            model_settings=self._agent_model_settings,
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

    async def cover_letter(
        self,
        cover: CoverLetter,
        jp: JobPosting,
        brief: JobBriefFields,
    ) -> str:
        agent = Agent(
            name="CoverLetterAligner",
            instructions=load_prompt("cover_letter_aligner") + self._instruction_suffix,
            model=self._model,
            model_settings=self._agent_model_settings,
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

    async def ats_score(
        self,
        resume_text: str,
        cover_text: str,
        jp: JobPosting,
    ) -> AtsScoreFields:
        agent = Agent(
            name="ATSScorer",
            instructions=load_prompt("ats_scorer") + self._instruction_suffix,
            model=self._model,
            model_settings=self._agent_model_settings,
            output_type=AtsScoreFields,
        )
        prompt = (
            f"Resume:\n{resume_text[:12000]}\n\n"
            f"Cover letter:\n{cover_text[:8000]}\n\n"
            f"Job:\n{jp.description[:8000]}"
        )
        result = await Runner.run(agent, prompt)
        return result.final_output_as(AtsScoreFields, raise_if_incorrect_type=True)

    async def match_score(
        self,
        resume_text: str,
        cover_text: str,
        jp: JobPosting,
    ) -> MatchScoreFields:
        agent = Agent(
            name="MatchScorer",
            instructions=load_prompt("match_scorer") + self._instruction_suffix,
            model=self._model,
            model_settings=self._agent_model_settings,
            output_type=MatchScoreFields,
        )
        prompt = (
            f"Resume:\n{resume_text[:12000]}\n\n"
            f"Cover letter:\n{cover_text[:8000]}\n\n"
            f"Job:\n{jp.description[:8000]}"
        )
        result = await Runner.run(agent, prompt)
        return result.final_output_as(MatchScoreFields, raise_if_incorrect_type=True)

    async def structure_resume(self, resume_text: str) -> StructuredResumeFields:
        agent = Agent(
            name="ResumeStructurer",
            instructions=(
                load_prompt("resume_structurer")
                + " "
                + load_schema_hint("resume_structure")
                + self._instruction_suffix
            ),
            model=self._model,
            model_settings=self._agent_model_settings,
            output_type=AgentOutputSchema(StructuredResumeFields, strict_json_schema=False),
        )
        result = await Runner.run(agent, f"Resume text:\n\n{resume_text}")
        return result.final_output_as(StructuredResumeFields, raise_if_incorrect_type=True)

    async def structure_cover_letter(self, cover_text: str) -> StructuredCoverLetterFields:
        agent = Agent(
            name="CoverLetterStructurer",
            instructions=(
                load_prompt("cover_letter_structurer")
                + " "
                + load_schema_hint("cover_letter_structure")
                + self._instruction_suffix
            ),
            model=self._model,
            model_settings=self._agent_model_settings,
            output_type=AgentOutputSchema(StructuredCoverLetterFields, strict_json_schema=False),
        )
        result = await Runner.run(agent, f"Cover letter:\n\n{cover_text}")
        return result.final_output_as(StructuredCoverLetterFields, raise_if_incorrect_type=True)
