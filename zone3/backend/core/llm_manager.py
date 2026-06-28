"""
llm_manager.py
==============
Singleton LLM manager for Zone 3.

Wraps the OpenAI client and provides a single `generate()` method.
If OPENAI_API_KEY is not set, activates FallbackClassifier automatically.

Design
------
- Singleton pattern (same as Zone 2 ModelManager).
- Logs prompt, raw response, and latency for every call.
- FallbackClassifier uses keyword matching — no external dependencies.
- ResponseParser validates and sanitises raw LLM dicts into typed fields.
"""

import json
import re
import time
from typing import Optional

import config
from core.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Negation helpers
# ---------------------------------------------------------------------------

# Negation words that, when found within this many tokens before a keyword,
# indicate the keyword should NOT be treated as a positive match.
_NEGATION_WORDS = frozenset({
    "not", "no", "never", "without", "neither", "nor",
    "absence", "absent", "negative", "deny", "denied",
    "denies", "ruled", "out", "exclude", "excluded",
})
_NEGATION_WINDOW = 4  # number of words to look back


def _has_keyword_without_negation(text: str, keywords: list[str]) -> bool:
    """
    Return True if ANY keyword from `keywords` appears in `text` and is NOT
    immediately preceded (within _NEGATION_WINDOW words) by a negation word.

    Parameters
    ----------
    text     : str  – lowercased input text
    keywords : list[str] – list of lowercased keyword strings to search for
    """
    words = re.split(r"\W+", text)

    for kw in keywords:
        kw_words = kw.split()  # handle multi-word keywords e.g. "cardiac arrest"
        kw_len = len(kw_words)

        # Sliding window over tokens to find keyword
        for i in range(len(words) - kw_len + 1):
            window = words[i: i + kw_len]
            if window == kw_words:
                # Check the preceding window for negation
                start = max(0, i - _NEGATION_WINDOW)
                preceding = set(words[start:i])
                if not (preceding & _NEGATION_WORDS):
                    return True

        # Also do a substring check (handles partial keywords like "hospitali")
        # but only if the keyword is NOT a full word match candidate
        if " " not in kw and kw_len == 1:
            for match in re.finditer(re.escape(kw), text):
                pos = match.start()
                # Find the word boundary position in terms of tokens
                preceding_text = text[:pos]
                preceding_tokens = re.split(r"\W+", preceding_text)
                start = max(0, len(preceding_tokens) - _NEGATION_WINDOW)
                preceding_window = set(preceding_tokens[start:])
                if not (preceding_window & _NEGATION_WORDS):
                    return True

    return False


# ---------------------------------------------------------------------------
# Fallback classifier (keyword-based, ICH E2B R3)
# ---------------------------------------------------------------------------

class FallbackClassifier:
    """
    Deterministic keyword-based triage classifier.

    Activates when OPENAI_API_KEY is not configured.
    Covers all ICH E2B(R3) seriousness criteria via text pattern matching.

    Negation-aware: "patient was not hospitalized" does NOT trigger Hospitalization.
    """

    DEATH_KEYWORDS = [
        "death", "died", "fatal", "deceased", "fatality", "passed away", "expire",
    ]
    LIFE_THREATENING_KEYWORDS = [
        "life-threatening", "life threatening", "lifethreatening",
        "critical condition", "intensive care", "icu", "ventilator",
        "cardiac arrest", "respiratory arrest", "anaphylactic shock",
    ]
    HOSPITALIZATION_KEYWORDS = [
        "hospitali", "admitted", "admission", "inpatient", "emergency room",
        "er visit", "a&e", "required hospital", "hospital stay",
    ]
    DISABILITY_KEYWORDS = [
        "disab", "paralys", "paralyz", "permanent damage", "permanent impairment",
        "loss of function", "permanent", "irreversible damage",
    ]
    CONGENITAL_KEYWORDS = [
        "birth defect", "congenital", "fetal", "foetal", "neonatal",
        "malformation", "teratogen",
    ]
    MEDICALLY_IMPORTANT_KEYWORDS = [
        "medically important", "drug abuse", "drug dependence", "drug misuse",
        "overdose", "cancer", "tumour", "tumor",
    ]

    def classify(self, text: str) -> dict:
        t = text.lower()
        criteria = []

        if _has_keyword_without_negation(t, self.DEATH_KEYWORDS):
            criteria.append("Death")
        if _has_keyword_without_negation(t, self.LIFE_THREATENING_KEYWORDS):
            criteria.append("Life-threatening")
        if _has_keyword_without_negation(t, self.HOSPITALIZATION_KEYWORDS):
            criteria.append("Hospitalization")
        if _has_keyword_without_negation(t, self.DISABILITY_KEYWORDS):
            criteria.append("Disability")
        if _has_keyword_without_negation(t, self.CONGENITAL_KEYWORDS):
            criteria.append("Congenital Anomaly")
        if _has_keyword_without_negation(t, self.MEDICALLY_IMPORTANT_KEYWORDS):
            criteria.append("Other Medically Important Condition")

        is_serious = len(criteria) > 0
        confidence = 0.85 if is_serious else 0.80

        return {
            "seriousness": "Serious" if is_serious else "Non-serious",
            "seriousness_criteria": criteria,
            "expedited_required": is_serious,
            "confidence": confidence,
            "explanation": (
                f"Fallback keyword classifier identified: {', '.join(criteria)}. "
                if is_serious
                else "No ICH seriousness criteria keywords detected. Classified as Non-serious."
            ),
        }


# ---------------------------------------------------------------------------
# Response Parser
# ---------------------------------------------------------------------------

class ResponseParser:
    """
    Validates and sanitises the raw LLM dict output into typed seriousness fields.

    This class is intentionally stateless and contains only static methods so
    it can be used independently of the LLM call path (e.g., in unit tests).

    Design note
    -----------
    Expectedness is intentionally absent from this parser.
    Expectedness is determined deterministically by ExpectednessService using
    mock_labels.json — the LLM is never consulted for it.
    """

    VALID_CRITERIA: frozenset[str] = frozenset({
        "Death",
        "Life-threatening",
        "Hospitalization",
        "Disability",
        "Congenital Anomaly",
        "Other Medically Important Condition",
    })

    @staticmethod
    def parse_seriousness(parsed: dict) -> tuple[str, list[str], float, str]:
        """
        Extract and validate seriousness fields from a raw LLM response dict.

        Parameters
        ----------
        parsed : dict
            Raw JSON dict from the LLM or FallbackClassifier.

        Returns
        -------
        tuple[str, list[str], float, str]
            (seriousness, seriousness_criteria, confidence, explanation)
        """
        seriousness = parsed.get("seriousness", "Non-serious")
        if seriousness not in ("Serious", "Non-serious"):
            seriousness = "Non-serious"

        raw_criteria = parsed.get("seriousness_criteria", [])
        criteria = [c for c in raw_criteria if c in ResponseParser.VALID_CRITERIA]

        # If LLM says Serious but gave no valid criteria, add catch-all
        if seriousness == "Serious" and not criteria:
            criteria = ["Other Medically Important Condition"]

        confidence = float(parsed.get("confidence", 0.75))
        confidence = min(1.0, max(0.0, confidence))

        explanation = parsed.get("explanation", "")

        return seriousness, criteria, confidence, explanation


# ---------------------------------------------------------------------------
# LLM Manager (OpenAI)
# ---------------------------------------------------------------------------

class LLMManager:
    """
    Singleton manager for LLM calls.

    Usage
    -----
    manager = LLMManager.get_instance()
    result = manager.generate(system_prompt, user_prompt)
    """

    _instance: Optional["LLMManager"] = None

    def __init__(self) -> None:
        self.fallback_mode = config.FALLBACK_MODE
        self.model = config.LLM_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.max_tokens = config.LLM_MAX_TOKENS
        self._client = None
        self._fallback = FallbackClassifier()

        if not self.fallback_mode:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=config.OPENAI_API_KEY)
                logger.info("LLMManager | OpenAI client initialized | model=%s", self.model)
            except Exception as e:
                logger.warning("LLMManager | OpenAI init failed (%s) – falling back", e)
                self.fallback_mode = True
        else:
            logger.info("LLMManager | FALLBACK MODE (no OPENAI_API_KEY configured)")

    @classmethod
    def get_instance(cls) -> "LLMManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def generate(self, system_prompt: str, user_prompt: str) -> tuple[dict, str, float]:
        """
        Call the LLM or fallback classifier.

        Returns
        -------
        tuple[dict, str, float]
            (parsed_result, raw_response_text, latency_ms)
        """
        start = time.perf_counter()

        if self.fallback_mode:
            result = self._fallback.classify(user_prompt)
            raw = json.dumps(result)
            latency_ms = (time.perf_counter() - start) * 1000
            logger.info("Fallback | latency=%.1fms | seriousness=%s", latency_ms, result["seriousness"])
            return result, raw, latency_ms

        # Real OpenAI call
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=config.LLM_TOP_P,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or "{}"
            latency_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "OpenAI | model=%s | latency=%.1fms | tokens=%d",
                self.model,
                latency_ms,
                response.usage.total_tokens if response.usage else 0,
            )
            parsed = self._parse(raw)
            return parsed, raw, latency_ms

        except Exception as exc:
            logger.warning("OpenAI call failed (%s) – using fallback", exc)
            result = self._fallback.classify(user_prompt)
            raw = json.dumps(result)
            latency_ms = (time.perf_counter() - start) * 1000
            return result, raw, latency_ms

    @staticmethod
    def _parse(raw: str) -> dict:
        """Extract JSON from LLM response (handles markdown code fences)."""
        try:
            # Strip ```json ... ``` wrappers if present
            clean = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
            return json.loads(clean)
        except json.JSONDecodeError:
            logger.warning("LLM returned non-JSON: %s", raw[:200])
            return {}
