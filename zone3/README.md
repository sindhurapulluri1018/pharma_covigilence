# Zone 3 – AI-Powered Triage & Priority Routing (PharmaVigilance)

**LLM-based ICSR triage using ICH E2B(R3) criteria. Built with FastAPI + OpenAI + React.**

Receives a validated, non-duplicate ICSR from Zone 2 and classifies it by:
- **Seriousness** (ICH E2B R3 criteria)
- **Expectedness** (product label comparison)
- **Priority** (Critical / Expedited / Standard)

---

## Architecture

### Pipeline Overview

```
Incoming Case (from Zone 2 – READY_FOR_TRIAGE)
        │
        ▼
PromptBuilder       ←── ICH E2B(R3) system prompt template
        │                    + user prompt from ICSR fields
        ▼
LLMManager          ←── OpenAI gpt-4o-mini (or FallbackClassifier)
        │                    Returns JSON: seriousness · criteria · confidence
        ▼
SeriousnessClassifier   Parse + validate ICH criteria from LLM response
        │
        ▼
ExpectednessClassifier  ←── mock_labels.json (drug → known reactions)
        │                    Fuzzy match: Expected | Unexpected
        ▼
PriorityRouter      ←── config.py (deterministic rules)
        │                    Death/Life-threatening → Critical
        │                    Hospitalization/Disability/Congenital → Expedited
        │                    Otherwise → Standard
        ▼
WorkflowService     → READY_FOR_EXTRACTION (or TRIAGE_FAILED)
        │
        ▼
TriageResponse  (seriousness · expectedness · priority · queue · confidence · llm_explanation)
```

---

### Sequence Diagram

```
Client       Router         TriageService   PromptBuilder   LLMManager      SeriousnessClf  ExpectnessClf  PriorityRouter  WorkflowSvc
  │              │                 │                │               │                │               │               │               │
  │──POST /check►│                 │                │               │                │               │               │               │
  │              │──check(req)────►│                │               │                │               │               │               │
  │              │                 │──build_prompt()►│               │                │               │               │               │
  │              │                 │◄──system+user──│               │                │               │               │               │
  │              │                 │──generate(prompts)────────────►│                │               │               │               │
  │              │                 │  (OpenAI / Fallback)           │                │               │               │               │
  │              │                 │◄──JSON response────────────────│                │               │               │               │
  │              │                 │──classify(ctx)────────────────────────────────►│               │               │               │
  │              │                 │◄──seriousness+criteria─────────────────────────│               │               │               │
  │              │                 │──classify(ctx)────────────────────────────────────────────────►│               │               │
  │              │                 │◄──expectedness─────────────────────────────────────────────────│               │               │
  │              │                 │──route(ctx)──────────────────────────────────────────────────────────────────►│               │
  │              │                 │◄──priority+queue───────────────────────────────────────────────────────────────│               │
  │              │                 │──transition(ctx)───────────────────────────────────────────────────────────────────────────────►│
  │              │                 │◄──workflow_state───────────────────────────────────────────────────────────────────────────────│
  │              │◄──Response──────│                │               │                │               │               │               │
  │◄──JSON───────│                 │                │               │                │               │               │               │
```

---

### Component Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                       FastAPI Application                            │
│                                                                      │
│  ┌──────────────┐   ┌───────────────────────────────────────────┐  │
│  │ triage_      │   │           TriageService                   │  │
│  │ router.py    │──►│   (Pipeline Orchestrator)                 │  │
│  └──────────────┘   │                                           │  │
│                     │  ┌──────────────┐  ┌──────────────────┐  │  │
│                     │  │PromptBuilder │  │  SeriousnessClf  │  │  │
│                     │  │ (pure fn)    │  │  LLM parse +     │  │  │
│                     │  │ ICH E2B R3   │  │  ICH validate    │  │  │
│                     │  └──────────────┘  └──────────────────┘  │  │
│                     │                                           │  │
│                     │  ┌──────────────┐  ┌──────────────────┐  │  │
│                     │  │Expectedness  │  │  PriorityRouter  │  │  │
│                     │  │Classifier    │  │  Deterministic   │  │  │
│                     │  │fuzzy label   │  │  ICH rules       │  │  │
│                     │  │lookup        │  │  → queue/zone    │  │  │
│                     │  └──────────────┘  └──────────────────┘  │  │
│                     └───────────────────────────────────────────┘  │
│                                                                      │
│  ┌─────────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │   LLMManager        │  │ WorkflowService  │  │ MetricsCollect│  │
│  │ OpenAI Singleton    │  │ State machine    │  │ In-memory     │  │
│  │ + FallbackClassifier│  │ READY → DONE     │  │ stats         │  │
│  └─────────────────────┘  └──────────────────┘  └───────────────┘  │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────── Frontend (React + Vite) ─────────────────────┐
│  Home.jsx → UploadCase.jsx ──POST /triage/check──► Results.jsx       │
│                                                                       │
│  Components: PipelineStatus · SeriousnessBadge · ExpectednessBadge  │
│              PriorityCard · ConfidenceMeter · WorkflowTransition     │
│              LLMReasoningCard · Navbar                               │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
zone3/
  backend/
    app.py                        FastAPI entry point (port 8001)
    config.py                     OpenAI model, temperature, thresholds, routing rules
    .env                          Your OPENAI_API_KEY goes here

    core/
      logger.py                   Structured logging
      llm_manager.py              OpenAI singleton + FallbackClassifier
      metrics.py                  In-memory metrics collector

    models/
      request_models.py           TriageRequest (from Zone 2)
      response_models.py          TriageResponse + HealthResponse + MetricsResponse
      context.py                  TriageContext pipeline state object

    services/
      prompt_builder.py           ICH E2B(R3) prompt builder (pure function)
      seriousness_classifier.py   LLM → Serious / Non-serious + criteria
      expectedness_classifier.py  Mock label lookup → Expected / Unexpected
      priority_router.py          Deterministic queue routing
      workflow_service.py         READY_FOR_TRIAGE → READY_FOR_EXTRACTION
      triage_service.py           Pipeline orchestrator

    routers/
      triage_router.py            POST /triage/check · GET /health · GET /metrics

    data/
      mock_labels.json            25 drugs → known reactions (SmPC mock)

    tests/
      test_prompt_builder.py      11 tests – ICH prompt coverage
      test_seriousness_classifier.py  21 tests – all 6 ICH criteria (fallback)
      test_expectedness_classifier.py 11 tests – label lookup + fuzzy match
      test_priority_router.py     11 tests – all routing rules
      test_workflow_service.py    5 tests – state transitions

    requirements.txt

  frontend/
    src/
      config/api.js               API URL + 6 realistic sample scenarios
      pages/
        Home.jsx                  Pipeline overview + ICH criteria grid
        UploadCase.jsx            Case submission form with preloaded samples
        Results.jsx               Full triage results page
      components/
        Navbar.jsx
        PipelineStatus.jsx        ✓ Stage1 → ✓ Stage6 strip
        SeriousnessBadge.jsx      Serious/Non-serious with ICH criteria pills
        ExpectednessBadge.jsx     Expected/Unexpected with label source
        PriorityCard.jsx          Priority + Queue + processing timeline
        ConfidenceMeter.jsx       Animated confidence bar + model name
        WorkflowTransition.jsx    State machine visualizer
        LLMReasoningCard.jsx      LLM explanation + collapsible prompt viewer

  README.md
```

---

## Quick Start

### 1. Configure API Key

Edit `zone3/backend/.env`:
```
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.1
```

> **No API key?** Leave `OPENAI_API_KEY` empty — the system activates the built-in
> keyword-based fallback classifier automatically. It covers all ICH E2B(R3) criteria.

---

### 2. Backend

```bash
cd zone3/backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Mac / Linux

pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

API: http://localhost:8001  
Swagger docs: http://localhost:8001/docs

---

### 3. Frontend

```bash
cd zone3/frontend
npm install
npm run dev
```

Frontend: http://localhost:5174

---

## API Reference

### `POST /triage/check`

**Request:**
```json
{
  "case_id": "TRIAGE001",
  "workflow_state": "READY_FOR_TRIAGE",
  "patient_name": "Robert Johnson",
  "age": 72,
  "gender": "Male",
  "drug": "Warfarin",
  "reaction": "Intracranial Bleeding",
  "event_date": "2025-06-10",
  "report_text": "Patient died following massive intracranial haemorrhage on Warfarin."
}
```

**Response:**
```json
{
  "case_id": "TRIAGE001",
  "seriousness": "Serious",
  "seriousness_criteria": ["Death", "Hospitalization"],
  "expectedness": "Unexpected",
  "expectedness_source": "Mock Product Label",
  "expedited_required": true,
  "priority": "Critical",
  "queue": "Critical Queue",
  "confidence": 0.97,
  "llm_explanation": "The case describes patient death following intracranial bleeding...",
  "llm_model": "gpt-4o-mini",
  "workflow_state": "READY_FOR_EXTRACTION",
  "next_zone": "Zone4",
  "pipeline_stages": ["Prompt Builder", "LLM Classification", "Seriousness Classifier", "Expectedness Classifier", "Priority Router", "Workflow Transition"],
  "pipeline_version": "1.0.0",
  "processing_time_ms": 1243.5
}
```

### `GET /triage/health`
Returns LLM mode, fallback flag, and pipeline version.

### `GET /triage/metrics`
Returns request counts, decision distribution, queue distribution, and latency stats.

---

## Running Tests

```bash
cd zone3/backend
pytest tests/ -v
```

| Test File | Tests | Coverage | Model Required? |
|---|---|---|---|
| `test_prompt_builder.py` | 11 | ICH criteria in prompt, schema, JSON-only | ❌ No |
| `test_seriousness_classifier.py` | 21 | All 6 ICH criteria (fallback keyword path) | ❌ No |
| `test_expectedness_classifier.py` | 11 | Label lookup, fuzzy match, future hooks | ❌ No |
| `test_priority_router.py` | 11 | All routing rules, edge cases | ❌ No |
| `test_workflow_service.py` | 5 | All 3 state transitions | ❌ No |

**Total: 57 tests — all pass — no OpenAI API key required**

---

## Routing Rules (Deterministic)

| Seriousness Criterion | Priority | Queue | Expedited |
|---|---|---|---|
| Death | Critical | Critical Queue | ✅ Yes |
| Life-threatening | Critical | Critical Queue | ✅ Yes |
| Hospitalization | High | Expedited Queue | ✅ Yes |
| Disability | High | Expedited Queue | ✅ Yes |
| Congenital Anomaly | High | Expedited Queue | ✅ Yes |
| Other Medically Important | High | Expedited Queue | ✅ Yes |
| Non-serious (any) | Standard | Standard Queue | ❌ No |

---

## Workflow States

| State | Description |
|---|---|
| `READY_FOR_TRIAGE` | Input — received from Zone 2 |
| `TRIAGE_COMPLETE` | Intermediate — all stages passed |
| `READY_FOR_EXTRACTION` | Output — ready for Zone 4 |
| `TRIAGE_FAILED` | Error — LLM failure or unhandled exception |

---

## Configuration

Override via environment variables or `.env`:

```bash
OPENAI_API_KEY=sk-...           # Required for real LLM calls
LLM_MODEL=gpt-4o-mini           # OpenAI model
LLM_TEMPERATURE=0.1             # Low temperature for deterministic clinical output
LLM_MAX_TOKENS=512
CONFIDENCE_THRESHOLD=0.70       # Minimum confidence for auto-routing
```

---

## Future Extensibility

| Feature | Hook Location |
|---|---|
| WHO Drug Label | `load_from_who_label(drug)` stub in `expectedness_classifier.py` |
| SmPC Database | `load_from_smpc(drug)` stub in `expectedness_classifier.py` |
| USPI | `load_from_uspi(drug)` stub in `expectedness_classifier.py` |
| LangChain | `LLMManager` interface — swap `generate()` implementation |
| Azure OpenAI | Set `LLM_MODEL` to Azure endpoint in `config.py` |
| Ollama / Local LLM | Implement `OllamaLLMManager(LLMManager)` |
| Zone 4 API | `workflow_state = READY_FOR_EXTRACTION` is the handoff |
| Person 6 Orchestrator | `workflow_state` in every `TriageResponse` |
| MedDRA | Pass `reaction` to Zone 5 for coding |
| Prometheus Metrics | Replace `MetricsCollector` with `prometheus_client` |

---

## Team Integration

| Team Member | Integration Point |
|---|---|
| Zone 2 (P2) | `TriageRequest` consumes Zone 2 `RoutingMetadata` output |
| Zone 4 (P3) | Cases with `READY_FOR_EXTRACTION` proceed to information extraction |
| Person 6 (Orchestrator) | `workflow_state` + `next_zone` fields in every response |
