import { Link } from "react-router-dom"
import Logo from "../components/common/Logo.jsx"

export default function NotFoundPage() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "1.25rem",
        padding: "2rem",
        textAlign: "center",
      }}
    >
      <Logo size={40} />
      <h1 style={{ fontSize: "3.5rem", color: "var(--color-primary)" }}>404</h1>
      <p className="muted" style={{ maxWidth: "40ch" }}>
        La página que buscas no existe o fue movida.
      </p>
      <Link to="/" className="btn btn-primary">
        Volver al panel
      </Link>
    </div>
  )
}
