// src/components/ConfidenceMeter.jsx
export default function ConfidenceMeter({ confidence, llmModel }) {
  const pct = Math.round((confidence || 0) * 100);
  const color = pct >= 85 ? "#10b981" : pct >= 70 ? "#f59e0b" : "#ef4444";
  const label = pct >= 85 ? "High Confidence" : pct >= 70 ? "Moderate Confidence" : "Low Confidence";

  return (
    <div className="card" style={{ marginBottom: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h4>🎯 Confidence Score</h4>
        <span className="badge badge-info" style={{ fontSize: "0.72rem" }}>
          {llmModel || "N/A"}
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "1.25rem", marginBottom: "0.75rem" }}>
        <div style={{ fontSize: "2.5rem", fontWeight: 800, color, minWidth: 70 }}>{pct}%</div>
        <div style={{ flex: 1 }}>
          <div style={{
            height: 12, borderRadius: 6, background: "var(--bg-secondary)",
            overflow: "hidden", marginBottom: "0.35rem"
          }}>
            <div style={{
              height: "100%", width: `${pct}%`,
              background: `linear-gradient(90deg, ${color}88, ${color})`,
              borderRadius: 6,
              transition: "width 0.8s ease"
            }} />
          </div>
          <div style={{ fontSize: "0.78rem", color, fontWeight: 600 }}>{label}</div>
        </div>
      </div>

      <div style={{ fontSize: "0.77rem", color: "var(--text-muted)", background: "var(--bg-secondary)", padding: "0.6rem 0.75rem", borderRadius: "var(--radius-sm)" }}>
        {pct >= 85
          ? "LLM classification and deterministic rules are in strong agreement."
          : pct >= 70
          ? "Moderate confidence — medical reviewer should verify the classification."
          : "Low confidence — manual review strongly recommended before routing."}
      </div>
    </div>
  );
}
