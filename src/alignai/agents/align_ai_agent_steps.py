"""Per-step Agents SDK calls for alignment (keeps AlignAiAgentRunner class size in budget)."""

from __future__ import annotations

from agents import Agent, AgentOutputSchema, Runner
from agents.model_settings import ModelSettings

from alignai.agents.aligned_cover_letter_fields import AlignedCoverLetterFields
from alignai.agents.aligned_resume_fields import AlignedResumeFields
from alignai.agents.ats_score_fields import AtsScoreFields
from alignai.agents.job_brief_fields import JobBriefFields
from alignai.agents.match_score_fields import MatchScoreFields
from alignai.agents.structured_cover_letter_fields import StructuredCoverLetterFields
from alignai.agents.structured_resume_fields import StructuredResumeFields
from alignai.domain.models import CoverLetter, JobPosting, Resume

_JOB_POSTING_BODY_MAX_CHARS = 18_000

_RESUME_STRUCTURE_SCHEMA_HINT = (
    " Output valid JSON with these keys: "
    '"name" (string), "email" (string), "phone" (string), "location" (string), '
    '"summary" (string), '
    '"links" (array of {"url": string, "display": string}), '
    '"skills_by_category" (object: {"Category Name": ["skill1", "skill2"]}), '
    '"experience" (array of {"title": string, "company": string, "dates": string, '
    '"bullets": [string], "meta": [{"label": string, "value": string}]}), '
    '"education" (array of {"degree": string, "school": string, '
    '"location": string, "graduation_date": string}), '
    '"certifications" (array of {"name": string, "issuer": string, "date": string}), '
    '"projects" (array of {"name": string, "link": string, "url": string, "description": string}), '
    '"volunteer" (array of {"title": string, "company": string, '
    '"dates": string, "bullets": [string]}), '
    '"affiliations" (array of strings), '
    '"awards" (array of {"title": string, "description": string}), '
    '"publications" (array of {"title": string, "venue": string, "date": string}), '
    '"extra_sections" (array of {"title": string, "lines": [string]}). '
    "Omit keys for sections not present in the resume. "
    "For meta: include Tech/Tools/Specialties/Platforms lines as meta entries."
)

_COVER_LETTER_STRUCTURE_SCHEMA_HINT = (
    " Output valid JSON with exactly these keys: "
    '"candidate_name" (string — the applicant name), '
    '"paragraphs" (array of strings — body paragraphs only, '
    "no greeting like 'Dear...' and no closing like 'Regards...')."
)

_JOB_BRIEF_SHAPE_HINT = (
    " Respond with JSON using ONLY these four top-level keys: "
    '"title" (string), "summary" (string), "must_have_skills" (array of strings), '
    '"nice_to_have_skills" (array of strings). '
    "Put each skill as a quoted string inside those two arrays only. "
    'INVALID (will not parse): a nested "skills" object whose keys contain pseudo-code such as '
    "`required([` or `niceToHave([` or parentheses inside key names—never emit that. "
    'VALID example: {"title":"Engineer","summary":"...","must_have_skills":["Python","AWS"],'
    '"nice_to_have_skills":["Beego"]}. '
    "Do not output responsibilities, benefits, or education as separate large JSON arrays; "
    "compress them into summary or short skill strings. "
    "Keep must_have_skills at most 15 strings and nice_to_have_skills at most 10 "
    "so the JSON completes."
)


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
                "Extract structured facts from the job posting. "
                "Do not invent requirements not implied by the text."
                + _JOB_BRIEF_SHAPE_HINT
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
            instructions=(
                "Rewrite the resume for this job. Keep facts truthful. "
                "For each role: keep 4-6 strong bullets that are most relevant to the "
                "target job. Rephrase to highlight alignment with job requirements. "
                "Remove only truly redundant or irrelevant bullets. "
                "Preserve Tech/Tools/Stack lines for each role. "
                "Plain UTF-8 text only (no markdown fences)." + self._instruction_suffix
            ),
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
            instructions=(
                "Write a tailored cover letter in plain text. "
                "Professional tone; no Dear Hiring Manager placeholders." + self._instruction_suffix
            ),
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
            instructions=(
                "Estimate ATS compatibility using the full 1-100 scale." + self._instruction_suffix
            ),
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
            instructions=(
                "Score overall fit 1-5 and pick the closest MatchLabel enum value."
                + self._instruction_suffix
            ),
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
                "Convert this plain-text resume into structured JSON. "
                "RULES: "
                "1) Include all bullet points exactly as written — do not summarize, "
                "shorten, or omit any bullets. "
                "2) For each experience entry, if there is a line like "
                "'Tech: Python, Go' or 'Tools: Docker, K8s' or 'Stack: ...' "
                'put it in the meta array as {"label": "Tech", "value": "Python, Go"}. '
                "3) Do not modify, rephrase, or drop any content. "
                "4) Preserve the full professional summary exactly as written "
                "(multiple sentences OK). "
                "5) Open source contributions, side projects, and similar sections "
                "should go into extra_sections with each contribution as a separate line."
                + _RESUME_STRUCTURE_SCHEMA_HINT
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
                "Convert this cover letter into structured JSON. "
                "Extract the candidate name and split the body into paragraphs. "
                "Omit greeting (Dear...) and closing (Regards/Sincerely) — "
                "only include body paragraphs."
                + _COVER_LETTER_STRUCTURE_SCHEMA_HINT
                + self._instruction_suffix
            ),
            model=self._model,
            model_settings=self._agent_model_settings,
            output_type=AgentOutputSchema(StructuredCoverLetterFields, strict_json_schema=False),
        )
        result = await Runner.run(agent, f"Cover letter:\n\n{cover_text}")
        return result.final_output_as(StructuredCoverLetterFields, raise_if_incorrect_type=True)
