"""
triage_router.py
================
FastAPI router for Zone 3 Triage API.

Routes:
    POST /triage/check   → TriageResponse
    GET  /triage/health  → HealthResponse
    GET  /triage/metrics → MetricsResponse
"""

from fastapi import APIRouter, HTTPException, status

import config
from core.logger import get_logger
from core.metrics import metrics_collector
from models.request_models import TriageRequest
from models.response_models import TriageResponse, HealthResponse, MetricsResponse
from services.triage_service import TriageService

logger = get_logger(__name__)
router = APIRouter(prefix="/triage", tags=["Triage"])

# Singleton service instance
_triage_service = TriageService()


@router.post(
    "/check",
    response_model=TriageResponse,
    summary="Run Zone 3 Triage",
    description=(
        "Receives a validated non-duplicate ICSR from Zone 2 and returns a Zone 4 handoff "
        "envelope containing: triage decision (seriousness, expectedness, priority, queue) "
        "and the original case_data for downstream extraction."
    ),
)
def triage_check(request: TriageRequest) -> TriageResponse:
    logger.info("POST /triage/check | case_id=%s", request.case_id)
    try:
        return _triage_service.check(request)
    except Exception as exc:
        logger.exception("Unexpected error during triage | case_id=%s", request.case_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Triage pipeline error: {exc}",
        ) from exc


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        fallback_mode=config.FALLBACK_MODE,
        llm_model="FALLBACK (keyword classifier)" if config.FALLBACK_MODE else config.LLM_MODEL,
        pipeline_version=config.PIPELINE_VERSION,
    )


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Runtime Metrics",
)
def metrics() -> MetricsResponse:
    snap = metrics_collector.snapshot()
    return MetricsResponse(**snap)
