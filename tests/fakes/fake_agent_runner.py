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
            ats_score=82,
            match_score=4,
            match_label=MatchLabel.GOOD_MATCH,
        )
