import { Navigate } from "react-router-dom"
import { useAuth } from "../hooks/useAuth.js"
import LoadingSpinner from "../components/common/LoadingSpinner.jsx"

// Evita que un usuario ya autenticado vea login/registro.
export default function PublicOnlyRoute({ children }) {
  const { isAuthenticated, initializing } = useAuth()

  if (initializing) {
    return (
      <div style={{ minHeight: "60vh", display: "grid", placeItems: "center" }}>
        <LoadingSpinner label="Cargando…" />
      </div>
    )
  }

  if (isAuthenticated) return <Navigate to="/" replace />

  return children
}
