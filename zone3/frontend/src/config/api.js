// src/config/api.js
export const API_BASE = "http://localhost:8001";

export const ENDPOINTS = {
  check:   `${API_BASE}/triage/check`,
  health:  `${API_BASE}/triage/health`,
  metrics: `${API_BASE}/triage/metrics`,
};

export const SAMPLE_CASES = [
  {
    label: "🔴 Death Case – Warfarin / Intracranial Bleeding",
    data: {
      case_id: "TRIAGE001",
      workflow_state: "READY_FOR_TRIAGE",
      patient_name: "Robert Johnson",
      age: 72,
      gender: "Male",
      drug: "Warfarin",
      reaction: "Intracranial Bleeding",
      event_date: "2025-06-10",
      report_text:
        "Elderly male patient on long-term Warfarin anticoagulation therapy was found unresponsive at home. Transported to emergency room where CT scan confirmed massive intracranial haemorrhage. Despite emergency neurosurgery, patient died within 24 hours of admission. INR was found to be 8.2 at time of presentation.",
    },
  },
  {
    label: "🔴 Life-Threatening – Anaphylactic Shock",
    data: {
      case_id: "TRIAGE002",
      workflow_state: "READY_FOR_TRIAGE",
      patient_name: "Emily Chen",
      age: 28,
      gender: "Female",
      drug: "Amoxicillin",
      reaction: "Anaphylactic Shock",
      event_date: "2025-05-22",
      report_text:
        "Female patient administered IV Amoxicillin for a UTI. Within 5 minutes developed severe anaphylactic shock with hypotension, bronchospasm, and urticaria. Life-threatening situation required immediate epinephrine administration and ICU transfer for monitoring. Patient was at immediate risk of death.",
    },
  },
  {
    label: "🟡 Hospitalization – Metformin / Lactic Acidosis",
    data: {
      case_id: "TRIAGE003",
      workflow_state: "READY_FOR_TRIAGE",
      patient_name: "Sarah Wilson",
      age: 52,
      gender: "Female",
      drug: "Metformin",
      reaction: "Lactic Acidosis",
      event_date: "2025-04-15",
      report_text:
        "Diabetic female patient on Metformin 2000mg/day was admitted to hospital with severe lactic acidosis. Serum lactate was critically elevated. Required inpatient treatment for 5 days with IV fluids and bicarbonate therapy. Metformin was permanently discontinued.",
    },
  },
  {
    label: "🟡 Disability – Ciprofloxacin / Tendon Rupture",
    data: {
      case_id: "TRIAGE004",
      workflow_state: "READY_FOR_TRIAGE",
      patient_name: "Michael Torres",
      age: 65,
      gender: "Male",
      drug: "Ciprofloxacin",
      reaction: "Achilles Tendon Rupture",
      event_date: "2025-03-08",
      report_text:
        "Elderly male patient developed bilateral Achilles tendon rupture after 2 weeks of Ciprofloxacin for a respiratory infection. Surgical repair was required. Patient has significant permanent disability and is unable to return to previous levels of mobility. Permanent impairment is expected.",
    },
  },
  {
    label: "🟢 Non-Serious – Paracetamol / Mild Rash",
    data: {
      case_id: "TRIAGE005",
      workflow_state: "READY_FOR_TRIAGE",
      patient_name: "Anna Schmidt",
      age: 34,
      gender: "Female",
      drug: "Paracetamol",
      reaction: "Mild Skin Rash",
      event_date: "2025-06-18",
      report_text:
        "Female patient developed a mild, localised skin rash on the forearm after taking Paracetamol 500mg for headache. The rash was non-urticarial and self-resolving within 48 hours without any treatment. No hospitalisation required. Patient continued to take the medication without recurrence.",
    },
  },
  {
    label: "🟡 Congenital – Valproate / Birth Defect",
    data: {
      case_id: "TRIAGE006",
      workflow_state: "READY_FOR_TRIAGE",
      patient_name: "Maria Rodriguez",
      age: 26,
      gender: "Female",
      drug: "Valproate",
      reaction: "Neural Tube Defect in Neonate",
      event_date: "2025-02-14",
      report_text:
        "Female patient took Valproate throughout pregnancy for epilepsy. Newborn was diagnosed with a neural tube defect (spina bifida) at birth. This is a suspected drug-induced congenital anomaly. The birth defect requires ongoing surgical and medical management.",
    },
  },
];
