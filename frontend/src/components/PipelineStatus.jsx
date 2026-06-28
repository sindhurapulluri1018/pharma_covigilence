// src/components/PipelineStatus.jsx

export default function PipelineStatus({ stages }) {
  const defaultStages = [
    "Candidate Retrieval",
    "Similarity Engine",
    "Scoring Engine",
    "Decision Engine",
    "Hard Gate",
  ];
  
  const stageList = stages && stages.length > 0 ? stages : defaultStages;

  return (
    <div className="card" style={{ marginBottom: "1.5rem", padding: "1rem 1.25rem" }}>
      <div className="section-label" style={{ marginBottom: "0.75rem" }}>AI Pipeline Execution Status</div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "0.5rem" }}>
        {stageList.map((stage, idx) => (
          <div key={stage} style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <div style={{ 
              display: "flex", 
              alignItems: "center", 
              gap: "0.4rem", 
              background: "rgba(16, 185, 129, 0.1)", 
              border: "1px solid rgba(16, 185, 129, 0.3)", 
              color: "#10b981", 
              padding: "0.35rem 0.75rem", 
              borderRadius: "20px",
              fontSize: "0.82rem",
              fontWeight: 600
            }}>
              <span>✓</span>
              <span>{stage}</span>
            </div>
            {idx < stageList.length - 1 && (
              <span style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>→</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
