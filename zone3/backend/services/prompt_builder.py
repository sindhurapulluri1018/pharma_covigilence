"""
prompt_builder.py
=================
Builds ICH E2B(R3)-compliant LLM prompts for triage seriousness classification.

Pure function — no I/O, fully unit-testable.

NOTE: Expectedness is NOT included in this prompt.
Expectedness is determined deterministically by ExpectednessService
using mock_labels.json as the authoritative source.
"""

from models.request_models import TriageRequest

# ---------------------------------------------------------------------------
# ICH E2B(R3) System Prompt – Seriousness ONLY
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a senior clinical pharmacovigilance expert specialised in ICH E2B(R3) adverse event triage.

Your ONLY task is to classify SERIOUSNESS of the adverse event report.
Do NOT assess expectedness — that is handled separately by the product label database.

ICH E2B(R3) Seriousness Criteria (select ALL that apply):
   - Death: Patient died as a result of the adverse event
   - Life-threatening: Patient was at immediate risk of death during the event
   - Hospitalization: Event required or prolonged hospitalisation
   - Disability: Event resulted in significant, persistent, or permanent disability/incapacity
   - Congenital Anomaly: Birth defect in offspring or foetal harm
   - Other Medically Important Condition: Event that may jeopardise the patient or require medical intervention to prevent a serious outcome

RULES:
- Return ONLY valid JSON — no markdown, no text outside the JSON object
- Be conservative: if there is ANY clear clinical evidence of hospitalisation, disability, or death, classify as Serious
- List ALL applicable criteria, not just the most severe one
- seriousness_criteria must be an empty array [] for Non-serious cases
- explanation must be 1–3 clinical sentences justifying your decision

Return exactly this JSON schema:
{
  "seriousness": "Serious" | "Non-serious",
  "seriousness_criteria": ["Death" | "Life-threatening" | "Hospitalization" | "Disability" | "Congenital Anomaly" | "Other Medically Important Condition"],
  "expedited_required": true | false,
  "confidence": 0.0-1.0,
  "explanation": "..."
}"""


def build_user_prompt(case: TriageRequest) -> str:
    """
    Build the user-facing seriousness prompt from the incoming ICSR.

    Parameters
    ----------
    case : TriageRequest
        Validated ICSR from Zone 2.

    Returns
    -------
    str
        Formatted prompt ready for LLM submission.
    """
    return f"""Classify the SERIOUSNESS of this Individual Case Safety Report (ICSR):

Case ID: {case.case_id}
Patient: {case.patient_name}, Age: {case.age}, Gender: {case.gender}
Suspect Drug: {case.drug}
Reported Adverse Reaction: {case.reaction}
Event Date: {case.event_date}

Case Narrative:
{case.report_text}

Apply ICH E2B(R3) seriousness criteria and return JSON only."""


def get_system_prompt() -> str:
    """Return the ICH E2B(R3) seriousness system prompt."""
    return SYSTEM_PROMPT
