import { Link } from "react-router-dom"
import { Sprout, Droplets, CloudRain, CircleCheck, Plus } from "lucide-react"
import { useAuth } from "../hooks/useAuth.js"
import { useAsync } from "../hooks/useAsync.js"
import { listarPlantaciones } from "../services/plantacionesService.js"
import DemoBanner from "../components/common/DemoBanner.jsx"
import LoadingSpinner from "../components/common/LoadingSpinner.jsx"
import ErrorMessage from "../components/common/ErrorMessage.jsx"
import EmptyState from "../components/common/EmptyState.jsx"
import PlantacionCard from "../components/plantaciones/PlantacionCard.jsx"
import "./DashboardPage.css"

const STAT_META = [
  { key: "total", label: "Plantaciones", icon: Sprout, tone: "primary" },
  { key: "regar", label: "Requieren riego", icon: Droplets, tone: "warning" },
  { key: "lluvia", label: "Lluvia próxima", icon: CloudRain, tone: "water" },
  { key: "ok", label: "Humedad suficiente", icon: CircleCheck, tone: "success" },
]

export default function DashboardPage() {
  const { user } = useAuth()
  const { data, loading, error, reload } = useAsync(() => listarPlantaciones())

  const plantaciones = data || []
  const stats = {
    total: plantaciones.length,
    regar: plantaciones.filter((p) => p.estado === "regar").length,
    lluvia: plantaciones.filter((p) => p.estado === "lluvia").length,
    ok: plantaciones.filter((p) => p.estado === "humedad_suficiente").length,
  }
  const atencion = plantaciones.filter((p) => p.estado === "regar")

  return (
    <div className="stack-lg">
      <DemoBanner />

      <header className="page-head">
        <div>
          <h1>Hola, {user?.nombre?.split(" ")[0] || "agricultor"}</h1>
          <p className="muted">Resumen del estado de riego de tus cultivos.</p>
        </div>
        <Link to="/plantaciones/nueva" className="btn btn-primary">
          <Plus size={18} aria-hidden="true" />
          Nueva plantación
        </Link>
      </header>

      {loading && <LoadingSpinner label="Cargando tu panel…" />}
      {error && !loading && <ErrorMessage message={error} onRetry={reload} />}

      {!loading && !error && (
        <>
          <section className="stats-grid" aria-label="Resumen">
            {STAT_META.map(({ key, label, icon: Icon, tone }) => (
              <article key={key} className={`stat-card tone-${tone}`}>
                <span className="stat-icon" aria-hidden="true">
                  <Icon size={22} />
                </span>
                <div>
                  <strong className="stat-value">{stats[key]}</strong>
                  <span className="stat-label">{label}</span>
                </div>
              </article>
            ))}
          </section>

          <section className="stack-md">
            <div className="section-head">
              <h2>Requieren riego hoy</h2>
              <Link to="/plantaciones" className="link-strong">
                Ver todas
              </Link>
            </div>

            {atencion.length === 0 ? (
              <EmptyState
                icon={CircleCheck}
                title="Todo en orden"
                description="Ninguna plantación necesita riego en este momento."
              />
            ) : (
              <div className="plantaciones-grid">
                {atencion.map((p) => (
                  <PlantacionCard key={p.id} plantacion={p} />
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  )
}
