// src/components/Navbar.jsx
import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const { pathname } = useLocation();
  const navLink = (to, label) => (
    <Link
      to={to}
      className={`nav-link ${pathname === to ? "nav-link-active" : ""}`}
    >
      {label}
    </Link>
  );
  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">⚕️</span>
          <span className="brand-text">
            PharmaVigilance <span className="brand-zone">Zone 3</span>
          </span>
        </Link>
        <div className="nav-links">
          {navLink("/", "Home")}
          {navLink("/upload", "Triage Case")}
          <a href="http://localhost:8001/docs" target="_blank" rel="noreferrer" className="nav-link">
            API Docs ↗
          </a>
        </div>
      </div>
    </nav>
  );
}
