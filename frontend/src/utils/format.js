// Utilidades de formato de fechas para la interfaz (es-CL).

const DIAS = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]
const MESES = [
  "enero",
  "febrero",
  "marzo",
  "abril",
  "mayo",
  "junio",
  "julio",
  "agosto",
  "septiembre",
  "octubre",
  "noviembre",
  "diciembre",
]

function toDate(value) {
  if (!value) return null
  const d = value instanceof Date ? value : new Date(value)
  return Number.isNaN(d.getTime()) ? null : d
}

export function formatFecha(value) {
  const d = toDate(value)
  if (!d) return "—"
  return `${d.getDate()} de ${MESES[d.getMonth()]} de ${d.getFullYear()}`
}

export function formatFechaCorta(value) {
  const d = toDate(value)
  if (!d) return "—"
  return `${d.getDate()} ${MESES[d.getMonth()].slice(0, 3)}`
}

export function formatFechaHora(value) {
  const d = toDate(value)
  if (!d) return "—"
  const hh = String(d.getHours()).padStart(2, "0")
  const mm = String(d.getMinutes()).padStart(2, "0")
  return `${formatFecha(d)} · ${hh}:${mm}`
}

export function nombreDia(value) {
  const d = toDate(value)
  if (!d) return "—"
  return DIAS[d.getDay()]
}

export function diasDesde(value) {
  const d = toDate(value)
  if (!d) return null
  const diff = Date.now() - d.getTime()
  return Math.floor(diff / (1000 * 60 * 60 * 24))
}
