// src/components/PipelineStatus.jsx
export default function PipelineStatus({ stages }) {
  const defaultStages = [
    "Prompt Builder",
    "LLM Manager",
    "Response Parser",
    "Seriousness Service",
    "Expectedness Service",
    "Priority Router",
    "Workflow Transition",
  ];
  const list = stages?.length ? stages : defaultStages;
  return (
    <div className="card pipeline-status-card">
      <div className="section-label" style={{ marginBottom: "0.75rem" }}>Pipeline Execution</div>
      <div className="pipeline-status-row">
        {list.map((stage, i) => (
          <div key={stage} className="pipeline-status-item">
            <div className="pipeline-status-chip">
              <span className="pipeline-check">✓</span>
              <span>{stage}</span>
            </div>
            {i < list.length - 1 && <span className="pipeline-arrow">→</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
