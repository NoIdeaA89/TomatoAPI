import axios from "axios"

/* =========================================================================
 *  Cliente HTTP central - TomatoAPI
 * =========================================================================
 *  - Base URL configurable vía VITE_API_URL (por defecto FastAPI local).
 *  - Adjunta el JWT en cada petición mediante un interceptor.
 *  - Normaliza los errores para que la UI muestre mensajes claros.
 *
 *  MODO MOCK:
 *  Mientras el backend no exponga todos los endpoints, los servicios pueden
 *  devolver datos de src/mocks. Esto se controla con VITE_USE_MOCKS.
 *  Por defecto está ACTIVADO para poder ver la interfaz sin backend.
 *  Los mocks son un modo de demostración explícito: NO fingen que una
 *  petición real al backend tuvo éxito.
 * ========================================================================= */

export const USE_MOCKS = String(import.meta.env.VITE_USE_MOCKS ?? "true") !== "false"

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

const TOKEN_KEY = "tomatoapi_token"

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}
export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
}
export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
})

// Adjunta el token JWT a cada petición.
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Normaliza los errores de red / API a un objeto consistente.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Sesión expirada o inválida -> limpiar y avisar a la app.
    if (error.response?.status === 401) {
      clearToken()
      window.dispatchEvent(new CustomEvent("auth:unauthorized"))
    }
    return Promise.reject(normalizeError(error))
  },
)

export function normalizeError(error) {
  if (error?.isNormalized) return error

  // FastAPI suele responder { detail: "..." } o { detail: [{ msg }] }
  const detail = error?.response?.data?.detail
  let message =
    error?.response?.data?.message ||
    (typeof detail === "string" ? detail : null) ||
    (Array.isArray(detail) ? detail.map((d) => d.msg).join(" · ") : null)

  if (!message) {
    if (error?.code === "ECONNABORTED") {
      message = "La solicitud tardó demasiado. Inténtalo nuevamente."
    } else if (error?.message === "Network Error") {
      message =
        "No se pudo conectar con el servidor. Verifica tu conexión o que el backend esté activo."
    } else {
      message = "Ocurrió un error inesperado. Inténtalo nuevamente."
    }
  }

  return {
    isNormalized: true,
    status: error?.response?.status ?? 0,
    message,
  }
}

// Pequeña latencia para que el modo mock se sienta realista.
export function mockDelay(ms = 450) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
