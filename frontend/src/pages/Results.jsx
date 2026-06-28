// src/pages/Results.jsx
import { useLocation, useNavigate, Link } from "react-router-dom";
import SimilarityGauge from "../components/SimilarityGauge";
import FieldScoreTable from "../components/FieldScoreTable";
import DecisionBadge from "../components/DecisionBadge";
import RoutingCard from "../components/RoutingCard";
import PipelineStatus from "../components/PipelineStatus";
import CandidateRetrievalCard from "../components/CandidateRetrievalCard";
import TopCandidatesTable from "../components/TopCandidatesTable";
import AlgorithmFooter from "../components/AlgorithmFooter";

const BANNER_CLS = {
  Duplicate:           "duplicate",
  "Possible Duplicate": "possible",
  "Unique Case":        "unique",
};

const BANNER_ICONS = {
  Duplicate:           "🔴",
  "Possible Duplicate": "🟡",
  "Unique Case":        "🟢",
};

export default function Results() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state?.result) {
    return (
      <div className="page" style={{ textAlign: "center" }}>
        <div className="container">
          <h2>No Results Found</h2>
          <p style={{ marginBottom: "1.5rem" }}>Please submit a case first.</p>
          <Link to="/upload" className="btn btn-primary">← Back to Check Case</Link>
        </div>
      </div>
    );
  }

  const r = state.result;
  const bannerCls = BANNER_CLS[r.decision] || "unique";
  const bannerIcon = BANNER_ICONS[r.decision] || "⚪";
  const pctScore = Math.round((r.overall_similarity || 0) * 100);

  return (
    <div className="page animate-fade-up">
      <div className="container" style={{ maxWidth: 960 }}>

        {/* ── Header ── */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.5rem", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div className="section-label">Zone 2 · VigiMatch Result</div>
            <h2>Duplicate Check Report</h2>
            <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "0.82rem", color: "var(--text-muted)" }}>
              Case {r.incoming_case} · {r.candidates_evaluated} candidate{r.candidates_evaluated !== 1 ? "s" : ""} evaluated · v{r.pipeline_version}
            </span>
          </div>
          <button onClick={() => navigate("/upload")} className="btn btn-secondary">
            ← Check Another
          </button>
        </div>

        {/* ── Pipeline Status ── */}
        <PipelineStatus stages={r.pipeline_stages} />

        {/* ── Decision Banner ── */}
        <div className={`decision-banner ${bannerCls}`} style={{ marginBottom: "1.5rem" }}>
          <div className="decision-icon">{bannerIcon}</div>
          <div style={{ flex: 1 }}>
            <div className="section-label" style={{ color: `var(--${bannerCls})` }}>Decision</div>
            <div className={`decision-title ${bannerCls}`}>{r.decision}</div>
            <div style={{ fontSize: "0.875rem", marginTop: "0.25rem", color: "var(--text-secondary)" }}>
              {r.routing?.next_action}
            </div>

            {/* Decision Reason bullets */}
            {r.decision_reason && r.decision_reason.length > 0 && (
              <ul style={{ marginTop: "0.75rem", paddingLeft: "1.25rem", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                {r.decision_reason.map((reason, i) => (
                  <li key={i} style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                    {reason}
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem" }}>
            <SimilarityGauge score={r.overall_similarity} />
            <DecisionBadge decision={r.decision} />
          </div>
        </div>

        {/* ── Overall Similarity breakdown label ── */}
        <div className="card" style={{ marginBottom: "1.5rem", padding: "1rem 1.25rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "0.75rem" }}>
            <div>
              <div className="section-label">Overall Similarity</div>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: pctScore >= 90 ? "var(--duplicate)" : pctScore >= 70 ? "var(--possible)" : "var(--unique)" }}>
                {pctScore}%
              </div>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "0.15rem" }}>
                Computed using: Drug · Reaction · Narrative · Patient · Date · Age · Gender
              </div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.3rem", fontSize: "0.8rem", color: "var(--text-muted)" }}>
              <div>🔴 Duplicate ≥ 90%</div>
              <div>🟡 Possible Duplicate ≥ 70%</div>
              <div>🟢 Unique Case &lt; 70%</div>
            </div>
          </div>
        </div>

        {/* ── Candidate Retrieval Card ── */}
        <CandidateRetrievalCard info={r.candidate_retrieval_info} />

        {/* ── Top Candidate Matches ── */}
        {r.top_candidates && r.top_candidates.length > 0 && (
          <TopCandidatesTable topCandidates={r.top_candidates} />
        )}

        {/* ── Incoming vs Best Match ── */}
        <div className="grid-2" style={{ gridTemplateColumns: "1fr 1fr", marginBottom: "1.5rem" }}>
          <div className="card">
            <h4 style={{ marginBottom: "1rem", display: "flex", gap: "0.5rem" }}>
              📥 Incoming Case
              <span className="tag">Unvalidated</span>
            </h4>
            {state.incoming && (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {[
                  ["ID",          state.incoming.case_id],
                  ["Patient",     state.incoming.patient_name],
                  ["Age / Gender", `${state.incoming.age} · ${state.incoming.gender}`],
                  ["Drug",        state.incoming.drug],
                  ["Reaction",    state.incoming.reaction],
                  ["Date",        state.incoming.event_date],
                ].map(([k, v]) => (
                  <div key={k} style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                    <span style={{ color: "var(--text-muted)" }}>{k}</span>
                    <span style={{ fontWeight: 500, textAlign: "right", maxWidth: "65%" }}>{v}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <h4 style={{ marginBottom: "1rem", display: "flex", gap: "0.5rem" }}>
              🗂️ Best Match
              {r.matched_case
                ? <span className="badge badge-info">{r.matched_case}</span>
                : <span className="tag">No match</span>
              }
            </h4>
            {r.matched_case_detail ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {[
                  ["ID",           r.matched_case_detail.case_id],
                  ["Patient",      r.matched_case_detail.patient_name],
                  ["Age / Gender", `${r.matched_case_detail.age} · ${r.matched_case_detail.gender}`],
                  ["Drug",         r.matched_case_detail.drug],
                  ["Reaction",     r.matched_case_detail.reaction],
                  ["Date",         r.matched_case_detail.event_date],
                ].map(([k, v]) => (
                  <div key={k} style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                    <span style={{ color: "var(--text-muted)" }}>{k}</span>
                    <span style={{ fontWeight: 500, textAlign: "right", maxWidth: "65%" }}>{v}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: "0.875rem" }}>No existing case matched this incoming report.</p>
            )}
          </div>
        </div>

        {/* ── Routing ── */}
        <div style={{ marginBottom: "1.5rem" }}>
          <RoutingCard
            routing={r.routing}
            confidence={r.confidence}
            confidenceReason={r.confidence_reason}
          />
        </div>

        {/* ── Field-Level Similarity Breakdown ── */}
        <div className="card" style={{ marginBottom: "1.5rem" }}>
          <h4 style={{ marginBottom: "1rem" }}>📊 Field-Level Similarity Breakdown</h4>
          <FieldScoreTable
            fieldScores={r.field_scores}
            fieldExplanations={r.field_explanations}
            incomingCase={state.incoming}
            matchedCase={r.matched_case_detail}
          />
        </div>

        {/* ── Matched Case Narrative ── */}
        {r.matched_case_detail?.report_text && (
          <div className="card" style={{ marginBottom: "1.5rem" }}>
            <h4 style={{ marginBottom: "0.75rem" }}>📄 Matched Case Narrative</h4>
            <p style={{ fontSize: "0.875rem", lineHeight: 1.8, fontStyle: "italic", borderLeft: "3px solid var(--border-accent)", paddingLeft: "1rem" }}>
              "{r.matched_case_detail.report_text}"
            </p>
          </div>
        )}

        {/* ── Algorithms Used ── */}
        <AlgorithmFooter />

      </div>
    </div>
  );
}
