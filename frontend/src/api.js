const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function obtenerRecomendacion({ tipoPlanta, latitud, longitud }) {
  const response = await fetch(`${API_URL}/riego/recomendacion`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tipo_planta: tipoPlanta,
      latitud,
      longitud,
    }),
  })

  if (!response.ok) {
    throw new Error(`Error del servidor: ${response.status}`)
  }

  return response.json()
}
