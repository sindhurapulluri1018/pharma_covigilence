"""
context.py
==========
TriageContext – mutable pipeline state object for Zone 3.

Passed sequentially through every stage:
    PromptBuilder → LLM → SeriousnessClassifier
    → ExpectednessClassifier → PriorityRouter → WorkflowService
"""

from dataclasses import dataclass, field
from typing import Optional
from models.request_models import TriageRequest


@dataclass
class TriageContext:
    """Carries all state for a single triage pipeline run."""

    # ── Input ─────────────────────────────────────────────────────────────────
    incoming_case: TriageRequest = field(default_factory=lambda: None)  # type: ignore

    # ── Stage 1: Prompt Builder ───────────────────────────────────────────────
    system_prompt: str = ""
    user_prompt: str = ""

    # ── Stage 2: LLM ─────────────────────────────────────────────────────────
    llm_raw_response: str = ""
    llm_parsed: dict = field(default_factory=dict)
    llm_latency_ms: float = 0.0
    llm_model_used: str = ""
    fallback_used: bool = False

    # ── Stage 3: Seriousness Classifier ──────────────────────────────────────
    seriousness: str = ""
    seriousness_criteria: list[str] = field(default_factory=list)

    # ── Stage 4: Expectedness Classifier ─────────────────────────────────────
    expectedness: str = ""
    expectedness_source: str = "Mock Product Label"

    # ── Stage 5: Priority Router ──────────────────────────────────────────────
    priority: str = ""
    queue: str = ""
    expedited_required: bool = False

    # ── Stage 6: Workflow Transition ──────────────────────────────────────────
    workflow_state: str = ""
    next_zone: str = "Zone4"

    # ── Cross-cutting ─────────────────────────────────────────────────────────
    confidence: float = 0.0
    llm_explanation: str = ""
    processing_time_ms: float = 0.0
    pipeline_version: str = "1.0.0"
