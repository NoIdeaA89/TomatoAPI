import { useCallback, useEffect, useState } from "react"

/* Hook genérico para peticiones asíncronas de solo lectura.
 * Maneja los tres estados clave: loading, error y data.
 *
 *   const { data, loading, error, reload } = useAsync(() => listar(), [deps])
 */
export function useAsync(asyncFn, deps = [], { immediate = true } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(immediate)
  const [error, setError] = useState(null)

  const run = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await asyncFn()
      setData(result)
      return result
    } catch (err) {
      setError(err?.message || "Ocurrió un error al cargar los datos.")
      throw err
    } finally {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    if (immediate) run().catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [run])

  return { data, loading, error, reload: run, setData }
}
