"""
request_models.py
=================
Pydantic request models for the Duplicate Detection API.

Design note
-----------
IncomingCase mirrors the output contract from Zone 1 (Person 1's module).
When Person 1's API is integrated, this model is the handoff point –
only the data-source changes, not the downstream pipeline.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class IncomingCase(BaseModel):
    """
    Represents a validated ICSR arriving from Zone 1.

    All fields are required for duplicate detection.  Optional fields
    are included for future extensibility (e.g. reporter information).
    """

    case_id: str = Field(
        ...,
        description="Unique temporary identifier assigned by Zone 1",
        example="TEMP001",
    )
    patient_name: str = Field(
        ...,
        description="Full name of the patient as reported",
        example="John Doe",
    )
    age: int = Field(
        ...,
        ge=0,
        le=120,
        description="Patient age in years at time of event",
        example=45,
    )
    gender: str = Field(
        ...,
        description="Patient gender (Male / Female / Unknown)",
        example="Male",
    )
    drug: str = Field(
        ...,
        description="Suspect drug name as reported (INN or brand name)",
        example="Paracetamol",
    )
    reaction: str = Field(
        ...,
        description="Adverse reaction / event term as reported",
        example="Severe Skin Rash",
    )
    event_date: str = Field(
        ...,
        description="Date the adverse event occurred (ISO 8601: YYYY-MM-DD)",
        example="2025-06-10",
    )
    report_text: str = Field(
        ...,
        description="Free-text narrative describing the adverse event",
        example="Patient developed severe skin rash after taking Paracetamol.",
    )

    # Optional metadata – ignored in duplicate detection, preserved for routing
    reporter_name: Optional[str] = Field(None, description="Name of the reporter")
    reporter_type: Optional[str] = Field(
        None, description="Reporter type (HCP / Consumer / Manufacturer)"
    )
    country: Optional[str] = Field(None, description="Country of occurrence")

    @field_validator("gender")
    @classmethod
    def normalise_gender(cls, v: str) -> str:
        """Normalise gender to title-case for consistent matching."""
        mapping = {"m": "Male", "f": "Female", "u": "Unknown"}
        cleaned = v.strip().lower()
        return mapping.get(cleaned, v.strip().title())

    @field_validator("event_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Ensure date is in YYYY-MM-DD format."""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("event_date must be in YYYY-MM-DD format")
        return v

    model_config = {"json_schema_extra": {
        "example": {
            "case_id": "TEMP001",
            "patient_name": "John Doe",
            "age": 45,
            "gender": "Male",
            "drug": "Paracetamol",
            "reaction": "Severe Skin Rash",
            "event_date": "2025-06-10",
            "report_text": "Patient developed severe skin rash after taking Paracetamol.",
        }
    }}
