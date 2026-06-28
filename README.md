# Zone 2 – AI-Powered Duplicate Detection (PharmaVigilance)

**VigiMatch-inspired ICSR duplicate detection pipeline built with FastAPI + React.**

---

## Architecture

### Pipeline Overview

```
Incoming Case (from Zone 1)
        │
        ▼
CandidateRetrieval   ←── CaseRepository ←── existing_cases.json
        │                    (55 cases in-memory)
        ▼
 SimilarityEngine    ←── ModelManager (all-MiniLM-L6-v2)
        │                    7-field per-candidate scoring
        ▼
  ScoringEngine      ←── config.py (configurable weights)
        │                    weighted average → overall score
        ▼
  DecisionEngine     ←── config.py (thresholds: 0.90 / 0.70)
        │                    → decision + confidence + reason
        ▼
    HardGate         → RoutingMetadata (for Person 6 Orchestrator)
        │
        ▼
DuplicateCheckResponse  (top_candidates, retrieval_info, pipeline_stages…)
```

---

### Sequence Diagram

```
Client          API Router      DuplicateService   CandidateRetrieval   SimilarityEngine   ScoringEngine   DecisionEngine   HardGate
  │                │                  │                    │                    │                  │                │               │
  │──POST /check──►│                  │                    │                    │                  │                │               │
  │                │──check(case)────►│                    │                    │                  │                │               │
  │                │                  │──retrieve(ctx)────►│                    │                  │                │               │
  │                │                  │  Drug/Age/Date/     │                    │                  │                │               │
  │                │                  │  Reaction filters   │                    │                  │                │               │
  │                │                  │◄──candidates[]──────│                    │                  │                │               │
  │                │                  │──find_best_match(ctx)──────────────────►│                  │                │               │
  │                │                  │  (per candidate)    │  compute(ctx,c)──►│                  │                │               │
  │                │                  │                     │                   │──encode(texts)──►model             │               │
  │                │                  │                     │                   │◄──embeddings─────model             │               │
  │                │                  │◄──(best,scores,top3)────────────────────│                  │                │               │
  │                │                  │──compute_overall(scores)────────────────────────────────►│                │               │
  │                │                  │◄──overall_similarity────────────────────────────────────│                │               │
  │                │                  │──decide(ctx)────────────────────────────────────────────────────────────►│               │
  │                │                  │◄──(decision, confidence)────────────────────────────────────────────────│               │
  │                │                  │──route(ctx)─────────────────────────────────────────────────────────────────────────────►│
  │                │                  │◄──RoutingMetadata───────────────────────────────────────────────────────────────────────│
  │                │◄──Response───────│                    │                    │                  │                │               │
  │◄──JSON─────────│                  │                    │                    │                  │                │               │
```

---

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                           │
│                                                                       │
│  ┌─────────────┐   ┌──────────────────────────────────────────────┐ │
│  │  duplicate  │   │              DuplicateService                │ │
│  │  _router.py │──►│  (Pipeline Orchestrator)                     │ │
│  └─────────────┘   │                                              │ │
│                     │  ┌──────────────┐  ┌────────────────────┐  │ │
│                     │  │  Candidate   │  │  SimilarityEngine  │  │ │
│                     │  │  Retrieval   │  │  ┌──────────────┐  │  │ │
│                     │  │  ──────────  │  │  │ RapidFuzz    │  │  │ │
│                     │  │  Drug filter │  │  │ SentenceTfmr │  │  │ │
│                     │  │  Age window  │  │  │ Gauss / Exp  │  │  │ │
│                     │  │  Date window │  │  └──────────────┘  │  │ │
│                     │  └──────────────┘  └────────────────────┘  │ │
│                     │                                              │ │
│                     │  ┌──────────────┐  ┌────────────────────┐  │ │
│                     │  │ ScoreEngine  │  │  DecisionEngine    │  │ │
│                     │  │  Weighted    │  │  + HardGate        │  │ │
│                     │  │  Average     │  │  Threshold logic   │  │ │
│                     │  └──────────────┘  └────────────────────┘  │ │
│                     └──────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────┐   ┌──────────────┐   ┌──────────────────┐  │
│  │   CaseRepository    │   │ ModelManager │   │  MetricsCollect. │  │
│  │  (JSON / future DB) │   │  Singleton   │   │  In-memory stats │  │
│  └─────────────────────┘   └──────────────┘   └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌────────────────────────── Frontend (React) ─────────────────────────┐
│  Home.jsx → UploadCase.jsx ──POST /duplicate/check──► Results.jsx   │
│                                                                       │
│  Components: PipelineStatus · CandidateRetrievalCard                │
│              TopCandidatesTable · FieldScoreTable                   │
│              RoutingCard · SimilarityGauge · AlgorithmFooter        │
└─────────────────────────────────────────────────────────────────────┘
```

### New in upgraded architecture

| Pattern | Where |
|---|---|
| Repository Layer | `repositories/case_repository.py` |
| Singleton Model Manager | `core/model_manager.py` |
| Pluggable Retrieval Strategy | `services/candidate_retrieval.py` |
| DuplicateContext Pipeline Object | `models/context.py` |
| Structured Logging | `core/logger.py` |
| In-Memory Metrics | `core/metrics.py` |
| Confidence Levels | `DecisionEngine` → Very High / High / Medium / Low |
| Routing Metadata | `HardGate` → next_zone, route, workflow_state |
| Field Explanations | `SimilarityEngine` → per-field human-readable reasons |

---

## Folder Structure

```
backend/
  app.py                      # FastAPI entry point (composition root)
  config.py                   # All weights, thresholds, model name

  core/
    logger.py                 # Structured logging
    model_manager.py          # Singleton SentenceTransformer
    metrics.py                # In-memory metrics collector

  repositories/
    case_repository.py        # Abstract + JSON implementation

  models/
    request_models.py         # IncomingCase (Pydantic)
    response_models.py        # DuplicateCheckResponse (Pydantic)
    context.py                # DuplicateContext pipeline object

  services/
    candidate_retrieval.py    # Pluggable strategy (JSON / FAISS future)
    similarity_engine.py      # 7-field similarity + explanations
    scoring_engine.py         # Weighted scoring
    decision_engine.py        # Thresholds + confidence + Hard Gate
    duplicate_service.py      # Pipeline orchestrator

  routers/
    duplicate_router.py       # /duplicate/check, /health, /metrics

  utils/
    text_utils.py             # Text cleaning, WHO-DD stub, MedDRA stub
    date_utils.py             # Date proximity scoring

  data/
    existing_cases.json       # 55 pharmacovigilance cases
    incoming_cases.json       # 5 test scenarios

  tests/
    test_scoring_engine.py    # Unit tests – ScoringEngine (no model needed)
    test_decision_engine.py   # Unit tests – DecisionEngine + HardGate
    test_similarity_engine.py # Unit tests – all 7 field methods (mocked model)

  requirements.txt

frontend/
  src/
    config/api.js             # API URL + sample cases
    pages/Home.jsx            # Landing page with pipeline diagram
    pages/UploadCase.jsx      # Case submission form
    pages/Results.jsx         # Full results page with all panels
    components/
      Navbar.jsx
      DecisionBadge.jsx
      SimilarityGauge.jsx        # Animated SVG ring gauge
      FieldScoreTable.jsx        # 7-field table: score · bar · algo · weight
      RoutingCard.jsx            # Routing metadata with confidence reason
      PipelineStatus.jsx         # ✓ Stage1 → ✓ Stage5 strip
      CandidateRetrievalCard.jsx # DB size → filter → candidates funnel
      TopCandidatesTable.jsx     # Ranked top-3 candidates with scores
      AlgorithmFooter.jsx        # Algorithm transparency card

README.md
```

---

## Quick Start

### 1. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac / Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

> **Note:** The first run downloads `all-MiniLM-L6-v2` (~90MB). This is cached locally afterwards.

API available at: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

---

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: http://localhost:5173

---

## API Reference

### `POST /duplicate/check`

**Request body:**
```json
{
  "case_id": "TEMP001",
  "patient_name": "John Doe",
  "age": 45,
  "gender": "Male",
  "drug": "Paracetamol",
  "reaction": "Severe Skin Rash",
  "event_date": "2025-06-10",
  "report_text": "Patient developed severe skin rash after taking Paracetamol."
}
```

**Response:**
```json
{
  "incoming_case": "TEMP001",
  "matched_case": "CASE001",
  "overall_similarity": 0.93,
  "field_scores": {
    "patient": 1.0, "drug": 1.0, "reaction": 0.91,
    "narrative": 0.89, "date": 0.98, "age": 0.97, "gender": 1.0
  },
  "field_explanations": {
    "patient": "Very high name match (100/100) – likely same patient",
    "drug": "Exact match after normalisation: 'paracetamol'",
    "reaction": "Semantic similarity 0.91 – very similar reactions (MedDRA grouping recommended)",
    "narrative": "Narrative cosine similarity 0.89 – narratives describe similar events",
    "date": "Events 2 day(s) apart → score 0.95",
    "age": "Age difference 1 years → score 0.99",
    "gender": "Exact match: Male"
  },
  "decision": "Duplicate",
  "confidence": "High",
  "routing": {
    "next_zone": "Closed",
    "route": "Stop",
    "workflow_state": "DUPLICATE_DETECTED",
    "next_action": "Stop Processing"
  },
  "candidates_evaluated": 9,
  "pipeline_version": "1.0.0"
}
```

### `GET /duplicate/health`
Returns model load status and case database size.

### `GET /duplicate/metrics`
Returns aggregated runtime statistics (request counts, decisions, processing time).

---

## Configuration

All weights, thresholds, and tuning parameters are in `backend/config.py`.

Override via environment variables:

```bash
PV_WEIGHT_DRUG=0.30           # Drug weight
PV_WEIGHT_REACTION=0.25       # Reaction weight
PV_THRESHOLD_DUPLICATE=0.90   # Duplicate threshold
PV_THRESHOLD_POSSIBLE=0.70    # Possible duplicate threshold
PV_EMBEDDING_MODEL=all-MiniLM-L6-v2
PV_CANDIDATE_AGE_WINDOW=15    # ±years
PV_CANDIDATE_DATE_WINDOW_DAYS=180
```

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

| Test File | Coverage | Model Required? |
|---|---|---|
| `test_scoring_engine.py` | Weighted scoring, edge cases | ❌ No |
| `test_decision_engine.py` | All thresholds, confidence levels, HardGate routing | ❌ No |
| `test_similarity_engine.py` | All 7 field methods, mocked semantic embeddings, full compute() | ❌ No |

All tests run offline — no SentenceTransformer download required.

---

## Decision Logic

| Similarity | Decision | Confidence | Routing |
|---|---|---|---|
| ≥ 0.95 | Duplicate | Very High | Stop · DUPLICATE_DETECTED |
| 0.90–0.94 | Duplicate | High | Stop · DUPLICATE_DETECTED |
| 0.80–0.89 | Possible Duplicate | Medium | Hold · PENDING_HUMAN_REVIEW |
| 0.70–0.79 | Possible Duplicate | Low | Hold · PENDING_HUMAN_REVIEW |
| < 0.70 | Unique Case | N/A | Proceed · READY_FOR_TRIAGE |

---

## Team Integration

| Team Member | Integration Point |
|---|---|
| Person 1 (Intake) | `IncomingCase` Pydantic model is the handoff contract |
| Person 6 (Orchestrator) | `workflow_state` field in `RoutingMetadata` |
| Person 3 (Extraction) | Cases with `READY_FOR_TRIAGE` state proceed to Zone 3 |

---

## Future Extensibility

| Feature | Hook |
|---|---|
| WHO Drug Dictionary | `normalize_drug_name()` stub in `text_utils.py` |
| MedDRA | `expand_reaction_synonyms()` stub in `text_utils.py` |
| FAISS | Implement `FAISSCandidateRetriever(AbstractCandidateRetriever)` |
| PostgreSQL | Implement `PostgresCaseRepository(AbstractCaseRepository)` |
| LLM Reranking | Post-process `SimilarityEngine` raw scores |
| Prometheus Metrics | Replace `MetricsCollector` with prometheus_client |
