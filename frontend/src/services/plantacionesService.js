import { api, USE_MOCKS, mockDelay } from "./api.js"
import {
  MOCK_PLANTACIONES,
  MOCK_PLANTAS,
  mockRecomendacion,
  mockRiego,
  mockClima,
  mockHumedad,
} from "../mocks/mockData.js"

/* Servicio de plantaciones y monitoreo.
 * Endpoints esperados del backend FastAPI:
 *   GET    /plantaciones
 *   GET    /plantaciones/:id
 *   POST   /plantaciones
 *   PUT    /plantaciones/:id
 *   DELETE /plantaciones/:id
 *   GET    /plantaciones/:id/recomendacion
 *   GET    /plantaciones/:id/riego
 *   GET    /plantaciones/:id/clima
 *   GET    /plantaciones/:id/humedad
 *   GET    /plantas
 *
 *  El modo mock mantiene un arreglo en memoria para que el CRUD se sienta real
 *  durante la demostración. Se reinicia al recargar la página.
 */

let memoria = null
function store() {
  if (!memoria) memoria = MOCK_PLANTACIONES.map((p) => ({ ...p }))
  return memoria
}

export async function listarPlantaciones() {
  if (USE_MOCKS) {
    await mockDelay()
    return store().map((p) => ({ ...p }))
  }
  const { data } = await api.get("/plantaciones")
  return data.items || data
}

export async function obtenerPlantacion(id) {
  if (USE_MOCKS) {
    await mockDelay()
    const p = store().find((x) => x.id === String(id))
    if (!p) throw { isNormalized: true, status: 404, message: "Plantación no encontrada." }
    return { ...p }
  }
  const { data } = await api.get(`/plantaciones/${id}`)
  return data
}

export async function crearPlantacion(payload) {
  if (USE_MOCKS) {
    await mockDelay()
    const planta = MOCK_PLANTAS.find((p) => p.id === payload.planta)
    const nueva = {
      id: String(Date.now()),
      ...payload,
      planta_nombre: planta ? planta.nombre : payload.planta,
      estado: "humedad_suficiente",
      proximo_riego: null,
      creado_en: new Date().toISOString(),
    }
    store().unshift(nueva)
    return { ...nueva }
  }
  const { data } = await api.post("/plantaciones", payload)
  return data
}

export async function actualizarPlantacion(id, payload) {
  if (USE_MOCKS) {
    await mockDelay()
    const list = store()
    const idx = list.findIndex((x) => x.id === String(id))
    if (idx === -1) throw { isNormalized: true, status: 404, message: "Plantación no encontrada." }
    const planta = MOCK_PLANTAS.find((p) => p.id === payload.planta)
    list[idx] = {
      ...list[idx],
      ...payload,
      planta_nombre: planta ? planta.nombre : list[idx].planta_nombre,
    }
    return { ...list[idx] }
  }
  const { data } = await api.put(`/plantaciones/${id}`, payload)
  return data
}

export async function eliminarPlantacion(id) {
  if (USE_MOCKS) {
    await mockDelay()
    memoria = store().filter((x) => x.id !== String(id))
    return { ok: true }
  }
  await api.delete(`/plantaciones/${id}`)
  return { ok: true }
}

export async function listarPlantas() {
  if (USE_MOCKS) {
    await mockDelay(250)
    return MOCK_PLANTAS.map((p) => ({ ...p }))
  }
  const { data } = await api.get("/plantas")
  return data.items || data
}

/* -------- Monitoreo -------- */

export async function obtenerRecomendacion(id) {
  if (USE_MOCKS) {
    await mockDelay()
    return mockRecomendacion(String(id))
  }
  const { data } = await api.get(`/plantaciones/${id}/recomendacion`)
  return data
}

export async function obtenerRiego(id) {
  if (USE_MOCKS) {
    await mockDelay()
    return mockRiego()
  }
  const { data } = await api.get(`/plantaciones/${id}/riego`)
  return data
}

export async function obtenerClima(id) {
  if (USE_MOCKS) {
    await mockDelay()
    return mockClima()
  }
  const { data } = await api.get(`/plantaciones/${id}/clima`)
  return data
}

export async function obtenerHumedad(id) {
  if (USE_MOCKS) {
    await mockDelay()
    return mockHumedad()
  }
  const { data } = await api.get(`/plantaciones/${id}/humedad`)
  return data
}

export async function crearPlanta(payload) {
  if (USE_MOCKS) {
    await mockDelay();
    // En modo mock, simplemente devolvemos el payload simulando éxito
    return { ...payload };
  }
  const { data } = await api.post("/plantas", payload);
  return data;
}
