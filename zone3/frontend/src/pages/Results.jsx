// src/pages/Results.jsx
import { useLocation, useNavigate, Link } from "react-router-dom";
import PipelineStatus from "../components/PipelineStatus";
import SeriousnessBadge from "../components/SeriousnessBadge";
import ExpectednessBadge from "../components/ExpectednessBadge";
import PriorityCard from "../components/PriorityCard";
import ConfidenceMeter from "../components/ConfidenceMeter";
import WorkflowTransition from "../components/WorkflowTransition";
import LLMReasoningCard from "../components/LLMReasoningCard";

export default function Results() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state?.result) {
    return (
      <div className="page" style={{ textAlign: "center" }}>
        <div className="container">
          <h2>No Results Found</h2>
          <p style={{ marginBottom: "1.5rem" }}>Please submit a case first.</p>
          <Link to="/upload" className="btn btn-primary">← Back to Triage</Link>
        </div>
      </div>
    );
  }

  const r = state.result;                          // full envelope
  const t = r.triage ?? {};                         // nested triage block
  const caseData = r.case_data ?? state.incoming;  // original ICSR
  const incoming = state.incoming;                  // keep for backward compat
  const isFailed = r.workflow_state === "TRIAGE_FAILED";
  const isSerious = t.seriousness === "Serious";
  const priorityColour = t.priority === "Critical" ? "#ef4444" : t.priority === "High" ? "#f59e0b" : "#10b981";

  return (
    <div className="page animate-fade-up">
      <div className="container" style={{ maxWidth: 960 }}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.5rem", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div className="section-label">Zone 3 · Triage Result</div>
            <h2>Triage Report</h2>
            <span style={{ fontFamily: "monospace", fontSize: "0.82rem", color: "var(--text-muted)" }}>
              Case {r.case_id} · {t.llm_model} · v{t.pipeline_version} · {t.processing_time_ms}ms
            </span>
          </div>
          <button onClick={() => navigate("/upload")} className="btn btn-secondary">← Triage Another</button>
        </div>

        {/* Pipeline Status */}
        <PipelineStatus stages={t.pipeline_stages} />

        {/* Summary Banner */}
        <div className={`decision-banner ${isFailed ? "possible" : isSerious ? "duplicate" : "unique"}`} style={{ marginBottom: "1.5rem" }}>
          <div className="decision-icon">{isFailed ? "⚠️" : isSerious ? "🔴" : "🟢"}</div>
          <div style={{ flex: 1 }}>
            <div className="section-label">Triage Decision</div>
            <div style={{ fontSize: "1.5rem", fontWeight: 800, color: isFailed ? "var(--possible)" : isSerious ? "var(--duplicate)" : "var(--unique)" }}>
              {t.seriousness} — {t.priority} Priority
            </div>
            <div style={{ fontSize: "0.875rem", marginTop: "0.3rem", color: "var(--text-secondary)" }}>
              {t.queue} · {r.workflow_state} · Next: {r.next_zone}
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "0.5rem" }}>
            <span style={{ fontSize: "2.5rem", fontWeight: 800, color: priorityColour }}>{Math.round((t.confidence ?? 0) * 100)}%</span>
            <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Confidence</span>
          </div>
        </div>

        {/* Seriousness + Expectedness side by side */}
        <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
          <SeriousnessBadge seriousness={t.seriousness} criteria={t.criteria} />
          <ExpectednessBadge expectedness={t.expectedness} source={t.expectedness_source} expedited={t.expedited_required} />
        </div>

        {/* Priority Card */}
        <PriorityCard priority={t.priority} queue={t.queue} expedited={t.expedited_required} nextZone={r.next_zone} />

        {/* Workflow Transition */}
        <WorkflowTransition currentState={r.workflow_state} />

        {/* Incoming Case Summary */}
        {caseData && (
          <div className="card" style={{ marginBottom: "1.5rem" }}>
            <h4 style={{ marginBottom: "1rem" }}>📥 Incoming Case Summary</h4>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
              {[
                ["Case ID", caseData.case_id],
                ["Patient", `${caseData.patient_name}, ${caseData.age} yrs, ${caseData.gender}`],
                ["Drug", caseData.drug],
                ["Reaction", caseData.reaction],
                ["Event Date", caseData.event_date],
              ].map(([k, v]) => (
                <div key={k} style={{ display: "flex", gap: "0.5rem", fontSize: "0.85rem" }}>
                  <span style={{ color: "var(--text-muted)", minWidth: 90 }}>{k}:</span>
                  <span style={{ fontWeight: 500 }}>{v}</span>
                </div>
              ))}
              <div style={{ gridColumn: "1 / -1", display: "flex", gap: "0.5rem", fontSize: "0.85rem" }}>
                <span style={{ color: "var(--text-muted)", minWidth: 90 }}>Narrative:</span>
                <span style={{ fontStyle: "italic", color: "var(--text-secondary)" }}>"{caseData.report_text}"</span>
              </div>
            </div>
          </div>
        )}

        {/* Confidence Meter */}
        <ConfidenceMeter confidence={t.confidence} llmModel={t.llm_model} />

        {/* LLM Reasoning */}
        <LLMReasoningCard
          explanation={t.explanation}
          promptUsed={t.prompt_used}
          llmModel={t.llm_model}
          fallback={t.llm_model === "FALLBACK"}
        />

      </div>
    </div>
  );
}
