export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        gap: "0.75rem",
        padding: "3.5rem 1.5rem",
        background: "var(--color-surface)",
        border: "1px dashed var(--color-border)",
        borderRadius: "var(--radius)",
      }}
    >
      {Icon && (
        <span
          style={{
            display: "inline-flex",
            padding: "0.9rem",
            borderRadius: "50%",
            background: "var(--color-primary-soft)",
            color: "var(--color-primary)",
          }}
        >
          <Icon size={26} aria-hidden="true" />
        </span>
      )}
      <h3 style={{ fontSize: "1.15rem" }}>{title}</h3>
      {description && (
        <p className="muted" style={{ maxWidth: "42ch", fontSize: "0.95rem" }}>
          {description}
        </p>
      )}
      {action && <div style={{ marginTop: "0.5rem" }}>{action}</div>}
    </div>
  )
}
