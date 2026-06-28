// src/components/CandidateRetrievalCard.jsx

export default function CandidateRetrievalCard({ info }) {
  if (!info) return null;

  return (
    <div className="card" style={{ marginBottom: "1.5rem" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
        <h4 style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          🔍 Stage 1 · Candidate Retrieval Funnel
        </h4>
        <span className="badge badge-info">VigiMatch Inspired</span>
      </div>

      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", 
        gap: "1.25rem", 
        background: "var(--bg-secondary)", 
        padding: "1.25rem", 
        borderRadius: "var(--radius-md)" 
      }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Database Size</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-primary)", marginTop: "0.25rem" }}>{info.database_size}</div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Total existing cases</div>
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", fontSize: "1.2rem" }}>↓</div>

        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Drug Filter</div>
          <div style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--accent)", marginTop: "0.25rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{info.drug_filter || "None"}</div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Exact / Fuzzy Match</div>
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", fontSize: "1.2rem" }}>↓</div>

        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Search Windows</div>
          <div style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)", marginTop: "0.35rem" }}>
            ±{info.age_window} yrs · ±{info.date_window_days}d
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Age & Event Date</div>
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", fontSize: "1.2rem" }}>↓</div>

        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Retrieved</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#10b981", marginTop: "0.25rem" }}>{info.candidates_retrieved}</div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Shortlisted candidates</div>
        </div>
      </div>
    </div>
  );
}
