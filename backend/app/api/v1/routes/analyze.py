from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.security import Principal, require_permissions
from app.dependencies import get_document_parser, get_orchestrator, get_repository
from app.domain.schemas import AgentAccuracyLevel, ErrorResponse, GeneratedSolution, TextAnalysisRequest
from app.repositories.analysis_repository import AnalysisRepository
from app.services.document_parser import DocumentParserService, UnsupportedDocumentError
from app.services.solution_orchestrator import SolutionOrchestrator

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post(
    "/text",
    response_model=GeneratedSolution,
    responses={400: {"model": ErrorResponse}},
)
async def analyze_text(
    request: TextAnalysisRequest,
    principal: Principal = Depends(require_permissions("documents:write")),
    orchestrator: SolutionOrchestrator = Depends(get_orchestrator),
    repository: AnalysisRepository = Depends(get_repository),
) -> GeneratedSolution:
    solution = orchestrator.generate(
        source_name=request.source_name,
        text=request.content,
        accuracy_level=request.accuracy_level,
    )
    return await repository.save(solution)


@router.post(
    "/document",
    response_model=GeneratedSolution,
    responses={400: {"model": ErrorResponse}},
)
async def analyze_document(
    file: UploadFile = File(...),
    accuracy_level: AgentAccuracyLevel = Form(AgentAccuracyLevel.BALANCED),
    principal: Principal = Depends(require_permissions("documents:write")),
    parser: DocumentParserService = Depends(get_document_parser),
    orchestrator: SolutionOrchestrator = Depends(get_orchestrator),
    repository: AnalysisRepository = Depends(get_repository),
) -> GeneratedSolution:
    try:
        text = await parser.extract_text(file)
    except UnsupportedDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if len(text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Document does not contain enough extractable text")

    solution = orchestrator.generate(
        source_name=file.filename or "uploaded-document",
        text=text,
        accuracy_level=accuracy_level,
    )
    return await repository.save(solution)


@router.get("/{solution_id}", response_model=GeneratedSolution)
async def get_solution(
    solution_id: UUID,
    principal: Principal = Depends(require_permissions("solutions:read")),
    repository: AnalysisRepository = Depends(get_repository),
) -> GeneratedSolution:
    solution = await repository.get(solution_id)
    if solution is None:
        raise HTTPException(status_code=404, detail="Solution not found")
    return solution


@router.get("", response_model=list[GeneratedSolution])
async def list_solutions(
    principal: Principal = Depends(require_permissions("solutions:read")),
    repository: AnalysisRepository = Depends(get_repository),
) -> list[GeneratedSolution]:
    return list(await repository.list())
