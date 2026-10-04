import test from "node:test"
import assert from "node:assert/strict"
import { readFile } from "node:fs/promises"

test("el catálogo demo conserva plantas y rechaza duplicados", async () => {
  const mockApi = `data:text/javascript,${encodeURIComponent(
    'export const USE_MOCKS = true; export const api = {}; export async function mockDelay() {}'
  )}`
  const source = (await readFile(new URL("./plantacionesService.js", import.meta.url), "utf8"))
    .replace('"./api.js"', JSON.stringify(mockApi))
    .replace('"../mocks/mockData.js"', JSON.stringify(new URL("../mocks/mockData.js", import.meta.url).href))
  const service = await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`)
  const planta = { id: "nalca", nombre: "Nalca", especie: "Gunnera tinctoria",
    kc_ini: 0.6, kc_mid: 1.15, kc_end: 0.8, raiz_m: 0.7, agotamiento: 0.4 }
  await service.crearPlanta(planta)
  assert.deepEqual((await service.listarPlantas()).find((p) => p.id === "nalca"), planta)
  await assert.rejects(service.crearPlanta(planta), (e) => e.status === 409)
  await assert.rejects(service.crearPlanta({ ...planta, id: "otra" }), (e) => e.status === 409)
  const plantacion = await service.crearPlantacion({ planta: "nalca" })
  assert.equal(plantacion.planta_nombre, "Nalca")
})
