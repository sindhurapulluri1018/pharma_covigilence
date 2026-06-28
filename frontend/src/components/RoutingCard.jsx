// src/components/RoutingCard.jsx

const ROUTE_ICONS = {
  Stop:    "🛑",
  Hold:    "⏸️",
  Proceed: "✅",
};

const ZONE_LABELS = {
  Closed:       "🔒 Closed",
  ReviewQueue:  "👁️ Review Queue",
  Zone3:        "➡️ Zone 3 – Triage",
};

export default function RoutingCard({ routing, confidence, confidenceReason }) {
  if (!routing) return null;

  const routeIcon = ROUTE_ICONS[routing.route] || "❓";
  const zoneLabel = ZONE_LABELS[routing.next_zone] || routing.next_zone;

  const routeColour =
    routing.route === "Stop"    ? "var(--duplicate)" :
    routing.route === "Hold"    ? "var(--possible)"  :
                                  "var(--unique)";

  return (
    <div className="routing-card card">
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
        <h4 style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          🔀 Routing Decision
        </h4>
        {confidence && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "0.2rem" }}>
            <span className="badge badge-info" style={{ fontSize: "0.72rem" }}>
              Confidence: {confidence}
            </span>
            {confidenceReason && (
              <span style={{ fontSize: "0.68rem", color: "var(--text-muted)", textAlign: "right", maxWidth: "220px" }}>
                {confidenceReason}
              </span>
            )}
          </div>
        )}
      </div>

      <div
        style={{
          background: "var(--bg-secondary)",
          borderRadius: "var(--radius-md)",
          padding: "1rem 1.25rem",
          marginBottom: "1rem",
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
        }}
      >
        <span style={{ fontSize: "1.75rem" }}>{routeIcon}</span>
        <div>
          <div style={{ fontWeight: 700, color: routeColour, fontSize: "1.05rem" }}>
            {routing.next_action}
          </div>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: 2 }}>
            Next destination: {zoneLabel}
          </div>
        </div>
      </div>

      <div className="routing-grid">
        <div className="routing-item">
          <div className="routing-item-label">Next Zone</div>
          <div className="routing-item-value">{routing.next_zone}</div>
        </div>
        <div className="routing-item">
          <div className="routing-item-label">Route</div>
          <div className="routing-item-value">{routing.route}</div>
        </div>
        <div className="routing-item" style={{ gridColumn: "1 / -1" }}>
          <div className="routing-item-label">Workflow State (for Orchestrator)</div>
          <div className="routing-item-value">{routing.workflow_state}</div>
        </div>
      </div>
    </div>
  );
}
