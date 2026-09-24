import { useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { Plus, Search, Sprout } from "lucide-react"
import { useAsync } from "../hooks/useAsync.js"
import { listarPlantaciones } from "../services/plantacionesService.js"
import { ESTADOS } from "../utils/constants.js"
import DemoBanner from "../components/common/DemoBanner.jsx"
import LoadingSpinner from "../components/common/LoadingSpinner.jsx"
import ErrorMessage from "../components/common/ErrorMessage.jsx"
import EmptyState from "../components/common/EmptyState.jsx"
import PlantacionCard from "../components/plantaciones/PlantacionCard.jsx"
import "./PlantacionesPage.css"

const FILTROS = [{ value: "todos", label: "Todos" }, ...Object.values(ESTADOS).map((e) => ({ value: e.key, label: e.label }))]

export default function PlantacionesPage() {
  const { data, loading, error, reload } = useAsync(() => listarPlantaciones())
  const [busqueda, setBusqueda] = useState("")
  const [filtro, setFiltro] = useState("todos")

  const plantaciones = data || []

  const visibles = useMemo(() => {
    const q = busqueda.trim().toLowerCase()
    return plantaciones.filter((p) => {
      const coincideTexto =
        !q ||
        p.planta_nombre.toLowerCase().includes(q) ||
        p.ubicacion.toLowerCase().includes(q)
      const coincideFiltro = filtro === "todos" || p.estado === filtro
      return coincideTexto && coincideFiltro
    })
  }, [plantaciones, busqueda, filtro])

  return (
    <div className="stack-lg">
      <DemoBanner />

      <header className="page-head">
        <div>
          <h1>Plantaciones</h1>
          <p className="muted">Administra tus cultivos y revisa su estado de riego.</p>
        </div>
        <Link to="/plantaciones/nueva" className="btn btn-primary">
          <Plus size={18} aria-hidden="true" />
          Nueva plantación
        </Link>
      </header>

      {!loading && !error && plantaciones.length > 0 && (
        <div className="list-toolbar">
          <div className="search-field">
            <Search size={17} aria-hidden="true" />
            <input
              type="search"
              className="input"
              placeholder="Buscar por planta o ubicación…"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              aria-label="Buscar plantaciones"
            />
          </div>
          <div className="filter-chips" role="group" aria-label="Filtrar por estado">
            {FILTROS.map((f) => (
              <button
                key={f.value}
                type="button"
                className={`chip ${filtro === f.value ? "active" : ""}`}
                onClick={() => setFiltro(f.value)}
                aria-pressed={filtro === f.value}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {loading && <LoadingSpinner label="Cargando plantaciones…" />}
      {error && !loading && <ErrorMessage message={error} onRetry={reload} />}

      {!loading && !error && plantaciones.length === 0 && (
        <EmptyState
          icon={Sprout}
          title="Aún no tienes plantaciones"
          description="Crea tu primera plantación para comenzar a recibir recomendaciones de riego."
          action={
            <Link to="/plantaciones/nueva" className="btn btn-primary">
              <Plus size={18} aria-hidden="true" />
              Crear plantación
            </Link>
          }
        />
      )}

      {!loading && !error && plantaciones.length > 0 && visibles.length === 0 && (
        <EmptyState
          icon={Search}
          title="Sin resultados"
          description="No hay plantaciones que coincidan con tu búsqueda o filtro."
        />
      )}

      {!loading && !error && visibles.length > 0 && (
        <div className="plantaciones-grid">
          {visibles.map((p) => (
            <PlantacionCard key={p.id} plantacion={p} />
          ))}
        </div>
      )}
    </div>
  )
}
