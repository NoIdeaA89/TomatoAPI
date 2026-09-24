export default function LoadingSpinner({ size = 28, label = "Cargando…", inline = false }) {
  const spinner = (
    <span
      className="spinner"
      style={{ width: size, height: size }}
      role="status"
      aria-label={label}
    />
  )
  if (inline) return spinner
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "0.85rem",
        padding: "3rem 1rem",
        color: "var(--color-muted)",
      }}
    >
      {spinner}
      <span style={{ fontSize: "0.9rem" }}>{label}</span>
    </div>
  )
}
