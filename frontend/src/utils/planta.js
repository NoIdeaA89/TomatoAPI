export const RANGOS_PLANTA = {
  kc_ini: [0.1, 2], kc_mid: [0.1, 2], kc_end: [0.1, 2],
  raiz_m: [0.1, 5], agotamiento: [0.1, 0.9],
}

export function validarPlanta(form) {
  const errores = {}
  for (const campo of ["nombre", "especie"]) {
    const texto = form[campo].trim()
    if (!texto || texto.length > 100) errores[campo] = "Ingresa entre 1 y 100 caracteres."
  }
  for (const [campo, [min, max]] of Object.entries(RANGOS_PLANTA)) {
    const valor = Number(form[campo])
    if (!String(form[campo]).trim() || !Number.isFinite(valor) || valor < min || valor > max) {
      errores[campo] = `Debe estar entre ${min} y ${max}.`
    }
  }
  return errores
}

export function generarIdPlanta(nombre) {
  const base = nombre.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "planta"
  // Conservar un sufijo único cuando el nombre no cabe en el identificador.
  return base.length <= 40 ? base : `${base.slice(0, 27)}_${crypto.randomUUID().slice(0, 12).replace(/-/g, "_")}`
}
