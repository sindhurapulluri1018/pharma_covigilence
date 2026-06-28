"""
response_models.py
==================
Pydantic response models for the Duplicate Detection API.

Updated to include:
  - FieldExplanations  (per-field human-readable reasons)
  - confidence         (Very High / High / Medium / Low)
  - confidence_reason  (WHY that confidence level was assigned)
  - decision_reason    (bullet-point explanation of the decision)
  - RoutingMetadata    (structured routing for Person 6 Orchestrator)
  - CandidateInfo      (case_id + score for top-candidate ranking)
  - CandidateRetrievalInfo (multi-stage retrieval pipeline metadata)
  - pipeline_stages    (ordered list of completed stage names)
"""

from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------------
# Field-level models
# ---------------------------------------------------------------------------

class FieldScores(BaseModel):
    """Per-field similarity scores (0.0 – 1.0) produced by the Similarity Engine."""

    patient: float = Field(..., ge=0.0, le=1.0, description="Patient name similarity")
    drug: float = Field(..., ge=0.0, le=1.0, description="Drug name similarity")
    reaction: float = Field(..., ge=0.0, le=1.0, description="Reaction / event similarity")
    narrative: float = Field(..., ge=0.0, le=1.0, description="Free-text narrative similarity")
    date: float = Field(..., ge=0.0, le=1.0, description="Event date proximity score")
    age: float = Field(..., ge=0.0, le=1.0, description="Patient age proximity score")
    gender: float = Field(..., ge=0.0, le=1.0, description="Gender match score")


class FieldExplanations(BaseModel):
    """
    Human-readable reason for each field score.

    Returned alongside FieldScores to make results auditable and
    explainable to medical reviewers.
    """

    patient: str = Field("", description="Reason for patient name score")
    drug: str = Field("", description="Reason for drug score")
    reaction: str = Field("", description="Reason for reaction score")
    narrative: str = Field("", description="Reason for narrative score")
    date: str = Field("", description="Reason for date score")
    age: str = Field("", description="Reason for age score")
    gender: str = Field("", description="Reason for gender score")


# ---------------------------------------------------------------------------
# Candidate models
# ---------------------------------------------------------------------------

class CandidateInfo(BaseModel):
    """Summary of a candidate case with its overall similarity score."""

    case_id: str = Field(..., description="Case identifier")
    score: float = Field(..., ge=0.0, le=1.0, description="Overall similarity score")
    patient_name: str = Field("", description="Patient name for display")
    drug: str = Field("", description="Drug name for display")
    reaction: str = Field("", description="Reaction for display")


class CandidateRetrievalInfo(BaseModel):
    """
    Metadata about the candidate retrieval stage.

    Shows the multi-stage filtering funnel: database → candidates.
    Makes the retrieval pipeline visible to reviewers.
    """

    database_size: int = Field(..., description="Total cases in the existing case database")
    drug_filter: str = Field(..., description="Drug name used for initial filtering")
    age_window: int = Field(..., description="Age window in years (±N)")
    date_window_days: int = Field(..., description="Date window in days (±N)")
    candidates_retrieved: int = Field(..., description="Number of candidates after filtering")


# ---------------------------------------------------------------------------
# Routing metadata
# ---------------------------------------------------------------------------

class RoutingMetadata(BaseModel):
    """
    Structured routing information from the Hard Gate.

    Designed for consumption by Person 6's Workflow Orchestrator.
    Contains both a machine-readable workflow_state and a human-readable
    next_action for display in the UI.
    """

    next_zone: str = Field(
        ..., description="Target processing zone (e.g., 'Zone3', 'ReviewQueue', 'Closed')"
    )
    route: str = Field(
        ..., description="Routing verb: 'Proceed', 'Hold', or 'Stop'"
    )
    workflow_state: str = Field(
        ...,
        description="Machine-readable state for the orchestrator (e.g., 'READY_FOR_TRIAGE')",
    )
    next_action: str = Field(
        ..., description="Human-readable action description"
    )


# ---------------------------------------------------------------------------
# Matched case detail
# ---------------------------------------------------------------------------

class MatchedCaseDetail(BaseModel):
    """Summary of the best-matching case from the existing case database."""

    case_id: str
    patient_name: str
    age: int
    gender: str
    drug: str
    reaction: str
    event_date: str
    report_text: str


# ---------------------------------------------------------------------------
# Main response
# ---------------------------------------------------------------------------

class DuplicateCheckResponse(BaseModel):
    """
    Full response from POST /duplicate/check.

    Returned after running the complete pipeline:
    Candidate Retrieval → Similarity → Scoring → Decision → Hard Gate.
    """

    incoming_case: str = Field(..., description="Case ID of the incoming ICSR")

    matched_case: Optional[str] = Field(
        None, description="Case ID of the best match (None if no candidates found)"
    )
    overall_similarity: float = Field(
        ..., ge=0.0, le=1.0, description="Weighted overall similarity score"
    )

    field_scores: FieldScores = Field(..., description="Per-field similarity breakdown")

    field_explanations: FieldExplanations = Field(
        ..., description="Human-readable reasons for each field score"
    )

    decision: str = Field(
        ..., description="One of: Duplicate | Possible Duplicate | Unique Case"
    )
    confidence: str = Field(
        ..., description="Confidence level: Very High | High | Medium | Low"
    )
    confidence_reason: str = Field(
        default="", description="Human-readable explanation of the confidence level"
    )
    decision_reason: list[str] = Field(
        default_factory=list,
        description="Bullet-point list explaining why this decision was reached"
    )

    routing: RoutingMetadata = Field(
        ..., description="Structured routing metadata for the Workflow Orchestrator"
    )

    matched_case_detail: Optional[MatchedCaseDetail] = Field(
        None, description="Full details of the matched case for display in the UI"
    )

    # ── Candidate retrieval metadata ──────────────────────────────────────
    candidates_evaluated: int = Field(
        ..., description="Number of candidate cases evaluated by the similarity engine"
    )
    candidate_retrieval_info: Optional[CandidateRetrievalInfo] = Field(
        None, description="Multi-stage retrieval funnel metadata"
    )
    top_candidates: list[CandidateInfo] = Field(
        default_factory=list,
        description="Top-3 candidate matches ranked by overall similarity score"
    )

    # ── Pipeline metadata ─────────────────────────────────────────────────
    pipeline_stages: list[str] = Field(
        default_factory=lambda: [
            "Candidate Retrieval",
            "Similarity Engine",
            "Scoring Engine",
            "Decision Engine",
            "Hard Gate",
        ],
        description="Ordered list of completed pipeline stages"
    )
    pipeline_version: str = Field(
        default="1.0.0", description="Version of the duplicate detection pipeline"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "incoming_case": "TEMP001",
                "matched_case": "CASE014",
                "overall_similarity": 0.93,
                "field_scores": {
                    "patient": 0.95,
                    "drug": 1.00,
                    "reaction": 0.91,
                    "narrative": 0.90,
                    "date": 0.98,
                    "age": 0.97,
                    "gender": 1.00,
                },
                "field_explanations": {
                    "patient": "Token-sort ratio 95/100 – likely same patient",
                    "drug": "Exact match after normalisation",
                    "reaction": "Semantic similarity 0.91 – very similar reactions",
                    "narrative": "Narrative cosine similarity 0.90",
                    "date": "Events 3 days apart",
                    "age": "Age difference 2 years",
                    "gender": "Exact match: Male",
                },
                "decision": "Duplicate",
                "confidence": "High",
                "confidence_reason": "Overall similarity ≥ 0.90 (score: 0.93)",
                "decision_reason": [
                    "Drug matched exactly.",
                    "Patient name highly similar (95/100).",
                    "Reaction semantically similar (0.91).",
                    "Narrative near-identical (0.90).",
                    "Overall score 93% — above duplicate threshold (90%).",
                ],
                "routing": {
                    "next_zone": "Closed",
                    "route": "Stop",
                    "workflow_state": "DUPLICATE_DETECTED",
                    "next_action": "Stop Processing",
                },
                "candidates_evaluated": 8,
                "candidate_retrieval_info": {
                    "database_size": 55,
                    "drug_filter": "Metformin",
                    "age_window": 15,
                    "date_window_days": 180,
                    "candidates_retrieved": 6,
                },
                "top_candidates": [
                    {"case_id": "CASE014", "score": 0.93, "patient_name": "John Doe", "drug": "Metformin", "reaction": "Lactic Acidosis"},
                    {"case_id": "CASE021", "score": 0.74, "patient_name": "Jane Smith", "drug": "Metformin", "reaction": "Acidosis"},
                    {"case_id": "CASE015", "score": 0.63, "patient_name": "Bob Jones", "drug": "Metformin", "reaction": "Nausea"},
                ],
                "pipeline_stages": [
                    "Candidate Retrieval",
                    "Similarity Engine",
                    "Scoring Engine",
                    "Decision Engine",
                    "Hard Gate",
                ],
                "pipeline_version": "1.0.0",
            }
        }
    }


# ---------------------------------------------------------------------------
# Ancillary responses
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    cases_loaded: int
    pipeline_version: str = "1.0.0"


class MetricsResponse(BaseModel):
    """Metrics snapshot response."""

    total_requests: int
    decisions: dict
    performance: dict
