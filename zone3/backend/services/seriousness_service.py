"""
seriousness_service.py
======================
Orchestrates the LLM call and parses seriousness classification into TriageContext.

ICH E2B(R3) criteria:
    Death · Life-threatening · Hospitalization · Disability
    Congenital Anomaly · Other Medically Important Condition

Pipeline stages handled here
-----------------------------
    Stage 1: Prompt Builder  → build system + user prompts
    Stage 2: LLM Manager     → call LLM (or FallbackClassifier)
    Stage 3: Response Parser → validate + sanitise LLM dict into typed fields

Note: Expectedness is NOT assessed here.
      It is determined deterministically by ExpectednessService (mock_labels.json).
"""

import config
from core.logger import get_logger
from core.llm_manager import LLMManager, ResponseParser
from models.context import TriageContext
from services.prompt_builder import build_user_prompt, get_system_prompt

logger = get_logger(__name__)


class SeriousnessService:
    """
    Stages 1–3 of the triage pipeline.

    Thin orchestrator: build prompt → call LLM → parse seriousness via ResponseParser.

    Writes to ctx
    -------------
        system_prompt, user_prompt       (Stage 1: Prompt Builder)
        llm_raw_response, llm_parsed,
        llm_latency_ms, llm_model_used,
        fallback_used                    (Stage 2: LLM Manager)
        seriousness, seriousness_criteria,
        confidence, llm_explanation      (Stage 3: Response Parser)
    """

    def __init__(self) -> None:
        self._llm = LLMManager.get_instance()

    def classify(self, ctx: TriageContext) -> None:
        """
        Build prompt → call LLM → parse seriousness into ctx.

        Parameters
        ----------
        ctx : TriageContext
            Shared pipeline state object. Modified in place.
        """
        # ── Stage 1: Prompt Builder ───────────────────────────────────────────
        ctx.system_prompt = get_system_prompt()
        ctx.user_prompt = build_user_prompt(ctx.incoming_case)

        # ── Stage 2: LLM Manager ──────────────────────────────────────────────
        parsed, raw, latency = self._llm.generate(ctx.system_prompt, ctx.user_prompt)

        ctx.llm_raw_response = raw
        ctx.llm_parsed = parsed
        ctx.llm_latency_ms = latency
        ctx.llm_model_used = "FALLBACK" if self._llm.fallback_mode else config.LLM_MODEL
        ctx.fallback_used = self._llm.fallback_mode

        # ── Stage 3: Response Parser ──────────────────────────────────────────
        (
            ctx.seriousness,
            ctx.seriousness_criteria,
            ctx.confidence,
            ctx.llm_explanation,
        ) = ResponseParser.parse_seriousness(parsed)

        logger.info(
            "Seriousness | seriousness=%s | criteria=%s | confidence=%.2f | fallback=%s",
            ctx.seriousness,
            ctx.seriousness_criteria,
            ctx.confidence,
            ctx.fallback_used,
        )
