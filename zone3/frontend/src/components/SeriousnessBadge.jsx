// src/components/SeriousnessBadge.jsx
const CRITERIA_ICONS = {
  "Death": "💀",
  "Life-threatening": "⚡",
  "Hospitalization": "🏥",
  "Disability": "♿",
  "Congenital Anomaly": "👶",
  "Other Medically Important Condition": "🔬",
};

export default function SeriousnessBadge({ seriousness, criteria }) {
  const isSerious = seriousness === "Serious";
  return (
    <div className={`seriousness-card ${isSerious ? "serious" : "non-serious"}`}>
      <div className="seriousness-header">
        <span className="seriousness-icon">{isSerious ? "🔴" : "🟢"}</span>
        <div>
          <div className="section-label">Seriousness (ICH E2B R3)</div>
          <div className={`seriousness-title ${isSerious ? "serious-text" : "non-serious-text"}`}>
            {seriousness}
          </div>
        </div>
      </div>
      {isSerious && criteria?.length > 0 && (
        <div className="criteria-list">
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.5rem", textTransform: "uppercase", letterSpacing: "0.5px" }}>
            Triggered Criteria
          </div>
          <div className="criteria-pills">
            {criteria.map((c) => (
              <span key={c} className="criteria-pill">
                {CRITERIA_ICONS[c] || "⚠️"} {c}
              </span>
            ))}
          </div>
        </div>
      )}
      {!isSerious && (
        <div style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginTop: "0.5rem" }}>
          No ICH E2B(R3) seriousness criteria met.
        </div>
      )}
    </div>
  );
}
