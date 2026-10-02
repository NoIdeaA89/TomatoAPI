import { useEffect, useState } from "react"
import { useNavigate, useParams, Link } from "react-router-dom"
import { ArrowLeft, Save } from "lucide-react"
import { useAsync } from "../hooks/useAsync.js"
import {
  listarPlantas,
  obtenerPlantacion,
  crearPlantacion,
  actualizarPlantacion,
} from "../services/plantacionesService.js"
import { TIPOS_TIERRA, ETAPAS_DESARROLLO } from "../utils/constants.js"
import DemoBanner from "../components/common/DemoBanner.jsx"
import LoadingSpinner from "../components/common/LoadingSpinner.jsx"
import ErrorMessage from "../components/common/ErrorMessage.jsx"

const EMPTY = {
  planta: "",
  ubicacion: "",
  tipo_tierra: "",
  etapa: "",
  ultimo_riego: "",
}

export default function PlantacionFormPage() {
  const { id } = useParams()
  const esEdicion = Boolean(id)
  const navigate = useNavigate()

  const { data: plantas, loading: cargandoPlantas } = useAsync(() => listarPlantas())
  const [form, setForm] = useState(EMPTY)
  const [errores, setErrores] = useState({})
  const [cargandoRegistro, setCargandoRegistro] = useState(esEdicion)
  const [errorCarga, setErrorCarga] = useState(null)
  const [guardando, setGuardando] = useState(false)
  const [errorGuardado, setErrorGuardado] = useState(null)

  useEffect(() => {
    if (!esEdicion) return
    let vivo = true
    setCargandoRegistro(true)
    obtenerPlantacion(id)
      .then((p) => {
        if (!vivo) return
        setForm({
          planta: p.planta || "",
          ubicacion: p.ubicacion || "",
          tipo_tierra: p.tipo_tierra || "",
          etapa: p.etapa || "",
          // Cortamos el string de fecha para obtener solo "YYYY-MM-DD"
          ultimo_riego: p.ultimo_riego ? p.ultimo_riego.split('T')[0] : "", 
        })
        setErrorCarga(null)
      })
      .catch((err) => vivo && setErrorCarga(err?.message || "No se pudo cargar la plantación."))
      .finally(() => vivo && setCargandoRegistro(false))
    return () => {
      vivo = false
    }
  }, [id, esEdicion])

  function actualizar(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }))
    setErrores((e) => ({ ...e, [campo]: undefined }))
  }

  function validar() {
    const e = {}
    if (!form.planta) e.planta = "Selecciona una planta."
    if (!form.ubicacion.trim()) e.ubicacion = "Ingresa la ubicación."
    if (!form.tipo_tierra) e.tipo_tierra = "Selecciona el tipo de tierra."
    if (!form.etapa) e.etapa = "Selecciona la etapa de desarrollo."
    setErrores(e)
    return Object.keys(e).length === 0
  }

  async function onSubmit(evento) {
    evento.preventDefault()
    if (!validar()) return
    setGuardando(true)
    setErrorGuardado(null)
    try {
      const payload = {
        planta: form.planta,
        ubicacion: form.ubicacion.trim(),
        tipo_tierra: form.tipo_tierra,
        etapa: form.etapa,
        // Convertimos el string a formato ISO o enviamos null
        ultimo_riego: form.ultimo_riego ? new Date(form.ultimo_riego).toISOString() : null,
      }
      const registro = esEdicion
        ? await actualizarPlantacion(id, payload)
        : await crearPlantacion(payload)
      navigate(`/plantaciones/${registro.id}`, { replace: true })
    } catch (err) {
      setErrorGuardado(err?.message || "No se pudo guardar la plantación.")
      setGuardando(false)
    }
  }

  if (cargandoRegistro) return <LoadingSpinner label="Cargando plantación…" />
  if (errorCarga)
    return (
      <div className="stack-lg">
        <BackLink />
        <ErrorMessage message={errorCarga} onRetry={() => navigate(0)} />
      </div>
    )

  return (
    <div className="stack-lg" style={{ maxWidth: "620px" }}>
      <DemoBanner />
      <div>
        <BackLink />
        <h1 style={{ marginTop: "0.75rem" }}>
          {esEdicion ? "Editar plantación" : "Nueva plantación"}
        </h1>
        <p className="muted">
          {esEdicion
            ? "Actualiza los datos de tu cultivo."
            : "Registra un cultivo para recibir recomendaciones de riego."}
        </p>
      </div>

      <form className="card" style={{ padding: "1.5rem" }} onSubmit={onSubmit} noValidate>
        <div className="field">
          <label htmlFor="planta">Planta</label>
          <select
            id="planta"
            className={`select ${errores.planta ? "has-error" : ""}`}
            value={form.planta}
            onChange={(e) => actualizar("planta", e.target.value)}
            disabled={cargandoPlantas}
          >
            <option value="">{cargandoPlantas ? "Cargando…" : "Selecciona una planta"}</option>
            {(plantas || []).map((p) => (
              <option key={p.id} value={p.id}>
                {p.nombre} — {p.especie}
              </option>
            ))}
          </select>
          {errores.planta && <span className="field-error">{errores.planta}</span>}
        </div>

        <div className="field">
          <label htmlFor="ultimo_riego">Último riego (Opcional)</label>
          <input
            id="ultimo_riego"
            type="date"
            className="input"
            value={form.ultimo_riego}
            max={new Date().toISOString().split("T")[0]} // Evita seleccionar fechas futuras
            onChange={(e) => actualizar("ultimo_riego", e.target.value)}
          />
          <p className="muted" style={{ fontSize: "0.8rem", marginTop: "0.25rem" }}>
            Si lo dejas en blanco, el sistema asumirá que el suelo está saturado de humedad a partir de hoy.
          </p>
        </div>

        <div className="field">
          <label htmlFor="tipo_tierra">Tipo de tierra</label>
          <select
            id="tipo_tierra"
            className={`select ${errores.tipo_tierra ? "has-error" : ""}`}
            value={form.tipo_tierra}
            onChange={(e) => actualizar("tipo_tierra", e.target.value)}
          >
            <option value="">Selecciona el tipo de tierra</option>
            {TIPOS_TIERRA.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
          {errores.tipo_tierra && <span className="field-error">{errores.tipo_tierra}</span>}
        </div>

        <div className="field">
          <label htmlFor="etapa">Etapa de desarrollo</label>
          <select
            id="etapa"
            className={`select ${errores.etapa ? "has-error" : ""}`}
            value={form.etapa}
            onChange={(e) => actualizar("etapa", e.target.value)}
          >
            <option value="">Selecciona la etapa</option>
            {ETAPAS_DESARROLLO.map((et) => (
              <option key={et.value} value={et.value}>
                {et.label}
              </option>
            ))}
          </select>
          {errores.etapa && <span className="field-error">{errores.etapa}</span>}
        </div>

        {errorGuardado && (
          <p className="field-error" role="alert" style={{ marginBottom: "1rem" }}>
            {errorGuardado}
          </p>
        )}

        <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem" }}>
          <button type="submit" className="btn btn-primary" disabled={guardando}>
            {guardando ? (
              <LoadingSpinner size={16} inline label="Guardando…" />
            ) : (
              <Save size={17} aria-hidden="true" />
            )}
            {guardando ? "Guardando…" : "Guardar"}
          </button>
          <Link to={esEdicion ? `/plantaciones/${id}` : "/plantaciones"} className="btn btn-secondary">
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  )
}

function BackLink() {
  return (
    <Link to="/plantaciones" className="btn btn-ghost btn-sm" style={{ paddingLeft: 0 }}>
      <ArrowLeft size={16} aria-hidden="true" />
      Volver a plantaciones
    </Link>
  )
}
