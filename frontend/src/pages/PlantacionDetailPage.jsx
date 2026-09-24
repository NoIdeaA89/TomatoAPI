import { useState } from "react"
import { useParams, Link, useNavigate } from "react-router-dom"
import {
  ArrowLeft,
  Pencil,
  Trash2,
  MapPin,
  Mountain,
  Sprout,
  Droplets,
  CalendarClock,
  Sun,
  CloudRain,
  Cloud,
  CloudSun,
} from "lucide-react"
import { useAsync } from "../hooks/useAsync.js"
import {
  obtenerPlantacion,
  obtenerRecomendacion,
  obtenerRiego,
  obtenerClima,
  obtenerHumedad,
  eliminarPlantacion,
} from "../services/plantacionesService.js"
import {
  getEstado,
  labelFrom,
  TIPOS_TIERRA,
  ETAPAS_DESARROLLO,
  NIVELES_HUMEDAD,
} from "../utils/constants.js"
import { formatFecha, formatFechaCorta, nombreDia } from "../utils/format.js"
import DemoBanner from "../components/common/DemoBanner.jsx"
import LoadingSpinner from "../components/common/LoadingSpinner.jsx"
import ErrorMessage from "../components/common/ErrorMessage.jsx"
import StatusBadge from "../components/common/StatusBadge.jsx"
import ConfirmModal from "../components/common/ConfirmModal.jsx"
import "./PlantacionDetailPage.css"

const CLIMA_ICON = {
  soleado: Sun,
  parcialmente_nublado: CloudSun,
  nublado: Cloud,
  lluvia: CloudRain,
}
const CLIMA_LABEL = {
  soleado: "Soleado",
  parcialmente_nublado: "Parcial",
  nublado: "Nublado",
  lluvia: "Lluvia",
}

export default function PlantacionDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const plantacion = useAsync(() => obtenerPlantacion(id), [id])
  const recomendacion = useAsync(() => obtenerRecomendacion(id), [id])
  const riego = useAsync(() => obtenerRiego(id), [id])
  const clima = useAsync(() => obtenerClima(id), [id])
  const humedad = useAsync(() => obtenerHumedad(id), [id])

  const [confirmar, setConfirmar] = useState(false)
  const [eliminando, setEliminando] = useState(false)

  async function onEliminar() {
    setEliminando(true)
    try {
      await eliminarPlantacion(id)
      navigate("/plantaciones", { replace: true })
    } catch {
      setEliminando(false)
      setConfirmar(false)
    }
  }

  if (plantacion.loading) return <LoadingSpinner label="Cargando plantación…" />
  if (plantacion.error)
    return (
      <div className="stack-lg">
        <BackLink />
        <ErrorMessage message={plantacion.error} onRetry={plantacion.reload} />
      </div>
    )

  const p = plantacion.data
  const estado = getEstado(p.estado)

  return (
    <div className="stack-lg">
      <DemoBanner />

      <div>
        <BackLink />
        <div className="detail-head">
          <div className="detail-head-main">
            <span className="detail-icon" aria-hidden="true">
              <Sprout size={26} />
            </span>
            <div>
              <h1>{p.planta_nombre}</h1>
              <StatusBadge tone={estado.tone}>{estado.label}</StatusBadge>
            </div>
          </div>
          <div className="detail-actions">
            <Link to={`/plantaciones/${id}/editar`} className="btn btn-secondary btn-sm">
              <Pencil size={15} aria-hidden="true" />
              Editar
            </Link>
            <button className="btn btn-ghost btn-sm" onClick={() => setConfirmar(true)}>
              <Trash2 size={15} aria-hidden="true" />
              Eliminar
            </button>
          </div>
        </div>
      </div>

      {/* Datos del cultivo */}
      <section className="card detail-facts">
        <Fact icon={MapPin} label="Ubicación" value={p.ubicacion} />
        <Fact icon={Mountain} label="Tipo de tierra" value={labelFrom(TIPOS_TIERRA, p.tipo_tierra)} />
        <Fact icon={Sprout} label="Etapa" value={labelFrom(ETAPAS_DESARROLLO, p.etapa)} />
        <Fact icon={Droplets} label="Último riego" value={formatFecha(p.ultimo_riego)} />
        <Fact icon={CalendarClock} label="Próximo riego" value={formatFecha(p.proximo_riego)} />
      </section>

      {/* Recomendación */}
      <section className="stack-md">
        <h2>Recomendación de hoy</h2>
        <Panel state={recomendacion}>
          {(rec) => (
            <div className={`reco-card tone-${getEstado(rec.estado).tone}`}>
              <Droplets size={24} aria-hidden="true" />
              <div>
                <strong className="reco-title">{rec.titulo}</strong>
                <p>{rec.motivo}</p>
              </div>
            </div>
          )}
        </Panel>
      </section>

      {/* Humedad */}
      <section className="stack-md">
        <h2>Humedad del suelo</h2>
        <Panel state={humedad}>
          {(h) => {
            const nivel = NIVELES_HUMEDAD[h.nivel] || { label: h.nivel, tone: "neutral" }
            return (
              <div className="card humedad-card">
                <div className="humedad-top">
                  <span className="humedad-value">{h.porcentaje}%</span>
                  <StatusBadge tone={nivel.tone}>Nivel {nivel.label}</StatusBadge>
                </div>
                <div
                  className="humedad-bar"
                  role="progressbar"
                  aria-valuenow={h.porcentaje}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  <span
                    className={`humedad-fill tone-${nivel.tone}`}
                    style={{ width: `${h.porcentaje}%` }}
                  />
                </div>
                <p className="muted">{h.detalle}</p>
              </div>
            )
          }}
        </Panel>
      </section>

      {/* Plan de riego */}
      <section className="stack-md">
        <h2>Plan de riego (próximos días)</h2>
        <Panel state={riego}>
          {(r) => (
            <ul className="riego-list">
              {r.dias.map((d) => (
                <li key={d.fecha} className="riego-row">
                  <div className="riego-day">
                    <strong>{nombreDia(d.fecha)}</strong>
                    <span className="muted">{formatFechaCorta(d.fecha)}</span>
                  </div>
                  <StatusBadge tone={d.regar ? "warning" : "success"}>
                    {d.regar ? "Regar" : "No regar"}
                  </StatusBadge>
                  <p className="riego-motivo muted">{d.motivo}</p>
                </li>
              ))}
            </ul>
          )}
        </Panel>
      </section>

      {/* Clima */}
      <section className="stack-md">
        <h2>Pronóstico del clima</h2>
        <Panel state={clima}>
          {(c) => (
            <div className="clima-grid">
              {c.dias.map((d) => {
                const Icon = CLIMA_ICON[d.condicion] || Cloud
                return (
                  <div key={d.fecha} className="clima-card">
                    <span className="clima-day">{nombreDia(d.fecha).slice(0, 3)}</span>
                    <Icon size={26} className="clima-icon" aria-hidden="true" />
                    <span className="clima-cond">{CLIMA_LABEL[d.condicion] || d.condicion}</span>
                    <span className="clima-temp">
                      {d.temp_max}° <span className="muted">{d.temp_min}°</span>
                    </span>
                    <span className="clima-lluvia">
                      <Droplets size={12} aria-hidden="true" />
                      {d.prob_lluvia}%
                    </span>
                  </div>
                )
              })}
            </div>
          )}
        </Panel>
      </section>

      <ConfirmModal
        open={confirmar}
        title="Eliminar plantación"
        message={`¿Seguro que deseas eliminar la plantación de ${p.planta_nombre}? Esta acción no se puede deshacer.`}
        confirmLabel="Eliminar"
        danger
        loading={eliminando}
        onConfirm={onEliminar}
        onCancel={() => setConfirmar(false)}
      />
    </div>
  )
}

function Fact({ icon: Icon, label, value }) {
  return (
    <div className="fact">
      <span className="fact-icon" aria-hidden="true">
        <Icon size={18} />
      </span>
      <div>
        <span className="fact-label">{label}</span>
        <strong className="fact-value">{value}</strong>
      </div>
    </div>
  )
}

/* Envuelve cada panel de monitoreo con sus propios estados de carga/error,
 * para que un endpoint lento o caído no bloquee al resto de la vista. */
function Panel({ state, children }) {
  if (state.loading) return <LoadingSpinner label="Cargando…" />
  if (state.error) return <ErrorMessage message={state.error} onRetry={state.reload} />
  if (!state.data) return null
  return children(state.data)
}

function BackLink() {
  return (
    <Link to="/plantaciones" className="btn btn-ghost btn-sm" style={{ paddingLeft: 0 }}>
      <ArrowLeft size={16} aria-hidden="true" />
      Volver a plantaciones
    </Link>
  )
}
