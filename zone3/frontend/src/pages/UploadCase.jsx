// src/pages/UploadCase.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { ENDPOINTS, SAMPLE_CASES } from "../config/api";

const EMPTY_FORM = {
  case_id: "", patient_name: "", age: "", gender: "Male",
  drug: "", reaction: "", event_date: "", report_text: "",
  workflow_state: "READY_FOR_TRIAGE",
};

export default function UploadCase() {
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((p) => ({ ...p, [name]: value }));
  };

  const loadSample = (e) => {
    const idx = parseInt(e.target.value, 10);
    if (isNaN(idx)) return;
    setForm({ ...SAMPLE_CASES[idx].data, age: String(SAMPLE_CASES[idx].data.age) });
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = { ...form, age: parseInt(form.age, 10) };
      const { data } = await axios.post(ENDPOINTS.check, payload);
      navigate("/results", { state: { result: data, incoming: payload } });
    } catch (err) {
      const msg = err?.response?.data?.detail || "Failed to connect. Is the Zone 3 backend running on port 8001?";
      setError(typeof msg === "string" ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 800 }}>
        <div style={{ marginBottom: "2rem" }}>
          <div className="section-label">Zone 3 · Triage Engine</div>
          <h1 style={{ fontSize: "clamp(1.75rem, 4vw, 2.5rem)", marginBottom: "0.5rem" }}>
            Submit ICSR for Triage
          </h1>
          <p>
            Enter the details of a validated, non-duplicate ICSR.
            The AI will classify seriousness, expectedness, and priority using ICH E2B(R3) criteria.
          </p>
        </div>

        {/* Sample loader */}
        <div className="card" style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
            <span style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--text-secondary)" }}>
              ⚡ Load a test scenario:
            </span>
            <select className="form-select" onChange={loadSample} defaultValue="" style={{ flex: 1, minWidth: 260 }} id="sample-selector">
              <option value="" disabled>Choose a preset…</option>
              {SAMPLE_CASES.map((s, i) => (
                <option key={i} value={i}>{s.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="card">
            <h3 style={{ marginBottom: "1.5rem" }}>📋 Case Details</h3>

            <div className="grid-2" style={{ marginBottom: "1rem" }}>
              <div className="form-group">
                <label className="form-label" htmlFor="case_id">Case ID</label>
                <input id="case_id" name="case_id" className="form-input" placeholder="e.g. TRIAGE001" value={form.case_id} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="patient_name">Patient Name</label>
                <input id="patient_name" name="patient_name" className="form-input" placeholder="Full name" value={form.patient_name} onChange={handleChange} required />
              </div>
            </div>

            <div className="grid-2" style={{ marginBottom: "1rem" }}>
              <div className="form-group">
                <label className="form-label" htmlFor="age">Age (years)</label>
                <input id="age" name="age" type="number" className="form-input" placeholder="e.g. 45" min={0} max={120} value={form.age} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="gender">Gender</label>
                <select id="gender" name="gender" className="form-select" value={form.gender} onChange={handleChange}>
                  <option>Male</option><option>Female</option><option>Unknown</option>
                </select>
              </div>
            </div>

            <hr className="divider" />

            <div className="grid-2" style={{ marginBottom: "1rem" }}>
              <div className="form-group">
                <label className="form-label" htmlFor="drug">Suspect Drug</label>
                <input id="drug" name="drug" className="form-input" placeholder="INN or brand name" value={form.drug} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="event_date">Event Date</label>
                <input id="event_date" name="event_date" type="date" className="form-input" value={form.event_date} onChange={handleChange} required />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: "1rem" }}>
              <label className="form-label" htmlFor="reaction">Adverse Reaction</label>
              <input id="reaction" name="reaction" className="form-input" placeholder="e.g. Intracranial Bleeding" value={form.reaction} onChange={handleChange} required />
            </div>

            <div className="form-group" style={{ marginBottom: "1.5rem" }}>
              <label className="form-label" htmlFor="report_text">Case Narrative</label>
              <textarea id="report_text" name="report_text" className="form-textarea" placeholder="Full clinical narrative of the adverse event…" value={form.report_text} onChange={handleChange} required rows={5} />
            </div>

            {error && (
              <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid #ef4444", borderRadius: "var(--radius-sm)", padding: "1rem", marginBottom: "1rem", color: "#ef4444", fontSize: "0.875rem" }}>
                ❌ {error}
              </div>
            )}

            <div style={{ display: "flex", gap: "1rem", justifyContent: "flex-end" }}>
              <button type="button" className="btn btn-secondary" onClick={() => { setForm(EMPTY_FORM); setError(null); }}>
                Clear
              </button>
              <button type="submit" className="btn btn-primary" disabled={loading} id="submit-triage-btn">
                {loading ? (
                  <><span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Consulting LLM…</>
                ) : (
                  "🔬 Run Triage"
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
