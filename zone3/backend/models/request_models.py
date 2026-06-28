"""
request_models.py
=================
Pydantic input models for Zone 3 Triage.

TriageRequest is the handoff contract from Zone 2.
Expected workflow_state: READY_FOR_TRIAGE
"""

from pydantic import BaseModel, Field, field_validator


class TriageRequest(BaseModel):
    """
    Incoming ICSR passed from Zone 2 after duplicate detection.

    workflow_state must be READY_FOR_TRIAGE (set by Zone 2 HardGate).
    """

    case_id: str = Field(..., description="Case identifier from Zone 1")
    workflow_state: str = Field(
        default="READY_FOR_TRIAGE",
        description="Workflow state from Zone 2. Must be READY_FOR_TRIAGE.",
    )
    patient_name: str = Field(..., description="Full patient name")
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    gender: str = Field(..., description="Patient gender: Male | Female | Unknown")
    drug: str = Field(..., description="Suspect drug (INN or brand name)")
    reaction: str = Field(..., description="Reported adverse reaction")
    event_date: str = Field(..., description="Date of adverse event (YYYY-MM-DD)")
    report_text: str = Field(..., description="Full case narrative")

    model_config = {
        "json_schema_extra": {
            "example": {
                "case_id": "TEMP001",
                "workflow_state": "READY_FOR_TRIAGE",
                "patient_name": "John Doe",
                "age": 45,
                "gender": "Male",
                "drug": "Paracetamol",
                "reaction": "Severe Skin Rash",
                "event_date": "2025-06-10",
                "report_text": (
                    "Patient developed severe skin rash after taking Paracetamol "
                    "and required hospitalization."
                ),
            }
        }
    }
