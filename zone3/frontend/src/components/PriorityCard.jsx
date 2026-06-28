// src/components/PriorityCard.jsx
const PRIORITY_CONFIG = {
  Critical:  { color: "#ef4444", bg: "rgba(239,68,68,0.1)",  border: "rgba(239,68,68,0.3)",  icon: "🚨", label: "Critical" },
  High:      { color: "#f59e0b", bg: "rgba(245,158,11,0.1)", border: "rgba(245,158,11,0.3)", icon: "⚡", label: "High" },
  Standard:  { color: "#10b981", bg: "rgba(16,185,129,0.1)", border: "rgba(16,185,129,0.3)", icon: "✅", label: "Standard" },
};

const QUEUE_TIMELINE = {
  "Critical Queue":  { steps: ["Received", "Triage ✓", "⚡ Critical Review", "Regulatory Report (7-day)"], active: 2 },
  "Expedited Queue": { steps: ["Received", "Triage ✓", "⚡ Expedited Review", "Regulatory Report (15-day)"], active: 2 },
  "Standard Queue":  { steps: ["Received", "Triage ✓", "Standard Review", "Periodic Report"], active: 2 },
};

export default function PriorityCard({ priority, queue, expedited, nextZone }) {
  const cfg = PRIORITY_CONFIG[priority] || PRIORITY_CONFIG.Standard;
  const timeline = QUEUE_TIMELINE[queue] || QUEUE_TIMELINE["Standard Queue"];

  return (
    <div className="card" style={{ marginBottom: "1.5rem" }}>
      <h4 style={{ marginBottom: "1rem" }}>🚦 Priority & Queue Assignment</h4>

      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.25rem", flexWrap: "wrap" }}>
        {/* Priority */}
        <div style={{
          flex: 1, minWidth: 140, background: cfg.bg, border: `1px solid ${cfg.border}`,
          borderRadius: "var(--radius-md)", padding: "1rem", textAlign: "center"
        }}>
          <div style={{ fontSize: "2rem" }}>{cfg.icon}</div>
          <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", marginTop: "0.25rem" }}>Priority</div>
          <div style={{ fontWeight: 800, fontSize: "1.25rem", color: cfg.color }}>{priority}</div>
        </div>

        {/* Queue */}
        <div style={{
          flex: 2, minWidth: 200, background: "var(--bg-secondary)",
          borderRadius: "var(--radius-md)", padding: "1rem"
        }}>
          <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "0.25rem" }}>Assigned Queue</div>
          <div style={{ fontWeight: 700, fontSize: "1.1rem", marginBottom: "0.5rem" }}>{queue}</div>
          <div style={{ fontSize: "0.8rem", display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <span style={{ color: "var(--text-muted)" }}>Next Zone:</span>
            <span className="badge badge-info">{nextZone}</span>
            <span style={{ color: "var(--text-muted)" }}>Expedited:</span>
            <span className={`badge ${expedited ? "badge-danger" : "badge-success"}`}>
              {expedited ? "Yes" : "No"}
            </span>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div style={{ background: "var(--bg-secondary)", borderRadius: "var(--radius-sm)", padding: "0.75rem 1rem" }}>
        <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginBottom: "0.6rem", textTransform: "uppercase" }}>Processing Timeline</div>
        <div style={{ display: "flex", alignItems: "center", gap: "0", overflowX: "auto" }}>
          {timeline.steps.map((step, i) => (
            <div key={step} style={{ display: "flex", alignItems: "center" }}>
              <div style={{
                display: "flex", flexDirection: "column", alignItems: "center", gap: "0.25rem",
                padding: "0.25rem 0.5rem"
              }}>
                <div style={{
                  width: 28, height: 28, borderRadius: "50%",
                  background: i <= timeline.active ? cfg.color : "var(--border-color)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "0.7rem", fontWeight: 700, color: "white", flexShrink: 0
                }}>
                  {i <= timeline.active ? "✓" : i + 1}
                </div>
                <span style={{ fontSize: "0.68rem", color: i <= timeline.active ? cfg.color : "var(--text-muted)", textAlign: "center", whiteSpace: "nowrap" }}>
                  {step}
                </span>
              </div>
              {i < timeline.steps.length - 1 && (
                <div style={{ width: 24, height: 2, background: i < timeline.active ? cfg.color : "var(--border-color)", flexShrink: 0 }} />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
