// src/components/TopCandidatesTable.jsx

export default function TopCandidatesTable({ topCandidates }) {
  if (!topCandidates || topCandidates.length === 0) return null;

  return (
    <div className="card" style={{ marginBottom: "1.5rem" }}>
      <h4 style={{ marginBottom: "1rem" }}>👥 Top Candidate Matches</h4>
      <table className="field-table">
        <thead>
          <tr>
            <th>Case ID</th>
            <th>Patient Name</th>
            <th>Drug</th>
            <th>Reaction</th>
            <th style={{ textAlign: "right" }}>Similarity Score</th>
          </tr>
        </thead>
        <tbody>
          {topCandidates.map((candidate, idx) => {
            const score = candidate.score;
            const pct = Math.round(score * 100);
            
            let color = "#10b981"; // Green (Unique / Low)
            if (score >= 0.9) {
              color = "#ef4444"; // Red (Duplicate)
            } else if (score >= 0.7) {
              color = "#f59e0b"; // Yellow (Possible Duplicate)
            }

            return (
              <tr key={candidate.case_id} style={{ opacity: idx === 0 ? 1 : 0.85 }}>
                <td style={{ fontWeight: 600 }}>
                  {candidate.case_id} {idx === 0 && <span className="tag" style={{ marginLeft: "0.5rem" }}>Best Match</span>}
                </td>
                <td>{candidate.patient_name || "N/A"}</td>
                <td><span className="badge badge-info">{candidate.drug || "N/A"}</span></td>
                <td style={{ fontSize: "0.85rem", color: "var(--text-secondary)", maxWidth: "200px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {candidate.reaction || "N/A"}
                </td>
                <td style={{ textAlign: "right" }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: "0.75rem" }}>
                    <div className="score-bar-track" style={{ width: "80px", marginBottom: 0 }}>
                      <div
                        className="score-bar-fill"
                        style={{ width: `${pct}%`, background: color }}
                      />
                    </div>
                    <span style={{ fontWeight: 700, color, minWidth: "45px" }}>
                      {pct}%
                    </span>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
