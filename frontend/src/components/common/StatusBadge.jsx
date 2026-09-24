import "./StatusBadge.css"

// tone: success | warning | danger | water | neutral
export default function StatusBadge({ tone = "neutral", children, dot = true }) {
  return (
    <span className={`status-badge tone-${tone}`}>
      {dot && <span className="status-dot" aria-hidden="true" />}
      {children}
    </span>
  )
}
