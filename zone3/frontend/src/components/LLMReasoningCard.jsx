// src/components/LLMReasoningCard.jsx
import { useState } from "react";

export default function LLMReasoningCard({ explanation, promptUsed, llmModel, fallback }) {
  const [showPrompt, setShowPrompt] = useState(false);

  return (
    <div className="card" style={{ marginBottom: "1.5rem" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
        <h4>🤖 LLM Reasoning</h4>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {fallback && (
            <span className="badge" style={{ background: "rgba(245,158,11,0.15)", color: "#f59e0b", border: "1px solid rgba(245,158,11,0.3)" }}>
              Fallback Mode
            </span>
          )}
          <span className="badge badge-info">{llmModel || "N/A"}</span>
        </div>
      </div>

      {/* Explanation */}
      <div style={{
        background: "var(--bg-secondary)", borderRadius: "var(--radius-md)",
        padding: "1rem", borderLeft: "3px solid var(--accent)", marginBottom: "1rem"
      }}>
        <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginBottom: "0.5rem", textTransform: "uppercase" }}>
          Clinical Reasoning
        </div>
        <p style={{ fontSize: "0.875rem", lineHeight: 1.75, color: "var(--text-secondary)", margin: 0 }}>
          {explanation || "No explanation provided by LLM."}
        </p>
      </div>

      {/* Prompt transparency */}
      {promptUsed && (
        <div>
          <button
            onClick={() => setShowPrompt(!showPrompt)}
            className="btn btn-secondary"
            style={{ fontSize: "0.78rem", padding: "0.4rem 0.75rem", marginBottom: showPrompt ? "0.75rem" : 0 }}
          >
            {showPrompt ? "▲ Hide Prompt" : "▼ View Prompt Sent to LLM"}
          </button>
          {showPrompt && (
            <pre style={{
              background: "#0d1117", color: "#c9d1d9", padding: "1rem",
              borderRadius: "var(--radius-md)", fontSize: "0.75rem",
              lineHeight: 1.6, overflowX: "auto", whiteSpace: "pre-wrap",
              wordBreak: "break-word", border: "1px solid var(--border-color)"
            }}>
              {promptUsed}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
