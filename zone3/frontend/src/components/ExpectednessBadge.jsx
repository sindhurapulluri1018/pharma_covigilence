// src/components/ExpectednessBadge.jsx
export default function ExpectednessBadge({ expectedness, source, expedited }) {
  const isUnexpected = expectedness === "Unexpected";
  return (
    <div className={`expectedness-card ${isUnexpected ? "unexpected" : "expected"}`}>
      <div className="seriousness-header">
        <span className="seriousness-icon">{isUnexpected ? "🟠" : "🔵"}</span>
        <div>
          <div className="section-label">Expectedness</div>
          <div className={`seriousness-title ${isUnexpected ? "unexpected-text" : "expected-text"}`}>
            {expectedness}
          </div>
        </div>
      </div>
      <div style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "0.4rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.82rem" }}>
          <span style={{ color: "var(--text-muted)" }}>Label source:</span>
          <span className="badge badge-info">{source || "Mock Product Label"}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.82rem" }}>
          <span style={{ color: "var(--text-muted)" }}>Expedited report required:</span>
          <span className={`badge ${expedited ? "badge-danger" : "badge-success"}`}>
            {expedited ? "Yes – 15-day report" : "No"}
          </span>
        </div>
        {isUnexpected && (
          <div style={{ fontSize: "0.77rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
            Reaction not found in approved product label. Unexpected reactions may trigger expedited reporting obligations.
          </div>
        )}
      </div>
    </div>
  );
}
