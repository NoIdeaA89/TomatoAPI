// Opciones de dominio usadas en formularios y filtros.
// Idealmente varias de estas listas (ej. plantas) vendrán del backend,
// pero se mantienen aquí como valores por defecto / fallback.

export const TIPOS_TIERRA = [
  { value: "arenoso", label: "Arenoso" },
  { value: "arcilloso", label: "Arcilloso" },
  { value: "limoso", label: "Limoso" },
  { value: "franco", label: "Franco" },
]

export const ETAPAS_DESARROLLO = [
  { value: "germinacion", label: "Germinación" },
  { value: "inicial", label: "Inicial" },
  { value: "vegetativa", label: "Vegetativa" },
  { value: "floracion", label: "Floración" },
  { value: "fructificacion", label: "Fructificación" },
  { value: "maduracion", label: "Maduración" },
]

// Estados de riego / plantación. Cada estado define su presentación visual.
// El backend define el estado; el frontend solo lo representa.
export const ESTADOS = {
  regar: {
    key: "regar",
    label: "Riego recomendado",
    tone: "warning",
  },
  no_regar: {
    key: "no_regar",
    label: "No regar",
    tone: "danger",
  },
  lluvia: {
    key: "lluvia",
    label: "Lluvia próxima",
    tone: "water",
  },
  humedad_suficiente: {
    key: "humedad_suficiente",
    label: "Humedad suficiente",
    tone: "success",
  },
}

export const NIVELES_HUMEDAD = {
  alta: { label: "Alta", tone: "success" },
  media: { label: "Media", tone: "warning" },
  baja: { label: "Baja", tone: "danger" },
}

export function getEstado(key) {
  return ESTADOS[key] || { key, label: key, tone: "neutral" }
}

export function labelFrom(list, value) {
  const found = list.find((item) => item.value === value)
  return found ? found.label : value
}
