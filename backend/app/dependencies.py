from functools import lru_cache

from app.repositories.analysis_repository import AnalysisRepository, InMemoryAnalysisRepository
from app.services.document_parser import DocumentParserService
from app.services.solution_orchestrator import SolutionOrchestrator


@lru_cache
def get_repository() -> AnalysisRepository:
    return InMemoryAnalysisRepository()


@lru_cache
def get_orchestrator() -> SolutionOrchestrator:
    return SolutionOrchestrator()


@lru_cache
def get_document_parser() -> DocumentParserService:
    return DocumentParserService()

