// src/pages/Home.jsx
import { Link } from "react-router-dom";

const PIPELINE_STEPS = [
  { icon: "📥", title: "Candidate Retrieval", desc: "Filters existing cases by drug, reaction keywords, age window, and event date – reducing comparison pool to ≤20 candidates." },
  { icon: "🔬", title: "Similarity Engine", desc: "Computes per-field similarity using RapidFuzz (names), Sentence Transformers cosine (reactions & narratives), Gaussian decay (age), and date proximity." },
  { icon: "⚖️", title: "Weighted Scoring", desc: "Combines field scores using configurable weights: Drug 25%, Reaction 25%, Narrative 20%, Patient 15%, Date 10%, Age 3%, Gender 2%." },
  { icon: "🧠", title: "Decision Engine", desc: "Applies thresholds: ≥0.90 = Duplicate, 0.70–0.89 = Possible Duplicate, <0.70 = Unique Case. Returns confidence level (Very High / High / Medium / Low)." },
  { icon: "🚦", title: "Hard Gate", desc: "Pure routing function – maps decision to structured metadata: next_zone, workflow_state, and route for the Person 6 Orchestrator." },
];

const STATS = [
  { icon: "💊", value: "55+", label: "Case Database" },
  { icon: "🔍", value: "5-stage", label: "AI Pipeline" },
  { icon: "⚡", value: "<2s", label: "Avg Response" },
  { icon: "🎯", value: "7-field", label: "Comparison" },
];

export default function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="hero-gradient page" style={{ textAlign: "center", paddingTop: "6rem" }}>
        <div className="container">
          <span className="tag" style={{ marginBottom: "1.5rem", display: "inline-flex" }}>
            ⚕️ Zone 2 · VigiMatch-Inspired Architecture
          </span>
          <h1 style={{ marginBottom: "1.5rem", background: "linear-gradient(135deg, #f1f5f9 0%, #94a3b8 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            AI-Powered<br />Duplicate Detection
          </h1>
          <p style={{ fontSize: "1.1rem", maxWidth: 560, margin: "0 auto 2.5rem", color: "var(--text-secondary)" }}>
            Detect duplicate ICSRs before they enter the pharmacovigilance pipeline. 
            Powered by Sentence Transformers, RapidFuzz, and a multi-stage weighted scoring engine.
          </p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
            <Link to="/upload" className="btn btn-primary btn-lg">
              🔍 Check a Case
            </Link>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="btn btn-secondary btn-lg">
              📚 API Docs
            </a>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section style={{ padding: "3rem 0" }}>
        <div className="container">
          <div className="grid-2" style={{ gridTemplateColumns: "repeat(4, 1fr)" }}>
            {STATS.map((s) => (
              <div key={s.label} className="stat-card">
                <div className="stat-icon">{s.icon}</div>
                <div className="stat-value" style={{ color: "var(--accent)" }}>{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline */}
      <section style={{ padding: "2rem 0 4rem" }}>
        <div className="container">
          <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
            <div className="section-label">Architecture</div>
            <h2>The 5-Stage Detection Pipeline</h2>
            <p style={{ marginTop: "0.5rem" }}>Each stage is an independent, swappable service.</p>
          </div>

          <div className="card-elevated" style={{ maxWidth: 720, margin: "0 auto" }}>
            <div className="pipeline">
              {PIPELINE_STEPS.map((step, i) => (
                <div key={step.title} className="pipeline-step">
                  <div className="pipeline-connector">
                    <div className="pipeline-dot">{step.icon}</div>
                    {i < PIPELINE_STEPS.length - 1 && <div className="pipeline-line" />}
                  </div>
                  <div className="pipeline-content">
                    <h4 style={{ marginBottom: "0.25rem" }}>{step.title}</h4>
                    <p style={{ fontSize: "0.875rem" }}>{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Future integrations */}
      <section style={{ padding: "2rem 0 5rem" }}>
        <div className="container">
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <div className="section-label">Extensibility</div>
            <h2>Built for the Future</h2>
          </div>
          <div className="grid-2">
            {[
              ["🗄️ WHO Drug Dictionary", "Stub ready in text_utils.py → normalize_drug_name()"],
              ["🏥 MedDRA Coding", "Stub ready → expand_reaction_synonyms()"],
              ["⚡ FAISS Vector Search", "FAISSCandidateRetriever interface defined"],
              ["🐘 PostgreSQL / MongoDB", "Swap JSONCaseRepository only"],
              ["🤖 LLM Reranking", "SimilarityEngine returns raw scores for post-processing"],
              ["🔗 Person 6 Orchestrator", "workflow_state field in every response"],
            ].map(([title, desc]) => (
              <div key={title} className="card" style={{ display: "flex", gap: "1rem", alignItems: "flex-start" }}>
                <div style={{ fontSize: "1.5rem" }}>{title.split(" ")[0]}</div>
                <div>
                  <h4 style={{ marginBottom: "0.25rem" }}>{title.slice(2)}</h4>
                  <p style={{ fontSize: "0.82rem" }}>{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
