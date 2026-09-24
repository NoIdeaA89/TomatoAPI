import { createContext, useCallback, useEffect, useMemo, useState } from "react"
import * as authService from "../services/authService.js"
import { getToken, clearToken } from "../services/api.js"

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [initializing, setInitializing] = useState(true)

  // Restaura la sesión si existe un token guardado.
  useEffect(() => {
    let active = true
    async function restore() {
      if (!getToken()) {
        setInitializing(false)
        return
      }
      try {
        const me = await authService.fetchMe()
        if (active) setUser(me)
      } catch {
        clearToken()
      } finally {
        if (active) setInitializing(false)
      }
    }
    restore()
    return () => {
      active = false
    }
  }, [])

  // Si algún request devuelve 401, cerramos sesión localmente.
  useEffect(() => {
    function onUnauthorized() {
      setUser(null)
    }
    window.addEventListener("auth:unauthorized", onUnauthorized)
    return () => window.removeEventListener("auth:unauthorized", onUnauthorized)
  }, [])

  const login = useCallback(async (credentials) => {
    const { user: u } = await authService.login(credentials)
    setUser(u)
    return u
  }, [])

  const register = useCallback(async (payload) => {
    const { user: u } = await authService.register(payload)
    setUser(u)
    return u
  }, [])

  const logout = useCallback(() => {
    authService.logout()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      initializing,
      login,
      register,
      logout,
    }),
    [user, initializing, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
