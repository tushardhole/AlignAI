"""Code-orchestrated multi-agent alignment using the OpenAI Agents SDK."""

from __future__ import annotations

import asyncio

from agents import set_default_openai_api, set_default_openai_client
from agents.models.default_models import get_default_model_settings
from openai import AsyncOpenAI

from alignai.agents.align_ai_agent_steps import AlignAiAgentSteps
from alignai.agents.chunked_resume_alignment import ChunkedResumeAligner
from alignai.agents.model_settings_compat import (
    json_object_instruction_suffix,
    merged_json_object_model_settings,
    use_json_object_for_structured_output,
)
from alignai.domain.models import AlignmentInputs, AlignmentResult
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
        self._json_object_structured_output = use_json_object_for_structured_output(
            llm_base_url=settings.get("llm_base_url"),
            settings_json_object_flag=settings.get("llm_json_object_mode"),
        )
        if self._json_object_structured_output:
            self._agent_model_settings = merged_json_object_model_settings()
            self._json_object_instruction_suffix = json_object_instruction_suffix()
        else:
            self._agent_model_settings = get_default_model_settings()
            self._json_object_instruction_suffix = ""
        self._steps = AlignAiAgentSteps(
            self._model,
            self._agent_model_settings,
            self._json_object_instruction_suffix,
        )

    async def run(self, inputs: AlignmentInputs) -> AlignmentResult:
        set_default_openai_client(self._client, use_for_tracing=False)
        set_default_openai_api("chat_completions")

        jp = inputs.job_posting
        brief = await self._steps.job_brief(jp)
        threshold_raw = self._settings.get("chunked_alignment_threshold")
        threshold = int(threshold_raw) if threshold_raw else _DEFAULT_CHUNK_THRESHOLD
        combined = len(inputs.resume.content) + len(jp.description)
        if combined > threshold:
            chunker = ChunkedResumeAligner(
                self._model,
                self._agent_model_settings,
                self._json_object_instruction_suffix,
            )
            resume_text = await chunker.run(inputs.resume.content, jp, brief)
        else:
            resume_text = await self._steps.single_resume(inputs.resume, jp, brief)
        cover_text = await self._steps.cover_letter(inputs.cover_letter, jp, brief)
        ats_coro = self._steps.ats_score(resume_text, cover_text, jp)
        match_coro = self._steps.match_score(resume_text, cover_text, jp)
        ats_out, match_out = await asyncio.gather(ats_coro, match_coro)
        return AlignmentResult(
            aligned_resume_content=resume_text,
            aligned_cover_letter_content=cover_text,
            ats_score=ats_out.score,
            match_score=match_out.score,
            match_label=match_out.label,
        )
