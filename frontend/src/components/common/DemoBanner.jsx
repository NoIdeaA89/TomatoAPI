import { Info } from "lucide-react"
import { USE_MOCKS } from "../../services/api.js"

/* Aviso visible del modo demostración.
 * Deja claro que los datos son de ejemplo y NO provienen del backend real. */
export default function DemoBanner() {
  if (!USE_MOCKS) return null
  return (
    <div className="demo-banner" role="status">
      <Info size={17} aria-hidden="true" />
      <p>
        <strong>Modo demostración.</strong> Los datos que ves son de ejemplo (mocks locales)
        mientras se conecta el backend. Los cambios no se guardan de forma permanente.
      </p>
    </div>
  )
}
