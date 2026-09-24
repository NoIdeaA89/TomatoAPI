import { Navigate, useLocation } from "react-router-dom"
import { useAuth } from "../hooks/useAuth.js"
import LoadingSpinner from "../components/common/LoadingSpinner.jsx"

export default function PrivateRoute({ children }) {
  const { isAuthenticated, initializing } = useAuth()
  const location = useLocation()

  if (initializing) {
    return (
      <div style={{ minHeight: "60vh", display: "grid", placeItems: "center" }}>
        <LoadingSpinner label="Verificando sesión…" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return children
}
