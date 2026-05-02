"""Use case: list saved alignments."""

from __future__ import annotations

from alignai.domain.models import Alignment
from alignai.domain.ports import AlignmentRepository


class ListAlignments:
    """Returns alignments newest-first."""

    def __init__(self, alignment_repository: AlignmentRepository) -> None:
        self._alignment_repository = alignment_repository

    def execute(self) -> list[Alignment]:
        return self._alignment_repository.list()
