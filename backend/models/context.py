"""
context.py
==========
DuplicateContext – the pipeline state object for Zone 2.

Design Pattern
--------------
Instead of passing individual arguments between every service:

    retrieval(case, repo) → candidates
    similarity(case, candidates, model) → scores
    scoring(scores, weights) → total
    decision(total) → verdict

We pass a single context object that each stage reads from and writes to:

    ctx = DuplicateContext(incoming_case=case)
    retrieval.run(ctx)      # adds ctx.candidates
    similarity.run(ctx)     # adds ctx.field_scores, ctx.best_match
    scoring.run(ctx)        # adds ctx.overall_similarity
    decision.run(ctx)       # adds ctx.decision, ctx.confidence
    hard_gate.run(ctx)      # adds ctx.routing

Benefits
--------
1. No long parameter lists.
2. Easy to inspect mid-pipeline for debugging.
3. New stages can read/write the context without changing existing signatures.
4. Serialisable for async/distributed pipelines (Person 6 integration).
"""

from dataclasses import dataclass, field
from typing import Optional

from models.request_models import IncomingCase


@dataclass
class FieldExplanations:
    """
    Human-readable reasons for each field similarity score.

    Returned alongside scores to make the result debuggable and auditable.
    """

    patient: str = ""
    drug: str = ""
    reaction: str = ""
    narrative: str = ""
    date: str = ""
    age: str = ""
    gender: str = ""


@dataclass
class RoutingMetadata:
    """
    Structured routing information produced by the Hard Gate.

    Designed for consumption by Person 6's Workflow Orchestrator.

    Attributes
    ----------
    next_zone : str
        Target zone for the case (e.g., "Zone3", "ReviewQueue", "Closed").
    route : str
        Routing verb: "Proceed", "Hold", "Stop".
    workflow_state : str
        Machine-readable state label for the orchestrator.
    next_action : str
        Human-readable action description.
    """

    next_zone: str = ""
    route: str = ""
    workflow_state: str = ""
    next_action: str = ""


@dataclass
class DuplicateContext:
    """
    Mutable pipeline state object – carries data through every stage of
    the duplicate detection pipeline.

    Instantiated by DuplicateService at the start of each check and
    passed sequentially through:

        CandidateRetrieval → SimilarityEngine → ScoringEngine
        → DecisionEngine → HardGate

    After all stages complete, DuplicateService reads the context to
    build the final DuplicateCheckResponse.
    """

    # ── Input (set at creation) ──────────────────────────────────────────
    incoming_case: IncomingCase = field(default_factory=lambda: None)  # type: ignore

    # ── Stage 1: Candidate Retrieval ─────────────────────────────────────
    candidates: list[dict] = field(default_factory=list)
    """Cases shortlisted for detailed comparison."""

    database_size: int = 0
    """Total number of cases in the existing case database."""

    # ── Stage 2: Similarity Engine ───────────────────────────────────────
    best_match: Optional[dict] = None
    """The single candidate with the highest overall similarity."""

    field_scores: dict[str, float] = field(default_factory=dict)
    """Per-field similarity scores from the Similarity Engine."""

    field_explanations: FieldExplanations = field(default_factory=FieldExplanations)
    """Human-readable reasons for each field score."""

    top_candidates: list[dict] = field(default_factory=list)
    """Top-3 candidates by overall score: [{'case_id': ..., 'score': ...}, ...]"""

    # ── Stage 3: Scoring Engine ──────────────────────────────────────────
    overall_similarity: float = 0.0
    """Weighted overall similarity score (0.0 – 1.0)."""

    # ── Stage 4: Decision Engine ─────────────────────────────────────────
    decision: str = ""
    """One of: 'Duplicate', 'Possible Duplicate', 'Unique Case'."""

    confidence: str = ""
    """One of: 'Very High', 'High', 'Medium', 'Low'."""

    # ── Stage 5: Hard Gate ───────────────────────────────────────────────
    routing: RoutingMetadata = field(default_factory=RoutingMetadata)
    """Structured routing metadata for the Workflow Orchestrator."""

    # ── Telemetry ────────────────────────────────────────────────────────
    candidates_evaluated: int = 0
    """Total candidates passed through the similarity engine."""

    pipeline_version: str = "1.0.0"
