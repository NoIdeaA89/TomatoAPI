import { useState } from "react"
import { Outlet, NavLink, useLocation } from "react-router-dom"
import { LayoutDashboard, Sprout, Menu, X, LogOut, Plus } from "lucide-react"
import { useAuth } from "../../hooks/useAuth.js"
import Logo from "../common/Logo.jsx"
import "./AppLayout.css"

const NAV = [
  { to: "/", label: "Panel", icon: LayoutDashboard, end: true },
  { to: "/plantaciones", label: "Plantaciones", icon: Sprout, end: false },
]

const TITLES = {
  "/": "Panel",
  "/plantaciones": "Plantaciones",
}

function initials(name = "") {
  return (
    name
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((w) => w[0]?.toUpperCase())
      .join("") || "U"
  )
}

export default function AppLayout() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [open, setOpen] = useState(false)

  let title = TITLES[location.pathname] || "Plantaciones"
  if (location.pathname === "/plantaciones/nueva") title = "Nueva plantación"
  else if (location.pathname.endsWith("/editar")) title = "Editar plantación"
  else if (/^\/plantaciones\/[^/]+$/.test(location.pathname)) title = "Detalle de plantación"

  return (
    <div className="app-shell">
      {open && <div className="sidebar-overlay" onClick={() => setOpen(false)} />}

      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="sidebar-head">
          <Logo size={30} />
        </div>
        <nav className="sidebar-nav" aria-label="Navegación principal">
          <span className="nav-section-label">General</span>
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
              onClick={() => setOpen(false)}
            >
              <Icon size={19} aria-hidden="true" />
              {label}
            </NavLink>
          ))}
          <span className="nav-section-label">Acciones</span>
          <NavLink
            to="/plantaciones/nueva"
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
            onClick={() => setOpen(false)}
          >
            <Plus size={19} aria-hidden="true" />
            Nueva plantación
          </NavLink>
        </nav>
        <div className="sidebar-foot">
          <div className="user-card">
            <span className="user-avatar" aria-hidden="true">
              {initials(user?.nombre)}
            </span>
            <span className="user-meta">
              <strong>{user?.nombre || "Usuario"}</strong>
              <span>{user?.email}</span>
            </span>
          </div>
          <button className="btn btn-secondary btn-block btn-sm" onClick={logout}>
            <LogOut size={16} aria-hidden="true" />
            Cerrar sesión
          </button>
        </div>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <button
            className="icon-btn menu-btn"
            onClick={() => setOpen((o) => !o)}
            aria-label={open ? "Cerrar menú" : "Abrir menú"}
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
          <span className="topbar-title">{title}</span>
        </header>
        <main className="page-content">
          <div className="container-page">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
