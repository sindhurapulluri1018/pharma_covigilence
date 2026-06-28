// src/components/DecisionBadge.jsx
const CONFIG = {
  Duplicate:          { icon: "🔴", cls: "duplicate" },
  "Possible Duplicate": { icon: "🟡", cls: "possible" },
  "Unique Case":       { icon: "🟢", cls: "unique" },
};

export default function DecisionBadge({ decision, size = "normal" }) {
  const cfg = CONFIG[decision] || { icon: "⚪", cls: "" };
  return (
    <span className={`badge badge-${cfg.cls}`} style={size === "large" ? { fontSize: "0.95rem", padding: "0.5rem 1.2rem" } : {}}>
      {cfg.icon} {decision}
    </span>
  );
}
