import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from './App'

beforeEach(() => {
  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: () =>
        Promise.resolve({
          tipo_planta: 'tomate',
          dias: [
            { fecha: '2026-09-01', recomendable: true, motivo: 'test' },
          ],
        }),
    }),
  )
})

describe('App', () => {
  it('muestra el título', () => {
    render(<App />)
    expect(screen.getByText('Riego Inteligente')).toBeInTheDocument()
  })

  it('pide la recomendación al backend y muestra el resultado', async () => {
    render(<App />)
    fireEvent.click(screen.getByText('Ver recomendación'))

    await waitFor(() => {
      expect(screen.getByText(/Recomendable regar/)).toBeInTheDocument()
    })

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/riego/recomendacion'),
      expect.objectContaining({ method: 'POST' }),
    )
  })
})
