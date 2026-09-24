import { AlertTriangle, RefreshCw } from "lucide-react"

export default function ErrorMessage({ message, onRetry }) {
  return (
    <div
      role="alert"
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        gap: "0.85rem",
        padding: "2.5rem 1.25rem",
        background: "var(--color-danger-soft)",
        border: "1px solid #f0c9c1",
        borderRadius: "var(--radius)",
        color: "var(--color-danger)",
      }}
    >
      <AlertTriangle size={26} aria-hidden="true" />
      <p style={{ fontWeight: 600, maxWidth: "36ch" }}>{message}</p>
      {onRetry && (
        <button className="btn btn-secondary btn-sm" onClick={onRetry}>
          <RefreshCw size={15} aria-hidden="true" />
          Reintentar
        </button>
      )}
    </div>
  )
}
