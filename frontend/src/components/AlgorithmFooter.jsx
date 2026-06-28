// src/components/AlgorithmFooter.jsx

const ALGORITHMS = [
  {
    icon: "⚡",
    name: "RapidFuzz",
    desc: "Token-sort ratio for patient name & drug matching",
  },
  {
    icon: "🧠",
    name: "Sentence Transformers",
    desc: "Semantic embeddings for reaction & narrative similarity",
  },
  {
    icon: "📐",
    name: "Cosine Similarity",
    desc: "Vector similarity between sentence embeddings",
  },
  {
    icon: "⚖️",
    name: "Weighted Scoring",
    desc: "Field weights: Drug 25% · Reaction 25% · Narrative 20% · Patient 15% · Date 10% · Age 3% · Gender 2%",
  },
  {
    icon: "🎯",
    name: "Threshold Decision",
    desc: "Duplicate ≥ 90% · Possible Duplicate ≥ 70% · Unique Case < 70%",
  },
];

export default function AlgorithmFooter() {
  return (
    <div className="card" style={{ marginBottom: "1.5rem" }}>
      <h4 style={{ marginBottom: "1rem" }}>⚙️ Algorithms Used</h4>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
        {ALGORITHMS.map((algo) => (
          <div
            key={algo.name}
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "0.75rem",
              padding: "0.6rem 0.75rem",
              background: "var(--bg-secondary)",
              borderRadius: "var(--radius-sm)",
              borderLeft: "3px solid var(--border-accent)",
            }}
          >
            <span style={{ fontSize: "1.1rem", lineHeight: 1 }}>{algo.icon}</span>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span
                  style={{
                    fontSize: "0.78rem",
                    color: "#10b981",
                    fontWeight: 700,
                    letterSpacing: "0.3px",
                  }}
                >
                  ✓ {algo.name}
                </span>
              </div>
              <div style={{ fontSize: "0.77rem", color: "var(--text-muted)", marginTop: "0.15rem" }}>
                {algo.desc}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
