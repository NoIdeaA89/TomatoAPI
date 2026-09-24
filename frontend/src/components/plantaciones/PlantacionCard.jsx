import { Link } from "react-router-dom"
import { MapPin, Sprout, CalendarClock, ArrowRight } from "lucide-react"
import StatusBadge from "../common/StatusBadge.jsx"
import { getEstado, labelFrom, ETAPAS_DESARROLLO } from "../../utils/constants.js"
import { formatFechaCorta } from "../../utils/format.js"
import "./PlantacionCard.css"

export default function PlantacionCard({ plantacion }) {
  const estado = getEstado(plantacion.estado)
  return (
    <Link to={`/plantaciones/${plantacion.id}`} className="plantacion-card">
      <div className="pc-top">
        <span className="pc-icon" aria-hidden="true">
          <Sprout size={20} />
        </span>
        <StatusBadge tone={estado.tone}>{estado.label}</StatusBadge>
      </div>

      <h3 className="pc-title">{plantacion.planta_nombre}</h3>

      <ul className="pc-meta">
        <li>
          <MapPin size={15} aria-hidden="true" />
          {plantacion.ubicacion}
        </li>
        <li>
          <Sprout size={15} aria-hidden="true" />
          {labelFrom(ETAPAS_DESARROLLO, plantacion.etapa)}
        </li>
        <li>
          <CalendarClock size={15} aria-hidden="true" />
          Próximo riego: {formatFechaCorta(plantacion.proximo_riego)}
        </li>
      </ul>

      <span className="pc-cta">
        Ver detalle
        <ArrowRight size={16} aria-hidden="true" />
      </span>
    </Link>
  )
}
