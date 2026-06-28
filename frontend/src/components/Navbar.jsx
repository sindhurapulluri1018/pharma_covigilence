// src/components/Navbar.jsx
import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const { pathname } = useLocation();
  const isActive = (p) => (pathname === p ? "active" : "");

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <div className="navbar-logo">🛡️</div>
        <div>
          <div style={{ fontSize: "0.85rem", lineHeight: 1.2 }}>PharmaVigilance</div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", fontWeight: 400 }}>
            Zone 2 · Duplicate Detection
          </div>
        </div>
      </Link>

      <ul className="navbar-links">
        <li><Link to="/" className={isActive("/")}>Home</Link></li>
        <li><Link to="/upload" className={isActive("/upload")}>Check Case</Link></li>
        <li>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}
          >
            API Docs ↗
          </a>
        </li>
      </ul>
    </nav>
  );
}
