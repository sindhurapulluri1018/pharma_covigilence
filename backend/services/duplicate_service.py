"""
duplicate_service.py
====================
DuplicateService – the pipeline orchestrator for Zone 2.

Coordinates the five-stage pipeline using a DuplicateContext object:

    Stage 1: CandidateRetrieval  → ctx.candidates
    Stage 2: SimilarityEngine    → ctx.best_match, ctx.field_scores, ctx.field_explanations
    Stage 3: ScoringEngine       → ctx.overall_similarity
    Stage 4: DecisionEngine      → ctx.decision, ctx.confidence
    Stage 5: HardGate            → ctx.routing

Each service reads from and writes to the shared context.
The orchestrator never contains business logic itself.

Architecture note
-----------------
DuplicateService depends on abstractions, not concretions:
  - AbstractCandidateRetriever (not JSONCandidateRetriever directly)
  - AbstractCaseRepository (not JSONCaseRepository directly)

This means swapping any implementation requires only app.py changes.
"""

import time

from core.logger import get_logger, log_pipeline_start, log_pipeline_end, log_decision
from core.metrics import metrics_collector
from core.model_manager import ModelManager
from models.context import DuplicateContext
from models.request_models import IncomingCase
from models.response_models import (
    CandidateInfo,
    CandidateRetrievalInfo,
    DuplicateCheckResponse,
    FieldScores,
    FieldExplanations as ResponseFieldExplanations,
    MatchedCaseDetail,
    RoutingMetadata as ResponseRoutingMetadata,
)
import config
from repositories.case_repository import AbstractCaseRepository
from services.candidate_retrieval import AbstractCandidateRetriever
from services.similarity_engine import SimilarityEngine
from services.scoring_engine import ScoringEngine
from services.decision_engine import DecisionEngine, HardGate

logger = get_logger(__name__)


class DuplicateService:
    """
    Orchestrates the full duplicate detection pipeline.

    Parameters
    ----------
    repository : AbstractCaseRepository
        Data access layer for existing cases.
    retriever : AbstractCandidateRetriever
        Candidate retrieval strategy.
    model_manager : ModelManager
        Singleton model manager (holds SentenceTransformer).
    """

    def __init__(
        self,
        repository: AbstractCaseRepository,
        retriever: AbstractCandidateRetriever,
        model_manager: ModelManager,
    ) -> None:
        self._repo = repository
        self._retriever = retriever
        self._similarity = SimilarityEngine(model_manager)
        self._scoring = ScoringEngine()
        self._decision = DecisionEngine()
        self._hard_gate = HardGate()

    def check(self, incoming_case: IncomingCase) -> DuplicateCheckResponse:
        """
        Run the complete duplicate detection pipeline.

        Parameters
        ----------
        incoming_case : IncomingCase
            Validated ICSR from Zone 1.

        Returns
        -------
        DuplicateCheckResponse
            Full result including decision, confidence, field scores,
            explanations, and routing metadata.
        """
        start_time = time.perf_counter()
        ctx = DuplicateContext(incoming_case=incoming_case)
        ctx.database_size = len(self._repo.get_all_cases())

        log_pipeline_start(logger, incoming_case.case_id)

        try:
            # ── Stage 1: Candidate Retrieval ──────────────────────────────
            ctx.candidates = self._retriever.retrieve(ctx)
            ctx.candidates_evaluated = len(ctx.candidates)
            logger.info(
                "Stage 1 complete | candidates=%d", ctx.candidates_evaluated
            )

            # ── Stage 2: Similarity Engine ────────────────────────────────
            best, scores, explanations, top_candidates = self._similarity.find_best_match(ctx)
            ctx.best_match = best
            ctx.field_scores = scores
            ctx.field_explanations = explanations
            ctx.top_candidates = top_candidates
            logger.info(
                "Stage 2 complete | best_match=%s",
                best.get("case_id") if best else "None",
            )

            # ── Stage 3: Scoring Engine ───────────────────────────────────
            ctx.overall_similarity = self._scoring.compute_overall(
                ctx.field_scores
            ) if ctx.field_scores else 0.0
            logger.info("Stage 3 complete | overall=%.4f", ctx.overall_similarity)

            # ── Stage 4: Decision Engine ──────────────────────────────────
            ctx.decision, ctx.confidence = self._decision.decide(ctx)
            logger.info(
                "Stage 4 complete | decision=%s | confidence=%s",
                ctx.decision,
                ctx.confidence,
            )

            # ── Stage 5: Hard Gate ────────────────────────────────────────
            ctx.routing = self._hard_gate.route(ctx)
            logger.info(
                "Stage 5 complete | workflow_state=%s", ctx.routing.workflow_state
            )

        except Exception as exc:
            logger.exception(
                "Pipeline error | case_id=%s | error=%s",
                incoming_case.case_id,
                exc,
            )
            raise

        # ── Build response ────────────────────────────────────────────────
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        log_decision(
            logger,
            incoming_case.case_id,
            ctx.decision,
            ctx.confidence,
            ctx.routing.next_action,
        )
        log_pipeline_end(logger, incoming_case.case_id, elapsed_ms)

        # Record metrics
        metrics_collector.record(
            decision=ctx.decision,
            processing_time_ms=elapsed_ms,
            candidates_evaluated=ctx.candidates_evaluated,
            overall_similarity=ctx.overall_similarity,
        )

        return self._build_response(ctx)

    def _build_response(self, ctx: DuplicateContext) -> DuplicateCheckResponse:
        """Convert the populated DuplicateContext into a Pydantic response model."""

        # Default field scores (all zeros) when no candidates exist
        default_scores = {
            "patient": 0.0, "drug": 0.0, "reaction": 0.0,
            "narrative": 0.0, "date": 0.0, "age": 0.0, "gender": 0.0,
        }
        scores = ctx.field_scores if ctx.field_scores else default_scores

        field_scores = FieldScores(
            patient=scores.get("patient", 0.0),
            drug=scores.get("drug", 0.0),
            reaction=scores.get("reaction", 0.0),
            narrative=scores.get("narrative", 0.0),
            date=scores.get("date", 0.0),
            age=scores.get("age", 0.0),
            gender=scores.get("gender", 0.0),
        )

        exp = ctx.field_explanations
        field_explanations = ResponseFieldExplanations(
            patient=exp.patient,
            drug=exp.drug,
            reaction=exp.reaction,
            narrative=exp.narrative,
            date=exp.date,
            age=exp.age,
            gender=exp.gender,
        )

        routing = ResponseRoutingMetadata(
            next_zone=ctx.routing.next_zone,
            route=ctx.routing.route,
            workflow_state=ctx.routing.workflow_state,
            next_action=ctx.routing.next_action,
        )

        matched_detail = None
        if ctx.best_match:
            matched_detail = MatchedCaseDetail(
                case_id=ctx.best_match.get("case_id", ""),
                patient_name=ctx.best_match.get("patient_name", ""),
                age=ctx.best_match.get("age", 0),
                gender=ctx.best_match.get("gender", ""),
                drug=ctx.best_match.get("drug", ""),
                reaction=ctx.best_match.get("reaction", ""),
                event_date=ctx.best_match.get("event_date", ""),
                report_text=ctx.best_match.get("report_text", ""),
            )

        # Build candidate retrieval info
        candidate_retrieval_info = CandidateRetrievalInfo(
            database_size=ctx.database_size,
            drug_filter=ctx.incoming_case.drug if ctx.incoming_case else "",
            age_window=config.CANDIDATE_AGE_WINDOW,
            date_window_days=config.CANDIDATE_DATE_WINDOW_DAYS,
            candidates_retrieved=ctx.candidates_evaluated,
        )

        # Build top candidates list
        top_candidates = [
            CandidateInfo(
                case_id=item.get("case_id", ""),
                score=item.get("score", 0.0),
                patient_name=item.get("patient_name", ""),
                drug=item.get("drug", ""),
                reaction=item.get("reaction", ""),
            )
            for item in ctx.top_candidates
        ]

        # Build confidence reason
        pct_score = round(ctx.overall_similarity * 100, 1)
        if ctx.decision == "Unique Case":
            confidence_reason = "No candidate exceeded the minimum similarity threshold (70%)."
        elif ctx.confidence == "Very High":
            confidence_reason = f"Overall similarity {pct_score}% is ≥ 95% threshold."
        elif ctx.confidence == "High":
            confidence_reason = f"Overall similarity {pct_score}% is in the 90%–94% range."
        elif ctx.confidence == "Medium":
            confidence_reason = f"Overall similarity {pct_score}% is in the 80%–89% range."
        else:
            confidence_reason = f"Overall similarity {pct_score}% is in the 70%–79% range."

        # Build decision reason bullets
        decision_reason = []
        if ctx.best_match:
            if scores.get("drug", 0.0) >= 0.9:
                decision_reason.append("Drug matched exactly or near-exactly.")
            elif scores.get("drug", 0.0) >= 0.7:
                decision_reason.append("Drug matched partially.")
            
            if scores.get("patient", 0.0) >= 0.8:
                decision_reason.append("Patient name matched highly.")
            elif scores.get("patient", 0.0) >= 0.6:
                decision_reason.append("Patient name moderately matched.")

            if scores.get("reaction", 0.0) >= 0.75:
                decision_reason.append("Adverse reaction semantically similar.")
            elif scores.get("reaction", 0.0) >= 0.5:
                decision_reason.append("Adverse reaction partially similar.")

            if scores.get("narrative", 0.0) >= 0.75:
                decision_reason.append("Narrative text highly similar.")

            decision_reason.append(f"Overall similarity score: {pct_score}%.")

            if ctx.decision == "Duplicate":
                decision_reason.append("Score meets or exceeds duplicate threshold (90%). Flagged for automated confirmation.")
            elif ctx.decision == "Possible Duplicate":
                decision_reason.append("Score is below duplicate threshold (90%) but above minimum threshold (70%). Sent to human reviewer queue.")
            else:
                decision_reason.append("Score is below minimum threshold (70%). Processed as a unique case.")
        else:
            decision_reason.append("No matching candidates found in existing database.")
            decision_reason.append("Processed as a unique case.")

        return DuplicateCheckResponse(
            incoming_case=ctx.incoming_case.case_id,
            matched_case=ctx.best_match.get("case_id") if ctx.best_match else None,
            overall_similarity=ctx.overall_similarity,
            field_scores=field_scores,
            field_explanations=field_explanations,
            decision=ctx.decision if ctx.decision else "Unique Case",
            confidence=ctx.confidence if ctx.confidence else "N/A",
            confidence_reason=confidence_reason,
            decision_reason=decision_reason,
            routing=routing,
            matched_case_detail=matched_detail,
            candidates_evaluated=ctx.candidates_evaluated,
            candidate_retrieval_info=candidate_retrieval_info,
            top_candidates=top_candidates,
            pipeline_stages=[
                "Candidate Retrieval",
                "Similarity Engine",
                "Scoring Engine",
                "Decision Engine",
                "Hard Gate",
            ],
            pipeline_version=ctx.pipeline_version,
        )
