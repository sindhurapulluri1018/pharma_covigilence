// src/components/SimilarityGauge.jsx
import { useEffect, useRef, useState } from "react";

const getClass = (score) => {
  if (score >= 0.9) return "duplicate";
  if (score >= 0.7) return "possible";
  return "unique";
};

const RADIUS = 56;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export default function SimilarityGauge({ score = 0 }) {
  const [animated, setAnimated] = useState(0);
  const cls = getClass(score);

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(score), 100);
    return () => clearTimeout(timer);
  }, [score]);

  const offset = CIRCUMFERENCE - animated * CIRCUMFERENCE;
  const pct = Math.round(score * 100);

  return (
    <div className="score-ring-wrapper">
      <div className="score-ring">
        <svg width="140" height="140" viewBox="0 0 140 140">
          <circle className="score-ring-track" cx="70" cy="70" r={RADIUS} />
          <circle
            className={`score-ring-fill ${cls}`}
            cx="70" cy="70" r={RADIUS}
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="score-ring-text">
          <span className={`score-number`} style={{ color: `var(--${cls})` }}>
            {pct}%
          </span>
          <span className="score-label">Similarity</span>
        </div>
      </div>
    </div>
  );
}
