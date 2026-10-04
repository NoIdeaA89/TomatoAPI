import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { ArrowLeft, Leaf } from "lucide-react"
import { crearPlanta } from "../services/plantacionesService.js"
import DemoBanner from "../components/common/DemoBanner.jsx"
import LoadingSpinner from "../components/common/LoadingSpinner.jsx"

import { validarPlanta, generarIdPlanta } from "../utils/planta.js"

const EMPTY = {
  nombre: "",
  especie: "",
  kc_ini: "",
  kc_mid: "",
  kc_end: "",
  raiz_m: "",
  agotamiento: "",
}

export default function PlantaFormPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY)
  const [errores, setErrores] = useState({})
  const [guardando, setGuardando] = useState(false)
  const [errorGuardado, setErrorGuardado] = useState(null)

  function actualizar(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }))
    setErrores((e) => ({ ...e, [campo]: undefined }))
  }

  function validar() {
    const e = validarPlanta(form)
    setErrores(e)
    return Object.keys(e).length === 0
  }

  async function onSubmit(evento) {
    evento.preventDefault()
    if (guardando || !validar()) return
    setGuardando(true)
    setErrorGuardado(null)

    try {
      // Autogenerar un ID en minúsculas y sin espacios
      const idGenerado = generarIdPlanta(form.nombre.trim())
      
      const payload = {
        id: idGenerado,
        nombre: form.nombre.trim(),
        especie: form.especie.trim(),
        kc_ini: parseFloat(form.kc_ini),
        kc_mid: parseFloat(form.kc_mid),
        kc_end: parseFloat(form.kc_end),
        raiz_m: parseFloat(form.raiz_m),
        agotamiento: parseFloat(form.agotamiento),
      }
      
      await crearPlanta(payload)
      // Redirigimos al formulario de plantaciones tras crearla exitosamente
      navigate("/plantaciones/nueva", { replace: true })
    } catch (err) {
      setErrorGuardado(err?.message || "No se pudo guardar la planta. Verifica que no exista una con el mismo nombre.")
      setGuardando(false)
    }
  }

  return (
    <div className="stack-lg" style={{ maxWidth: "620px" }}>
      <DemoBanner />
      <div>
        <Link to="/plantaciones/nueva" className="btn btn-ghost btn-sm" style={{ paddingLeft: 0 }}>
          <ArrowLeft size={16} aria-hidden="true" />
          Volver a nueva plantación
        </Link>
        <h1 style={{ marginTop: "0.75rem" }}>Añadir nueva especie</h1>
        <p className="muted">Registra los parámetros agronómicos de una nueva planta al catálogo.</p>
      </div>

      <form className="card" style={{ padding: "1.5rem" }} onSubmit={onSubmit} noValidate>
        
        {/* Identificación */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
          <div className="field">
            <label htmlFor="nombre">Nombre común</label>
            <input id="nombre" type="text" maxLength={100} className={`input ${errores.nombre ? "has-error" : ""}`} value={form.nombre} onChange={(e) => actualizar("nombre", e.target.value)} placeholder="Ej: Nalca" />
            {errores.nombre && <span className="field-error">{errores.nombre}</span>}
          </div>
          <div className="field">
            <label htmlFor="especie">Especie científica</label>
            <input id="especie" type="text" maxLength={100} className={`input ${errores.especie ? "has-error" : ""}`} value={form.especie} onChange={(e) => actualizar("especie", e.target.value)} placeholder="Ej: Gunnera tinctoria" />
            {errores.especie && <span className="field-error">{errores.especie}</span>}
          </div>
        </div>

        {/* Coeficientes de Cultivo (Kc) */}
        <h3 style={{ fontSize: "1rem", marginBottom: "0.75rem", borderBottom: "1px solid #eaeaea", paddingBottom: "0.5rem" }}>Coeficientes de Cultivo (Kc)</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
          <div className="field">
            <label htmlFor="kc_ini">Etapa Inicial</label>
            <input id="kc_ini" min="0.1" max="2" type="number" step="0.01" className={`input ${errores.kc_ini ? "has-error" : ""}`} value={form.kc_ini} onChange={(e) => actualizar("kc_ini", e.target.value)} placeholder="0.60" />
            {errores.kc_ini && <span className="field-error">{errores.kc_ini}</span>}
          </div>
          <div className="field">
            <label htmlFor="kc_mid">Etapa Media</label>
            <input id="kc_mid" min="0.1" max="2" type="number" step="0.01" className={`input ${errores.kc_mid ? "has-error" : ""}`} value={form.kc_mid} onChange={(e) => actualizar("kc_mid", e.target.value)} placeholder="1.15" />
            {errores.kc_mid && <span className="field-error">{errores.kc_mid}</span>}
          </div>
          <div className="field">
            <label htmlFor="kc_end">Etapa Final</label>
            <input id="kc_end" min="0.1" max="2" type="number" step="0.01" className={`input ${errores.kc_end ? "has-error" : ""}`} value={form.kc_end} onChange={(e) => actualizar("kc_end", e.target.value)} placeholder="0.80" />
            {errores.kc_end && <span className="field-error">{errores.kc_end}</span>}
          </div>
        </div>

        {/* Parámetros de Suelo */}
        <h3 style={{ fontSize: "1rem", marginBottom: "0.75rem", borderBottom: "1px solid #eaeaea", paddingBottom: "0.5rem" }}>Parámetros de Suelo y Raíz</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
          <div className="field">
            <label htmlFor="raiz_m">Profundidad de Raíz (m)</label>
            <input id="raiz_m" min="0.1" max="5" type="number" step="0.1" className={`input ${errores.raiz_m ? "has-error" : ""}`} value={form.raiz_m} onChange={(e) => actualizar("raiz_m", e.target.value)} placeholder="0.7" />
            {errores.raiz_m && <span className="field-error">{errores.raiz_m}</span>}
          </div>
          <div className="field">
            <label htmlFor="agotamiento">Agotamiento Permitido</label>
            <input id="agotamiento" min="0.1" max="0.9" type="number" step="0.01" className={`input ${errores.agotamiento ? "has-error" : ""}`} value={form.agotamiento} onChange={(e) => actualizar("agotamiento", e.target.value)} placeholder="0.40" />
            {errores.agotamiento && <span className="field-error">{errores.agotamiento}</span>}
          </div>
        </div>

        {errorGuardado && <p className="field-error" style={{ marginTop: "1rem" }}>{errorGuardado}</p>}

        <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem" }}>
          <button type="submit" className="btn btn-primary" disabled={guardando}>
            {guardando ? <LoadingSpinner size={16} inline label="Guardando…" /> : <Leaf size={17} />}
            {guardando ? "Guardando…" : "Registrar Especie"}
          </button>
        </div>
      </form>
    </div>
  )
}