from collections.abc import Iterable
from uuid import UUID

from app.domain.schemas import GeneratedSolution


class AnalysisRepository:
    async def save(self, solution: GeneratedSolution) -> GeneratedSolution:
        raise NotImplementedError

    async def get(self, solution_id: UUID) -> GeneratedSolution | None:
        raise NotImplementedError

    async def list(self) -> Iterable[GeneratedSolution]:
        raise NotImplementedError


class InMemoryAnalysisRepository(AnalysisRepository):
    def __init__(self) -> None:
        self._items: dict[UUID, GeneratedSolution] = {}

    async def save(self, solution: GeneratedSolution) -> GeneratedSolution:
        self._items[solution.solution_id] = solution
        return solution

    async def get(self, solution_id: UUID) -> GeneratedSolution | None:
        return self._items.get(solution_id)

    async def list(self) -> Iterable[GeneratedSolution]:
        return list(self._items.values())

