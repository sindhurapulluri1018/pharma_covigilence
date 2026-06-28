"""
response_models.py
==================
Pydantic output models for Zone 3 Triage.

Zone 4 Handoff Contract
-----------------------
TriageResponse is designed as the direct handoff to Zone 4 (Data Extraction).
It carries:
  - case_id / workflow_state / next_zone  → routing metadata
  - triage                                → nested TriageDecision block
  - case_data                             → original ICSR fields for Zone 4 use

Example response
----------------
{
  "case_id": "TEMP001",
  "workflow_state": "READY_FOR_EXTRACTION",
  "next_zone": "Zone4",
  "triage": {
    "seriousness": "Serious",
    "criteria": ["Hospitalization"],
    "expectedness": "Unexpected",
    "expectedness_source": "Mock Product Label",
    "priority": "Expedited",
    "queue": "Expedited Queue",
    "expedited_required": true,
    "confidence": 0.92,
    "explanation": "...",
    "llm_model": "FALLBACK",
    "prompt_used": "...",
    "pipeline_stages": [...],
    "pipeline_version": "1.0.0",
    "processing_time_ms": 12.4
  },
  "case_data": {
    "patient_name": "John Doe",
    "age": 45,
    ...
  }
}
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class TriageDecision(BaseModel):
    """Nested triage classification block embedded in TriageResponse."""

    # ── Seriousness ───────────────────────────────────────────────────────────
    seriousness: str = Field(
        ..., description="Serious | Non-serious (ICH E2B R3)"
    )
    criteria: list[str] = Field(
        default_factory=list,
        description="ICH criteria that triggered seriousness: Death, Hospitalization, etc.",
    )

    # ── Expectedness ──────────────────────────────────────────────────────────
    expectedness: str = Field(
        ..., description="Expected | Unexpected (from mock_labels.json)"
    )
    expectedness_source: str = Field(
        default="Mock Product Label",
        description="Source checked: Mock Label | SmPC | WHO Label | USPI",
    )

    # ── Priority routing ──────────────────────────────────────────────────────
    priority: str = Field(..., description="Critical | High | Standard")
    queue: str = Field(..., description="Critical Queue | Expedited Queue | Standard Queue")
    expedited_required: bool = Field(
        ..., description="Whether 15-day expedited reporting is required"
    )

    # ── Confidence & explanation ──────────────────────────────────────────────
    confidence: float = Field(..., ge=0.0, le=1.0, description="LLM confidence score (0.0–1.0)")
    explanation: str = Field(default="", description="LLM reasoning for the triage decision")
    prompt_used: Optional[str] = Field(
        default=None, description="Prompt sent to LLM (for audit / transparency)"
    )
    llm_model: str = Field(default="", description="LLM model used (or FALLBACK)")

    # ── Pipeline metadata ─────────────────────────────────────────────────────
    pipeline_stages: list[str] = Field(
        default_factory=lambda: [
            "Prompt Builder",
            "LLM Manager",
            "Response Parser",
            "Seriousness Service",
            "Expectedness Service",
            "Priority Router",
            "Workflow Transition",
        ]
    )
    pipeline_version: str = Field(default="1.0.0")
    processing_time_ms: float = Field(default=0.0)


class TriageResponse(BaseModel):
    """
    Full Zone 3 → Zone 4 handoff response.

    Zone 4 should read:
        response.triage.seriousness
        response.triage.expectedness
        response.triage.priority
        response.case_data  (original ICSR fields)
    """

    # ── Routing envelope ──────────────────────────────────────────────────────
    case_id: str = Field(..., description="Case identifier")
    workflow_state: str = Field(
        ..., description="Final workflow state: READY_FOR_EXTRACTION | TRIAGE_FAILED"
    )
    next_zone: str = Field(default="Zone4", description="Next processing zone")

    # ── Triage decision ───────────────────────────────────────────────────────
    triage: TriageDecision = Field(..., description="Full triage classification block")

    # ── Original case data for Zone 4 ─────────────────────────────────────────
    case_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Original ICSR fields from Zone 2, passed through for Zone 4 consumption",
    )


class HealthResponse(BaseModel):
    status: str
    fallback_mode: bool
    llm_model: str
    pipeline_version: str = "1.0.0"


class MetricsResponse(BaseModel):
    total_requests: int
    decisions: dict
    queues: dict
    performance: dict
