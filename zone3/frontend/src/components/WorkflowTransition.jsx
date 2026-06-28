// src/components/WorkflowTransition.jsx
const STATES = ["READY_FOR_TRIAGE", "TRIAGE_COMPLETE", "READY_FOR_EXTRACTION"];
const FAILED_STATE = "TRIAGE_FAILED";

export default function WorkflowTransition({ currentState }) {
  const isFailed = currentState === FAILED_STATE;

  return (
    <div className="card" style={{ marginBottom: "1.5rem" }}>
      <h4 style={{ marginBottom: "1rem" }}>🔄 Workflow State Transition</h4>
      {isFailed ? (
        <div style={{
          background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
          borderRadius: "var(--radius-md)", padding: "1rem", color: "#ef4444", textAlign: "center"
        }}>
          <div style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>⚠️</div>
          <div style={{ fontWeight: 700 }}>TRIAGE_FAILED</div>
          <div style={{ fontSize: "0.8rem", marginTop: "0.25rem", opacity: 0.8 }}>
            Pipeline encountered an error. Manual intervention required.
          </div>
        </div>
      ) : (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 0, flexWrap: "wrap" }}>
          {STATES.map((state, i) => {
            const isActive = currentState === state || (i < STATES.indexOf(currentState));
            const isCurrent = currentState === state;
            return (
              <div key={state} style={{ display: "flex", alignItems: "center" }}>
                <div style={{
                  background: isActive ? "rgba(99,102,241,0.15)" : "var(--bg-secondary)",
                  border: `2px solid ${isCurrent ? "var(--accent)" : isActive ? "rgba(99,102,241,0.4)" : "var(--border-color)"}`,
                  borderRadius: "var(--radius-md)", padding: "0.5rem 0.75rem",
                  textAlign: "center", minWidth: 140
                }}>
                  <div style={{ fontSize: "0.7rem", color: isActive ? "var(--accent)" : "var(--text-muted)", marginBottom: "0.15rem", textTransform: "uppercase", letterSpacing: "0.3px" }}>
                    {i === 0 ? "Input" : i === 1 ? "Processing" : "Output"}
                  </div>
                  <div style={{ fontSize: "0.8rem", fontWeight: 700, color: isActive ? "var(--text-primary)" : "var(--text-muted)" }}>
                    {state}
                  </div>
                  {isCurrent && (
                    <div style={{ fontSize: "0.65rem", color: "var(--accent)", marginTop: "0.15rem" }}>● Current</div>
                  )}
                </div>
                {i < STATES.length - 1 && (
                  <div style={{
                    width: 32, height: 2,
                    background: STATES.indexOf(currentState) > i ? "var(--accent)" : "var(--border-color)"
                  }} />
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
