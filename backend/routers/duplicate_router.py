"""
duplicate_router.py
===================
FastAPI router for Zone 2 – Duplicate Detection endpoints.

Endpoints
---------
POST /duplicate/check    – Run the full duplicate detection pipeline
GET  /duplicate/health   – Service health check
GET  /duplicate/metrics  – Runtime metrics snapshot

Dependency Injection
--------------------
The DuplicateService is built once (at startup via app.py) and injected
here.  The router never instantiates services directly, keeping it thin.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from core.logger import get_logger
from core.metrics import metrics_collector
from models.request_models import IncomingCase
from models.response_models import (
    DuplicateCheckResponse,
    HealthResponse,
    MetricsResponse,
)
from services.duplicate_service import DuplicateService

logger = get_logger(__name__)

router = APIRouter(prefix="/duplicate", tags=["Duplicate Detection"])

# Module-level service reference – set by app.py during startup
_duplicate_service: DuplicateService | None = None


def set_duplicate_service(service: DuplicateService) -> None:
    """Called by app.py during startup to inject the service."""
    global _duplicate_service
    _duplicate_service = service


def get_service() -> DuplicateService:
    """FastAPI dependency – returns the shared DuplicateService instance."""
    if _duplicate_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Duplicate detection service is not initialised.",
        )
    return _duplicate_service


# ---------------------------------------------------------------------------
# POST /duplicate/check
# ---------------------------------------------------------------------------

@router.post(
    "/check",
    response_model=DuplicateCheckResponse,
    summary="Check incoming ICSR for duplicates",
    description=(
        "Runs the full VigiMatch-inspired pipeline: Candidate Retrieval → "
        "Similarity Engine → Weighted Scoring → Decision Engine → Hard Gate."
    ),
    responses={
        200: {"description": "Duplicate check completed successfully"},
        422: {"description": "Invalid input – see field validation errors"},
        503: {"description": "Service not initialised"},
    },
)
def check_duplicate(
    case: IncomingCase,
    service: DuplicateService = Depends(get_service),
) -> DuplicateCheckResponse:
    """
    Run duplicate detection on a validated incoming ICSR.

    The incoming case is assumed to have passed Zone 1 validity checks.
    """
    logger.info("POST /duplicate/check | case_id=%s", case.case_id)
    try:
        result = service.check(case)
        return result
    except Exception as exc:
        logger.exception("Unexpected error during duplicate check: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {str(exc)}",
        )


# ---------------------------------------------------------------------------
# GET /duplicate/health
# ---------------------------------------------------------------------------

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns service status, model load state, and case database size.",
)
def health_check(
    service: DuplicateService = Depends(get_service),
) -> HealthResponse:
    from core.model_manager import model_manager

    return HealthResponse(
        status="ok",
        model_loaded=model_manager.is_loaded,
        cases_loaded=service._repo.count(),
        pipeline_version="1.0.0",
    )


# ---------------------------------------------------------------------------
# GET /duplicate/metrics
# ---------------------------------------------------------------------------

@router.get(
    "/metrics",
    summary="Runtime metrics",
    description=(
        "Returns aggregated pipeline metrics: request counts, "
        "decision breakdown, and average processing time."
    ),
)
def get_metrics() -> dict:
    """Return the current metrics snapshot (for Person 6 / dashboards)."""
    return metrics_collector.snapshot()
