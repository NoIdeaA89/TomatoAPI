export default function Logo({ size = 34, showText = true }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: "0.6rem" }}>
      <img src="/icon.svg" width={size} height={size} alt="" aria-hidden="true" />
      {showText && (
        <span
          style={{
            fontFamily: "var(--font-sans)",
            fontWeight: 800,
            fontSize: size * 0.55,
            letterSpacing: "-0.01em",
            color: "var(--color-text)",
          }}
        >
          Tomato<span style={{ color: "var(--color-primary)" }}>API</span>
        </span>
      )}
    </span>
  )
}
