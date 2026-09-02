import { useState } from 'react'
import { obtenerRecomendacion } from './api'

const TIPOS_PLANTA = ['tomate', 'lechuga', 'albahaca', 'pimiento']

function App() {
  const [tipoPlanta, setTipoPlanta] = useState(TIPOS_PLANTA[0])
  const [dias, setDias] = useState([])
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setCargando(true)
    setError(null)
    try {
      // Coordenadas de ejemplo; después las podés tomar de un input o geolocalización
      const data = await obtenerRecomendacion({
        tipoPlanta,
        latitud: -29.95,
        longitud: -71.34,
      })
      setDias(data.dias)
    } catch (err) {
      setError('No se pudo obtener la recomendación. ¿El backend está corriendo?')
    } finally {
      setCargando(false)
    }
  }

  return (
    <main style={{ maxWidth: 480, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h1>Riego Inteligente</h1>

      <form onSubmit={handleSubmit}>
        <label htmlFor="tipo-planta">Tipo de planta</label>
        <select
          id="tipo-planta"
          value={tipoPlanta}
          onChange={(e) => setTipoPlanta(e.target.value)}
        >
          {TIPOS_PLANTA.map((tipo) => (
            <option key={tipo} value={tipo}>
              {tipo}
            </option>
          ))}
        </select>
        <button type="submit" disabled={cargando}>
          {cargando ? 'Consultando...' : 'Ver recomendación'}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      {dias.length > 0 && (
        <ul>
          {dias.map((dia) => (
            <li key={dia.fecha}>
              {dia.fecha}: {dia.recomendable ? 'Recomendable regar' : 'No recomendable'} —{' '}
              {dia.motivo}
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}

export default App
