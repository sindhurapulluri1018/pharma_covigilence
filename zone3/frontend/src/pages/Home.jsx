// src/pages/Home.jsx
import { Link } from "react-router-dom";

const PIPELINE_STEPS = [
  { icon: "📝", title: "Prompt Builder", desc: "Constructs an ICH E2B(R3)-aligned prompt from the incoming ICSR narrative and metadata. Pure function — fully auditable and deterministic." },
  { icon: "🤖", title: "LLM Classification", desc: "Sends the structured prompt to GPT-4o-mini. Returns JSON only: seriousness, criteria, expectedness, confidence, and clinical reasoning." },
  { icon: "⚕️", title: "Seriousness Classifier", desc: "Parses and validates the LLM response against ICH criteria: Death · Life-threatening · Hospitalization · Disability · Congenital Anomaly." },
  { icon: "📋", title: "Expectedness Classifier", desc: "Checks the reported reaction against the approved product label (mock SmPC). Returns Expected or Unexpected using fuzzy matching." },
  { icon: "🚦", title: "Priority Router", desc: "Deterministic rule-based routing: Death/Life-threatening → Critical · Hospitalization/Disability/Congenital → Expedited · Otherwise → Standard." },
];

const STATS = [
  { icon: "⚕️", value: "6", label: "ICH Criteria" },
  { icon: "🤖", value: "GPT-4o-mini", label: "LLM Model" },
  { icon: "📋", value: "25+", label: "Drug Labels" },
  { icon: "🚦", value: "3", label: "Priority Queues" },
];

const FUTURE_HOOKS = [
  ["📖 SmPC Integration", "load_from_smpc(drug) stub in expectedness_classifier.py"],
  ["🌍 WHO Drug Label", "load_from_who_label(drug) stub ready for integration"],
  ["🏥 MedDRA Coding", "Reaction text ready for MedDRA term matching in Zone 5"],
  ["🔗 LangChain Router", "LLMManager interface supports swapping to LangChain"],
  ["☁️ Azure OpenAI", "Set LLM_MODEL in config to use Azure OpenAI endpoint"],
  ["🔗 Person 6 Orchestrator", "workflow_state field in every response"],
];

export default function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="hero-gradient page" style={{ textAlign: "center", paddingTop: "6rem" }}>
        <div className="container">
          <span className="tag" style={{ marginBottom: "1.5rem", display: "inline-flex" }}>
            ⚕️ Zone 3 · ICH E2B(R3) Triage Engine
          </span>
          <h1 style={{ marginBottom: "1.5rem", background: "linear-gradient(135deg, #f1f5f9 0%, #94a3b8 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            AI-Powered<br />Adverse Event Triage
          </h1>
          <p style={{ fontSize: "1.1rem", maxWidth: 580, margin: "0 auto 2.5rem", color: "var(--text-secondary)" }}>
            Classify ICSRs by seriousness, expectedness, and priority using GPT-4o-mini 
            guided by ICH E2B(R3) criteria. Routes to Critical, Expedited, or Standard queue.
          </p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
            <Link to="/upload" className="btn btn-primary btn-lg">🔬 Triage a Case</Link>
            <a href="http://localhost:8001/docs" target="_blank" rel="noreferrer" className="btn btn-secondary btn-lg">📚 API Docs</a>
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
                <div className="stat-value" style={{ color: "var(--accent)", fontSize: "1.3rem" }}>{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ICH Criteria */}
      <section style={{ padding: "2rem 0" }}>
        <div className="container">
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <div className="section-label">ICH E2B(R3)</div>
            <h2>Seriousness Criteria</h2>
          </div>
          <div className="grid-2" style={{ gridTemplateColumns: "repeat(3, 1fr)" }}>
            {[
              ["💀", "Death", "Patient died as a result of the adverse event"],
              ["⚡", "Life-threatening", "Patient at immediate risk of death during event"],
              ["🏥", "Hospitalization", "Event required or prolonged hospitalisation"],
              ["♿", "Disability", "Significant, persistent, or permanent disability"],
              ["👶", "Congenital Anomaly", "Birth defect or foetal harm from drug exposure"],
              ["🔬", "Medically Important", "Event requiring intervention to prevent serious outcomes"],
            ].map(([icon, title, desc]) => (
              <div key={title} className="card" style={{ display: "flex", gap: "0.75rem" }}>
                <span style={{ fontSize: "1.5rem" }}>{icon}</span>
                <div>
                  <h4 style={{ marginBottom: "0.25rem", fontSize: "0.9rem" }}>{title}</h4>
                  <p style={{ fontSize: "0.78rem" }}>{desc}</p>
                </div>
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
            <h2>The 5-Stage Triage Pipeline</h2>
          </div>
          <div className="card-elevated" style={{ maxWidth: 760, margin: "0 auto" }}>
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

      {/* Future Hooks */}
      <section style={{ padding: "2rem 0 5rem" }}>
        <div className="container">
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <div className="section-label">Extensibility</div>
            <h2>Built for the Future</h2>
          </div>
          <div className="grid-2">
            {FUTURE_HOOKS.map(([title, desc]) => (
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
