import { useState } from "react"
import { Link, useNavigate, useLocation } from "react-router-dom"
import { Eye, EyeOff } from "lucide-react"
import { useAuth } from "../hooks/useAuth.js"
import { USE_MOCKS } from "../services/api.js"
import Logo from "../components/common/Logo.jsx"
import AuthBranding from "../components/layout/AuthBranding.jsx"
import "./AuthPage.css"

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || "/"

  const [form, setForm] = useState({ email: "", password: "" })
  const [errors, setErrors] = useState({})
  const [showPass, setShowPass] = useState(false)
  const [apiError, setApiError] = useState("")
  const [loading, setLoading] = useState(false)

  function update(e) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
    setErrors((prev) => ({ ...prev, [e.target.name]: undefined }))
  }

  function validate() {
    const next = {}
    if (!form.email.trim()) next.email = "Ingresa tu correo."
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) next.email = "Correo no válido."
    if (!form.password) next.password = "Ingresa tu contraseña."
    setErrors(next)
    return Object.keys(next).length === 0
  }

  async function onSubmit(e) {
    e.preventDefault()
    setApiError("")
    if (!validate()) return
    setLoading(true)
    try {
      await login(form)
      navigate(from, { replace: true })
    } catch (err) {
      setApiError(err?.message || "No se pudo iniciar sesión.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      <AuthBranding />
      <main className="auth-form-panel">
        <div className="auth-card">
          <div className="logo-mobile">
            <Logo />
          </div>
          <h1>Inicia sesión</h1>
          <p className="auth-lead">Accede a tu panel de plantaciones.</p>

          {apiError && (
            <div className="auth-alert" role="alert">
              {apiError}
            </div>
          )}

          <form onSubmit={onSubmit} noValidate>
            <div className="field">
              <label htmlFor="email">Correo electrónico</label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                className={`input ${errors.email ? "has-error" : ""}`}
                placeholder="tu@correo.com"
                value={form.email}
                onChange={update}
              />
              {errors.email && <span className="field-error">{errors.email}</span>}
            </div>

            <div className="field">
              <label htmlFor="password">Contraseña</label>
              <div className="input-wrap">
                <input
                  id="password"
                  name="password"
                  type={showPass ? "text" : "password"}
                  autoComplete="current-password"
                  className={`input ${errors.password ? "has-error" : ""}`}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={update}
                />
                <button
                  type="button"
                  className="input-toggle"
                  onClick={() => setShowPass((s) => !s)}
                  aria-label={showPass ? "Ocultar contraseña" : "Mostrar contraseña"}
                >
                  {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.password && <span className="field-error">{errors.password}</span>}
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? "Ingresando…" : "Ingresar"}
            </button>
          </form>

          <p className="auth-switch">
            ¿No tienes cuenta? <Link to="/registro">Regístrate</Link>
          </p>

          {USE_MOCKS && (
            <p className="auth-demo-note">
              Modo demostración activo: puedes ingresar con cualquier correo y contraseña.
              Los datos son de ejemplo mientras el backend se conecta.
            </p>
          )}
        </div>
      </main>
    </div>
  )
}
