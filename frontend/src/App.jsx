import { useState, useEffect } from 'react'

const TIPOS_PLANTA = ['tomate', 'lechuga', 'alfalfa']

function App() {
  const [tipoPlanta, setTipoPlanta] = useState(TIPOS_PLANTA[0])
  const [dias, setDias] = useState([])
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  const [plantas, setPlantas] = useState([])
  const [errorPlantas, setErrorPlantas] = useState(null)

  // Cargar tabla al iniciar
  useEffect(() => {
    fetch('http://localhost:8000/riego/plantas')
      .then(response => {
        if (!response.ok) throw new Error('Error en la red')
        return response.json()
      })
      .then(data => setPlantas(data))
      .catch(err => setErrorPlantas('No se pudo cargar la BD.'))
  }, [])

  // Enviar formulario directamente al backend
  async function handleSubmit(e) {
    e.preventDefault()
    setCargando(true)
    setError(null)
    setDias([])
    
    try {
      const response = await fetch('http://localhost:8000/riego/recomendacion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tipo_planta: tipoPlanta,
          latitud: -29.95, 
          longitud: -71.34
        })
      })

      if (!response.ok) {
        throw new Error(`Fallo en la petición: ${response.status}`)
      }

      const data = await response.json()
      setDias(data.dias)
      
    } catch (err) {
      console.error(err)
      setError('No se pudo obtener la recomendación. ¿El backend está corriendo?')
    } finally {
      setCargando(false)
    }
  }

  return (
    <main style={{ maxWidth: 800, margin: '2rem auto', fontFamily: 'sans-serif', padding: '0 1rem' }}>
      
      <section style={{ marginBottom: '3rem' }}>
        <h1>Riego Inteligente</h1>
        <form onSubmit={handleSubmit} style={{ marginBottom: '1.5rem' }}>
          <label htmlFor="tipo-planta" style={{ marginRight: '1rem' }}>Tipo de planta:</label>
          <select
            id="tipo-planta"
            value={tipoPlanta}
            onChange={(e) => setTipoPlanta(e.target.value)}
            style={{ marginRight: '1rem', padding: '0.4rem' }}
          >
            {TIPOS_PLANTA.map((tipo) => (
              <option key={tipo} value={tipo}>
                {tipo}
              </option>
            ))}
          </select>
          <button type="submit" disabled={cargando} style={{ padding: '0.4rem 1rem' }}>
            {cargando ? 'Consultando...' : 'Ver recomendación'}
          </button>
        </form>

        {error && <p role="alert" style={{ color: '#ff4444' }}>{error}</p>}

        {dias.length > 0 && (
          <ul style={{ background: '#2c2c2c', padding: '1.5rem 2.5rem', borderRadius: '8px' }}>
            {dias.map((dia) => (
              <li key={dia.fecha} style={{ marginBottom: '0.5rem', color: '#fff' }}>
                <strong>{dia.fecha}:</strong> {dia.recomendable ? '💧 Regar' : '❌ No regar'} — {dia.motivo}
              </li>
            ))}
          </ul>
        )}
      </section>

      <hr style={{ border: '1px solid #555', marginBottom: '3rem' }} />

      <section>
        <h2>🌱 Catálogo de Plantas (Base de Datos)</h2>
        {errorPlantas && <p style={{ color: '#ff4444' }}>{errorPlantas}</p>}
        
        <table border="1" cellPadding="10" style={{ borderCollapse: 'collapse', width: '100%', borderColor: '#555' }}>
          <thead style={{ backgroundColor: '#222', color: '#fff' }}>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Profundidad Raíz</th>
              <th>Kc Inicial</th>
              <th>Kc Medio</th>
              <th>Kc Final</th>
            </tr>
          </thead>
          <tbody>
            {plantas.length === 0 && !errorPlantas ? (
              <tr><td colSpan="6" style={{ textAlign: 'center' }}>Cargando base de datos...</td></tr>
            ) : (
              plantas.map(planta => (
                <tr key={planta.id_planta}>
                  <td style={{ textAlign: 'center' }}>{planta.id_planta}</td>
                  <td><strong>{planta.nombre_comun}</strong></td>
                  <td style={{ textAlign: 'center' }}>{planta.profundidad_raiz_cm} cm</td>
                  <td style={{ textAlign: 'center' }}>{planta.kc_inicial}</td>
                  <td style={{ textAlign: 'center' }}>{planta.kc_medio}</td>
                  <td style={{ textAlign: 'center' }}>{planta.kc_final}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </main>
  )
}

export default App