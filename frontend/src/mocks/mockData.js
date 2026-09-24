/* =========================================================================
 *  DATOS MOCK TEMPORALES  -  TomatoAPI
 * =========================================================================
 *  Estos datos existen ÚNICAMENTE para poder visualizar la interfaz
 *  mientras el backend FastAPI aún no expone todos los endpoints.
 *
 *  Cómo se usan:
 *    - Se activan mediante la bandera VITE_USE_MOCKS (ver src/services/api.js).
 *    - NADA fuera de la carpeta /mocks debe importar este archivo salvo la
 *      capa de servicios cuando la bandera de mocks está activa.
 *
 *  Cómo eliminarlos cuando el backend esté listo:
 *    1. Poner VITE_USE_MOCKS=false (o quitar la variable).
 *    2. Borrar la carpeta src/mocks/.
 *    3. Borrar las ramas `if (USE_MOCKS)` en src/services/*.
 *
 *  IMPORTANTE: estos mocks NO simulan que el backend real responde.
 *  Son claramente un modo de demostración local.
 * ========================================================================= */

function isoOffset(days) {
  const d = new Date()
  d.setHours(9, 0, 0, 0)
  d.setDate(d.getDate() + days)
  return d.toISOString()
}

export const MOCK_USER = {
  id: "usr_mock_1",
  nombre: "Ana Rojas",
  email: "ana@tomatoapi.dev",
}

export const MOCK_TOKEN = "mock.jwt.token-solo-para-demostracion"

export const MOCK_PLANTAS = [
  { id: "tomate", nombre: "Tomate", especie: "Solanum lycopersicum" },
  { id: "lechuga", nombre: "Lechuga", especie: "Lactuca sativa" },
  { id: "papa", nombre: "Papa", especie: "Solanum tuberosum" },
  { id: "maiz", nombre: "Maíz", especie: "Zea mays" },
  { id: "pimenton", nombre: "Pimentón", especie: "Capsicum annuum" },
  { id: "zanahoria", nombre: "Zanahoria", especie: "Daucus carota" },
]

export const MOCK_PLANTACIONES = [
  {
    id: "1",
    planta: "tomate",
    planta_nombre: "Tomate",
    ubicacion: "Coquimbo, Chile",
    tipo_tierra: "franco",
    etapa: "floracion",
    ultimo_riego: isoOffset(-3),
    proximo_riego: isoOffset(0),
    estado: "regar",
    creado_en: isoOffset(-40),
  },
  {
    id: "2",
    planta: "lechuga",
    planta_nombre: "Lechuga",
    ubicacion: "La Serena, Chile",
    tipo_tierra: "limoso",
    etapa: "vegetativa",
    ultimo_riego: isoOffset(-1),
    proximo_riego: isoOffset(2),
    estado: "lluvia",
    creado_en: isoOffset(-25),
  },
  {
    id: "3",
    planta: "maiz",
    planta_nombre: "Maíz",
    ubicacion: "Ovalle, Chile",
    tipo_tierra: "arcilloso",
    etapa: "inicial",
    ultimo_riego: isoOffset(0),
    proximo_riego: isoOffset(4),
    estado: "humedad_suficiente",
    creado_en: isoOffset(-12),
  },
  {
    id: "4",
    planta: "pimenton",
    planta_nombre: "Pimentón",
    ubicacion: "Vicuña, Chile",
    tipo_tierra: "arenoso",
    etapa: "fructificacion",
    ultimo_riego: isoOffset(-2),
    proximo_riego: isoOffset(1),
    estado: "no_regar",
    creado_en: isoOffset(-8),
  },
]

export function mockRecomendacion(id) {
  const p = MOCK_PLANTACIONES.find((x) => x.id === id)
  const estado = p?.estado || "regar"
  const map = {
    regar: {
      estado: "regar",
      titulo: "Regar hoy",
      motivo: "El terreno alcanzará un nivel bajo de humedad durante la jornada.",
    },
    no_regar: {
      estado: "no_regar",
      titulo: "No regar hoy",
      motivo: "Se pronostica lluvia en las próximas horas.",
    },
    lluvia: {
      estado: "lluvia",
      titulo: "No regar hoy",
      motivo: "Lluvia próxima; el aporte natural será suficiente.",
    },
    humedad_suficiente: {
      estado: "humedad_suficiente",
      titulo: "No es necesario regar",
      motivo: "El suelo conserva humedad suficiente para la etapa actual.",
    },
  }
  return map[estado]
}

export function mockRiego() {
  return {
    dias: [
      { fecha: isoOffset(0), regar: true, motivo: "Humedad estimada insuficiente." },
      { fecha: isoOffset(1), regar: false, motivo: "Lluvia pronosticada." },
      { fecha: isoOffset(2), regar: false, motivo: "Humedad suficiente en el terreno." },
      { fecha: isoOffset(3), regar: true, motivo: "Descenso previsto de humedad." },
      { fecha: isoOffset(4), regar: false, motivo: "Precipitaciones ligeras esperadas." },
      { fecha: isoOffset(5), regar: true, motivo: "Terreno bajo el umbral óptimo." },
    ],
  }
}

export function mockClima() {
  const condiciones = ["soleado", "parcialmente_nublado", "lluvia", "nublado"]
  return {
    dias: Array.from({ length: 6 }).map((_, i) => {
      const cond = condiciones[i % condiciones.length]
      return {
        fecha: isoOffset(i),
        temp_min: 9 + (i % 4),
        temp_max: 20 + (i % 6),
        condicion: cond,
        prob_lluvia: cond === "lluvia" ? 80 : cond === "nublado" ? 35 : 10,
        precipitacion: cond === "lluvia" ? 6.5 : 0,
      }
    }),
  }
}

export function mockHumedad() {
  return {
    porcentaje: 46,
    nivel: "media",
    dias_restantes: 2,
    detalle: "Se estima que el suelo mantendrá humedad suficiente durante 2 días.",
  }
}
