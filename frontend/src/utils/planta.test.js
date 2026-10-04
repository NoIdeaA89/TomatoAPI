import test from "node:test"
import assert from "node:assert/strict"
import { validarPlanta, generarIdPlanta } from "./planta.js"

const planta = { nombre: "Nalca", especie: "Gunnera tinctoria", kc_ini: "0.6",
  kc_mid: "1.15", kc_end: "0.8", raiz_m: "0.7", agotamiento: "0.4" }

test("acepta parámetros válidos y límites inclusivos", () => {
  assert.deepEqual(validarPlanta(planta), {})
  assert.deepEqual(validarPlanta({ ...planta, kc_ini: "0.1", kc_mid: "2", raiz_m: "5", agotamiento: "0.9" }), {})
})

test("rechaza vacíos, números no finitos y parámetros fuera de rango", () => {
  for (const [campo, valores] of Object.entries({
    kc_ini: ["", " ", "NaN", "Infinity", "0.01", "3"],
    raiz_m: ["0", "6"], agotamiento: ["0.05", "0.95"],
    nombre: [" ", "x".repeat(101)], especie: ["", "x".repeat(101)],
  })) {
    for (const valor of valores) assert.ok(validarPlanta({ ...planta, [campo]: valor })[campo])
  }
})

test("IDs válidos con acentos, símbolos y nombres largos", () => {
  assert.equal(generarIdPlanta(" Maíz dulce "), "maiz_dulce")
  for (const nombre of ["x".repeat(100), "🌱", "Tomate / cherry"]) {
    const id = generarIdPlanta(nombre)
    assert.ok(id.length <= 40)
    assert.match(id, /^[a-z0-9_]+$/)
  }
  assert.notEqual(generarIdPlanta("x".repeat(100)), generarIdPlanta("x".repeat(100)))
})
