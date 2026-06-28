// src/config/api.js
// Central API configuration for Zone 2 frontend

export const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

export const ENDPOINTS = {
  check: `${API_BASE_URL}/duplicate/check`,
  health: `${API_BASE_URL}/duplicate/health`,
  metrics: `${API_BASE_URL}/duplicate/metrics`,
};

// Sample test cases preloaded in the form
export const SAMPLE_CASES = [
  {
    label: "🔴 Duplicate Scenario – John Doe / Paracetamol Rash",
    data: {
      case_id: "TEMP001",
      patient_name: "John Doe",
      age: 45,
      gender: "Male",
      drug: "Paracetamol",
      reaction: "Severe Skin Rash",
      event_date: "2025-06-10",
      report_text:
        "Patient developed severe skin rash after taking Paracetamol.",
    },
  },
  {
    label: "🟡 Possible Duplicate – Metformin Acidosis",
    data: {
      case_id: "TEMP002",
      patient_name: "Sarah Wilson",
      age: 43,
      gender: "Female",
      drug: "Metformin",
      reaction: "Nausea and Acidosis",
      event_date: "2025-03-05",
      report_text:
        "Diabetic female on Metformin developed nausea and signs of metabolic acidosis.",
    },
  },
  {
    label: "🟢 Unique Case – Doxycycline Photosensitivity",
    data: {
      case_id: "TEMP003",
      patient_name: "Yusuf Al-Rashid",
      age: 28,
      gender: "Male",
      drug: "Doxycycline",
      reaction: "Photosensitivity",
      event_date: "2025-06-20",
      report_text:
        "Male patient developed severe sunburn-like photosensitivity reaction on face and arms after starting Doxycycline for acne treatment.",
    },
  },
  {
    label: "🔴 Duplicate Scenario – Warfarin Brain Bleed",
    data: {
      case_id: "TEMP005",
      patient_name: "Robert J",
      age: 62,
      gender: "Male",
      drug: "Warfarin",
      reaction: "Brain Bleed",
      event_date: "2024-11-22",
      report_text:
        "Male patient on Warfarin suffered intracranial bleeding with sudden headache and neurological deficit.",
    },
  },
];
