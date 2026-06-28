// src/components/FieldScoreTable.jsx

const FIELD_META = {
  drug: {
    icon: "💊",
    label: "Drug",
    weight: "25%",
    weightLabel: "Highest Weight",
    algorithm: "RapidFuzz · Exact Match",
  },
  reaction: {
    icon: "⚡",
    label: "Reaction",
    weight: "25%",
    weightLabel: "Highest Weight",
    algorithm: "Sentence Transformer · Cosine",
  },
  narrative: {
    icon: "📄",
    label: "Narrative",
    weight: "20%",
    weightLabel: "High Weight",
    algorithm: "Sentence Transformer · Cosine",
  },
  patient: {
    icon: "👤",
    label: "Patient Name",
    weight: "15%",
    weightLabel: "Medium Weight",
    algorithm: "RapidFuzz · Token Sort",
  },
  date: {
    icon: "📅",
    label: "Event Date",
    weight: "10%",
    weightLabel: "Medium Weight",
    algorithm: "Exponential Decay",
  },
  age: {
    icon: "🎂",
    label: "Patient Age",
    weight: "3%",
    weightLabel: "Low Weight",
    algorithm: "Gaussian Decay",
  },
  gender: {
    icon: "⚥",
    label: "Gender",
    weight: "2%",
    weightLabel: "Low Weight",
    algorithm: "Exact Match",
  },
};

function getBarColor(score) {
  if (score >= 0.9) return "#ef4444";
  if (score >= 0.7) return "#f59e0b";
  return "#10b981";
}

export default function FieldScoreTable({ fieldScores, fieldExplanations, incomingCase, matchedCase }) {
  if (!fieldScores) return null;

  // Extract display values for Incoming vs Matched columns
  const incomingValues = {
    drug: incomingCase?.drug || "",
    reaction: incomingCase?.reaction || "",
    narrative: incomingCase?.report_text ? `"${incomingCase.report_text.slice(0, 40)}…"` : "",
    patient: incomingCase?.patient_name || "",
    date: incomingCase?.event_date || "",
    age: incomingCase?.age != null ? `${incomingCase.age} yrs` : "",
    gender: incomingCase?.gender || "",
  };

  const matchedValues = {
    drug: matchedCase?.drug || "",
    reaction: matchedCase?.reaction || "",
    narrative: matchedCase?.report_text ? `"${matchedCase.report_text.slice(0, 40)}…"` : "",
    patient: matchedCase?.patient_name || "",
    date: matchedCase?.event_date || "",
    age: matchedCase?.age != null ? `${matchedCase.age} yrs` : "",
    gender: matchedCase?.gender || "",
  };

  return (
    <table className="field-table">
      <thead>
        <tr>
          <th>Field</th>
          <th>Incoming → Matched</th>
          <th>Score</th>
          <th style={{ minWidth: 120 }}>Similarity</th>
          <th>Weight</th>
          <th>Algorithm</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(FIELD_META).map(([key, meta]) => {
          const score = fieldScores[key] ?? 0;
          const pct = Math.round(score * 100);
          const color = getBarColor(score);
          const explanation = fieldExplanations?.[key] || "";
          const inVal = incomingValues[key];
          const matchVal = matchedValues[key];

          return (
            <tr key={key}>
              <td>
                <div className="field-name">
                  {meta.icon} {meta.label}
                </div>
                {explanation && (
                  <div className="explanation">{explanation}</div>
                )}
              </td>
              <td style={{ fontSize: "0.8rem", maxWidth: "200px" }}>
                {inVal || matchVal ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                    <span style={{ color: "var(--text-muted)" }}>
                      {inVal || <em style={{ opacity: 0.5 }}>N/A</em>}
                    </span>
                    <span style={{ color: "var(--text-muted)", fontSize: "0.7rem" }}>↓</span>
                    <span style={{ color: "var(--text-secondary)", fontWeight: 500 }}>
                      {matchVal || <em style={{ opacity: 0.5 }}>N/A</em>}
                    </span>
                  </div>
                ) : (
                  <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>—</span>
                )}
              </td>
              <td>
                <span className="field-score-value" style={{ color }}>
                  {score.toFixed(2)}
                </span>
              </td>
              <td>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <div className="score-bar-track" style={{ flex: 1, marginBottom: 0 }}>
                    <div
                      className="score-bar-fill"
                      style={{ width: `${pct}%`, background: color }}
                    />
                  </div>
                  <span style={{ fontSize: "0.75rem", color, fontWeight: 600, minWidth: 30 }}>
                    {pct}%
                  </span>
                </div>
              </td>
              <td>
                <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                  <span className="badge badge-info">{meta.weight}</span>
                  <span style={{ fontSize: "0.68rem", color: "var(--text-muted)" }}>{meta.weightLabel}</span>
                </div>
              </td>
              <td>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace" }}>
                  {meta.algorithm}
                </span>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
