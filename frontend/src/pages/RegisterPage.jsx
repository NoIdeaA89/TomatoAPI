import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { Eye, EyeOff } from "lucide-react"
import { useAuth } from "../hooks/useAuth.js"
import { USE_MOCKS } from "../services/api.js"
import Logo from "../components/common/Logo.jsx"
import AuthBranding from "../components/layout/AuthBranding.jsx"
import "./AuthPage.css"

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({ nombre: "", email: "", password: "", confirm: "" })
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
    if (!form.nombre.trim()) next.nombre = "Ingresa tu nombre."
    if (!form.email.trim()) next.email = "Ingresa tu correo."
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) next.email = "Correo no válido."
    if (!form.password) next.password = "Ingresa una contraseña."
    else if (form.password.length < 6) next.password = "Mínimo 6 caracteres."
    if (form.confirm !== form.password) next.confirm = "Las contraseñas no coinciden."
    setErrors(next)
    return Object.keys(next).length === 0
  }

  async function onSubmit(e) {
    e.preventDefault()
    setApiError("")
    if (!validate()) return
    setLoading(true)
    try {
      await register({ nombre: form.nombre, email: form.email, password: form.password })
      navigate("/", { replace: true })
    } catch (err) {
      setApiError(err?.message || "No se pudo crear la cuenta.")
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
          <h1>Crea tu cuenta</h1>
          <p className="auth-lead">Empieza a gestionar el riego de tus cultivos.</p>

          {apiError && (
            <div className="auth-alert" role="alert">
              {apiError}
            </div>
          )}

          <form onSubmit={onSubmit} noValidate>
            <div className="field">
              <label htmlFor="nombre">Nombre</label>
              <input
                id="nombre"
                name="nombre"
                type="text"
                autoComplete="name"
                className={`input ${errors.nombre ? "has-error" : ""}`}
                placeholder="Tu nombre"
                value={form.nombre}
                onChange={update}
              />
              {errors.nombre && <span className="field-error">{errors.nombre}</span>}
            </div>

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
                  autoComplete="new-password"
                  className={`input ${errors.password ? "has-error" : ""}`}
                  placeholder="Mínimo 6 caracteres"
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

            <div className="field">
              <label htmlFor="confirm">Confirmar contraseña</label>
              <input
                id="confirm"
                name="confirm"
                type={showPass ? "text" : "password"}
                autoComplete="new-password"
                className={`input ${errors.confirm ? "has-error" : ""}`}
                placeholder="Repite la contraseña"
                value={form.confirm}
                onChange={update}
              />
              {errors.confirm && <span className="field-error">{errors.confirm}</span>}
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? "Creando cuenta…" : "Crear cuenta"}
            </button>
          </form>

          <p className="auth-switch">
            ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
          </p>

          {USE_MOCKS && (
            <p className="auth-demo-note">
              Modo demostración activo: el registro es simulado localmente mientras el backend
              se conecta.
            </p>
          )}
        </div>
      </main>
    </div>
  )
}
