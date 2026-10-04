# Revisión de crearPlanta — 2026-10-04

## Diagnóstico del arranque con el volumen local existente

El backend local falla al arrancar con `UndefinedColumn: column "id" of relation "plantas" does not exist`. Su volumen contiene el esquema SQL original (`id_planta`, `nombre_comun`, `agronomo_id`), que create_all no convierte al esquema del backend actual.

Se encontraron 3 plantas antiguas y 2 sectores, sin agrónomos, usuarios ni plantaciones. Se preparó `db/migrations/000_archivar_esquema_legacy.sql`: conserva las tablas originales en `tomato_legacy_v1` y permite que el backend cree las tablas actuales. Los datos archivados no se importan automáticamente al modelo actual. **La migración se aplicó con autorización del usuario.** Se verificaron las 3 plantas y los 2 sectores archivados, el arranque del backend y la respuesta `{"status":"ok"}` de `/health`; `/plantas` responde con el catálogo actual.

Se agregó un test que prueba archivado, conservación de registros y arranque posterior con catálogo nuevo. La suite completa alcanza **105 tests pasando en PostgreSQL y Python 3.12**.

## Verificación con Docker y PostgreSQL completada

**104 tests pasan con Python 3.12, PostgreSQL 16.14 y las versiones fijadas en requirements.txt.** Esto resuelve las limitaciones anteriores de Python/PostgreSQL. Se probó la suite con esquemas independientes por caso en una base efímera, sin modificar bases ni volúmenes del usuario.

Se verificó carga inicial e idempotencia del catálogo, CRUD y aislamiento entre usuarios, validación y casos extremos, además de tres escenarios de migración: FK ausente, FK con otro nombre pendiente de validar y referencias inválidas. La migración se puede repetir conservando datos; ante referencias inválidas revierte sin eliminar registros. El clima sigue simulado; las pruebas visuales en navegador permanecen pendientes. Se observó una advertencia de deprecación entre Starlette y AnyIO, sin fallos.

Para repetir:

```powershell
docker compose -p tomatoapi-tests -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from tests
docker compose -p tomatoapi-tests -f docker-compose.test.yml down
```

## Correcciones aplicadas

Los resultados siguientes documentan el diagnóstico inicial. Después de corregir la aplicación, la suite completa existente más los casos nuevos pasó: **99 tests, 92% de cobertura**. Dos tests adicionales de inicialización idempotente y edición inválida también pasaron, al igual que los cuatro tests de formulario y catálogo demo ejecutados con `npm.cmd run test:plantas`. La compilación del frontend pasa.

Se agregó carga idempotente del catálogo al arranque, autenticación al POST de plantas, validación de referencias antes de modificar plantaciones, campos de identificación obligatorios y parámetros finitos. El formulario comparte límites con la API, genera IDs acotados y normalizados, y el modo demo mantiene el catálogo en memoria y rechaza duplicados.

`db/migrations/001_catalogo_fk.sql` agrega la FK a PostgreSQL con el esquema del backend anterior, después del arranque que inserta el catálogo. No fue ejecutado contra PostgreSQL. No usar initDB.sql para migrar bases existentes: elimina tablas. La inicialización conserva datos pero create_all no modifica restricciones de tablas antiguas; el script cubre esa actualización de PostgreSQL. SQLite existente recibe catálogo y validación de referencias desde la API, sin reconstruir tablas.

Se mantiene la limitación del entorno Python 3.14 y versiones distintas de requirements.txt. No se ejecutaron pruebas visuales de navegador.

Verificación final: **101 tests del backend y 4 del frontend pasan**. Docker está instalado, pero su motor no está disponible, por lo que no se pudo completar la prueba en PostgreSQL/Python 3.12 con contenedores. Se ajustó además la migración para validar claves foráneas preexistentes pendientes de validación, independientemente de su nombre.

Se revisó el commit `5b85120` contra su padre `991f0e4`. Se añadieron tests, sin modificar código de aplicación ni datos reales.

## Resultados

| Verificación | Resultado |
| --- | --- |
| Suite original, 54 casos | 43 pasan, 11 fallan |
| Nuevos tests del catálogo, 45 casos | 34 pasan, 11 fallan |
| Cobertura de la suite original | 82% |
| `npm.cmd run build` | Correcto |

Los tests usan SQLite en memoria y clima simulado. No se probaron PostgreSQL, una migración de producción ni la interacción visual en navegador. El frontend contiene un App.test.jsx antiguo que importa Vitest y Testing Library, pero package.json no incluye esas dependencias ni un comando test.

El entorno disponible es Python 3.14, FastAPI 0.121.2, Pydantic 2.12.4, SQLAlchemy 2.0.44 y pytest 9.0.3. Las versiones fijadas por el proyecto no pudieron instalarse: psycopg2-binary y pydantic-core requieren compilación y faltan herramientas de C++. Por eso estos resultados deben repetirse en Python 3.12 con las dependencias fijadas antes de aprobar el cambio.

## Hallazgos prioritarios

1. **Alta: falta carga inicial y migración del catálogo.** main.py solo ejecuta create_all, que crea tablas pero no inserta plantas ni migra tablas existentes. El seed solo se ejecuta mediante los scripts de inicialización de Docker; el volumen db_data existente no vuelve a inicializarse. En ejecución local o actualización de una BD existente el catálogo queda vacío. Los 11 fallos originales están relacionados con catálogo vacío, referencias inexistentes y serialización. Además, el test original del catálogo debe actualizar su contrato porque ahora devuelve parámetros agronómicos adicionales.

2. **Alta: planta inexistente produce 500 y puede persistir datos inválidos.** PlantacionIn perdió la validación del catálogo y crear/actualizar no consultan la tabla antes del commit. En SQLite, con las claves foráneas desactivadas, se guarda la referencia inválida y luego planta_rel.nombre falla; en PostgreSQL la FK debería rechazarla, pero falta manejo de IntegrityError. Validar antes de guardar y responder 422, manteniendo la BD intacta. El nuevo test confirma HTTP 500.

3. **Alta: POST /plantas permite escritura anónima.** El endpoint no depende de get_current_user. Una llamada sin token devuelve 201 y modifica el catálogo compartido, aunque la pantalla esté protegida en React. Añadir autenticación al POST.

4. **Media: identificación vacía aceptada.** PlantaIn solo limita longitud máxima. Los nueve casos de id/nombre/especie vacíos, espacios y tabulaciones devuelven 201. Recortar espacios, exigir contenido y definir formato de ID.

5. **Media: formulario y API validan rangos diferentes.** PlantaFormPage.validar solo exige Kc/raíz mayores a cero y agotamiento entre cero y uno. Así permite Kc 0.01 o 3, raíz 6 y agotamiento 0.95, que la API rechaza. noValidate desactiva la validación nativa. Usar exactamente los límites del backend y comprobar números finitos. Hallazgo por revisión de código, sin prueba de navegador.

6. **Media: nombres válidos generan IDs demasiado largos.** El nombre admite 100 caracteres en la API, pero el ID generado directamente a partir del nombre admite 40. Un nombre de 41 letras pasa validar en React y falla al guardar. El formulario tampoco limita especie/nombre a 100 caracteres. Definir un ID estable con longitud acotada y validar las longitudes antes del envío.

7. **Media: creación en modo demo no guarda la planta.** crearPlanta devuelve el payload pero no lo añade a MOCK_PLANTAS; listarPlantas sigue devolviendo el catálogo original. Al navegar a nueva plantación, la especie creada no aparece. Mantener un catálogo mock mutable, compartido por listado y creación, y validar duplicados. Hallazgo por revisión de código.

## Casos que funcionan

- Crear, listar y usar una nueva especie para recomendaciones, plan de seis días y humedad.
- Actualizar una plantación a otra especie devuelve el nombre correcto.
- IDs o nombres duplicados responden 409 y mantienen el catálogo.
- Los 25 casos numéricos fuera de rango, NaN e infinitos responden 422.
- Longitudes superiores a las máximas se rechazan.
- Límites numéricos mínimos y máximos admitidos mantienen humedad entre 0 y 100 con evaporación extrema.

## Reproducción

Desde backend:

```powershell
py -m pytest -p no:cacheprovider --ignore=tests/test_plantas.py --tb=short -q --cov=app --cov-report=term
py -m pytest -p no:cacheprovider tests/test_plantas.py --tb=short -q
```

Desde frontend:

```powershell
npm.cmd run build
```

La branch necesita correcciones antes de considerarse libre de regresiones; superar 60% de cobertura no compensa los fallos funcionales.
