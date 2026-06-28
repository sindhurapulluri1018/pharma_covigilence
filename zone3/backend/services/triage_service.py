"""
triage_service.py
=================
TriageService – the pipeline orchestrator for Zone 3.

Coordinates five stages using a shared TriageContext object:

    Stage 1+2+3: SeriousnessService  → Prompt Builder → LLM Manager → Response Parser
    Stage 4:     ExpectednessService  → label lookup (mock_labels.json — authoritative)
    Stage 5:     PriorityRouter       → deterministic queue routing
    Stage 6:     WorkflowService      → state transition

Each service reads from and writes to the shared TriageContext.

Output
------
Returns a TriageResponse containing:
  - case_id / workflow_state / next_zone  → routing envelope for Zone 4
  - triage                                → nested TriageDecision block
  - case_data                             → original ICSR fields passed through to Zone 4
"""

import time

import config
from core.logger import get_logger, log_triage_start, log_triage_end, log_decision
from core.metrics import metrics_collector
from models.context import TriageContext
from models.request_models import TriageRequest
from models.response_models import TriageDecision, TriageResponse
from services.seriousness_service import SeriousnessService
from services.expectedness_classifier import ExpectednessService
from services.priority_router import PriorityRouter
from services.workflow_service import WorkflowService

logger = get_logger(__name__)


class TriageService:
    """
    Orchestrates the full triage pipeline for Zone 3.

    Parameters are injected (Dependency Injection) so each stage
    can be swapped without changing this class.
    """

    def __init__(self) -> None:
        self._seriousness = SeriousnessService()
        self._expectedness = ExpectednessService()
        self._router = PriorityRouter()
        self._workflow = WorkflowService()

    def check(self, request: TriageRequest) -> TriageResponse:
        """
        Run the complete triage pipeline.

        Parameters
        ----------
        request : TriageRequest
            Validated ICSR from Zone 2 (workflow_state = READY_FOR_TRIAGE).

        Returns
        -------
        TriageResponse
            Zone 4 handoff envelope with triage decision + original case data.
        """
        start_time = time.perf_counter()
        ctx = TriageContext(incoming_case=request)

        log_triage_start(logger, request.case_id)

        try:
            # ── Stages 1+2+3: Prompt Builder + LLM + Seriousness ─────────────
            logger.info("Stages 1-3: Prompt Builder → LLM Manager → Response Parser")
            self._seriousness.classify(ctx)

            # ── Stage 4: Expectedness (label lookup — LLM not consulted) ──────
            logger.info("Stage 4: Expectedness Service (mock_labels.json)")
            self._expectedness.classify(ctx)

            # ── Stage 5: Priority Routing ─────────────────────────────────────
            logger.info("Stage 5: Priority Router")
            self._router.route(ctx)

            # ── Stage 6: Workflow Transition ──────────────────────────────────
            logger.info("Stage 6: Workflow Transition")
            self._workflow.transition(ctx, success=True)

        except Exception as exc:
            logger.exception("Pipeline error | case_id=%s | error=%s", request.case_id, exc)
            self._workflow.transition(ctx, success=False)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        ctx.processing_time_ms = elapsed_ms

        log_decision(
            logger,
            request.case_id,
            ctx.seriousness,
            ctx.priority,
            ctx.queue,
            ctx.workflow_state,
        )
        log_triage_end(logger, request.case_id, elapsed_ms)

        metrics_collector.record(
            seriousness=ctx.seriousness,
            queue=ctx.queue,
            processing_time_ms=elapsed_ms,
            llm_latency_ms=ctx.llm_latency_ms,
        )

        return self._build_response(ctx)

    @staticmethod
    def _build_response(ctx: TriageContext) -> TriageResponse:
        """
        Build the Zone 4 handoff envelope from the completed TriageContext.

        Structure
        ---------
        TriageResponse
          ├── case_id          (routing)
          ├── workflow_state   (routing)
          ├── next_zone        (routing)
          ├── triage           (TriageDecision — all classification results)
          └── case_data        (original ICSR fields for Zone 4)
        """
        triage = TriageDecision(
            seriousness=ctx.seriousness or "Non-serious",
            criteria=ctx.seriousness_criteria,
            expectedness=ctx.expectedness or "Unexpected",
            expectedness_source=ctx.expectedness_source,
            priority=ctx.priority or "Standard",
            queue=ctx.queue or "Standard Queue",
            expedited_required=ctx.expedited_required,
            confidence=ctx.confidence,
            explanation=ctx.llm_explanation,
            prompt_used=ctx.user_prompt,
            llm_model=ctx.llm_model_used,
            pipeline_stages=[
                "Prompt Builder",
                "LLM Manager",
                "Response Parser",
                "Seriousness Service",
                "Expectedness Service",
                "Priority Router",
                "Workflow Transition",
            ],
            pipeline_version=ctx.pipeline_version,
            processing_time_ms=round(ctx.processing_time_ms, 1),
        )

        # Serialise original case as a plain dict for Zone 4 consumption
        case_data = ctx.incoming_case.model_dump() if ctx.incoming_case else {}

        return TriageResponse(
            case_id=ctx.incoming_case.case_id if ctx.incoming_case else "",
            workflow_state=ctx.workflow_state,
            next_zone=ctx.next_zone,
            triage=triage,
            case_data=case_data,
        )
