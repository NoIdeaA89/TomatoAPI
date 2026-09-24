import { Droplets, CloudSun, Sprout } from "lucide-react"

export default function AuthBranding() {
  return (
    <aside className="auth-brand">
      <span className="auth-brand-badge">
        <img src="/icon.svg" width={34} height={34} alt="" aria-hidden="true" />
        TomatoAPI
      </span>

      <div>
        <h2>Riego inteligente para cada plantación</h2>
        <p style={{ marginBottom: "2rem" }}>
          Registra tus cultivos y recibe recomendaciones de riego basadas en clima,
          tipo de tierra y etapa de crecimiento.
        </p>
        <ul>
          <li>
            <span className="ico">
              <Droplets size={18} aria-hidden="true" />
            </span>
            Recomendaciones diarias de riego
          </li>
          <li>
            <span className="ico">
              <CloudSun size={18} aria-hidden="true" />
            </span>
            Pronóstico del clima integrado
          </li>
          <li>
            <span className="ico">
              <Sprout size={18} aria-hidden="true" />
            </span>
            Seguimiento por etapa de cultivo
          </li>
        </ul>
      </div>

      <p style={{ fontSize: "0.85rem" }}>© {new Date().getFullYear()} TomatoAPI</p>
    </aside>
  )
}
