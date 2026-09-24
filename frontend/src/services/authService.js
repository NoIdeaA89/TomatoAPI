import { api, USE_MOCKS, mockDelay, setToken, clearToken } from "./api.js"
import { MOCK_USER, MOCK_TOKEN } from "../mocks/mockData.js"

/* Servicio de autenticación.
 * Endpoints esperados del backend FastAPI:
 *   POST /auth/register  -> { access_token, user }
 *   POST /auth/login     -> { access_token, user }
 *   GET  /auth/me        -> user
 */

export async function login({ email, password }) {
  if (USE_MOCKS) {
    await mockDelay()
    if (!email || !password) {
      throw { isNormalized: true, status: 400, message: "Credenciales incompletas." }
    }
    setToken(MOCK_TOKEN)
    return { user: { ...MOCK_USER, email }, token: MOCK_TOKEN }
  }

  const { data } = await api.post("/auth/login", { email, password })
  const token = data.access_token || data.token
  setToken(token)
  return { user: data.user, token }
}

export async function register({ nombre, email, password }) {
  if (USE_MOCKS) {
    await mockDelay()
    setToken(MOCK_TOKEN)
    return { user: { ...MOCK_USER, nombre, email }, token: MOCK_TOKEN }
  }

  const { data } = await api.post("/auth/register", { nombre, email, password })
  const token = data.access_token || data.token
  setToken(token)
  return { user: data.user, token }
}

export async function fetchMe() {
  if (USE_MOCKS) {
    await mockDelay(250)
    return MOCK_USER
  }
  const { data } = await api.get("/auth/me")
  return data.user || data
}

export function logout() {
  clearToken()
}
