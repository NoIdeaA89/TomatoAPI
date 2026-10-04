# TomatoAPI — Backend

API REST (FastAPI + PostgreSQL) que recomienda qué días regar cada plantación según el clima,
el tipo de planta, el tipo de suelo y la etapa de desarrollo. Swagger en `/docs`.

## Ejecutar

```bash
# Con Docker (backend + PostgreSQL)
docker compose up --build        # desde la raíz del repo → http://localhost:8000/docs

# Sin Docker
cd backend
pip install -r requirements-dev.txt
uvicorn app.main:app --reload    # usa SQLite (tomatoapi.db) si no defines DATABASE_URL
pytest                           # tests (sin internet: el clima se simula)
```

## Variables de entorno

Para ejecutar los tests con Python 3.12 y PostgreSQL 16 en una base efímera aislada,
desde la raíz del repositorio:

```powershell
docker compose -p tomatoapi-tests -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from tests
docker compose -p tomatoapi-tests -f docker-compose.test.yml down
```

Las pruebas locales siguen usando SQLite en memoria. `TEST_DATABASE_URL` permite
probar PostgreSQL creando y eliminando un esquema aleatorio por caso de prueba.

El backend carga las seis especies iniciales al arrancar, tanto en SQLite como en PostgreSQL,
sin sobrescribir especies ni parámetros existentes. Para una base PostgreSQL creada por la
versión anterior del backend, ejecutar `db/migrations/001_catalogo_fk.sql` después del primer
arranque actualizado para agregar la clave foránea del catálogo. No ejecutar `db/initDB.sql`
sobre una base existente: es un script de inicialización que elimina tablas.

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Cadena de conexión PostgreSQL (Neon). Sin definir: SQLite local. |
| `SECRET_KEY` | Clave para firmar los JWT. **Obligatoria en producción**, larga y aleatoria. |
| `CORS_ORIGINS` | URLs del frontend permitidas, separadas por coma. |
| `ACCESS_TOKEN_MINUTES` | Duración del token (por defecto 1440 = 24 h). |

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/auth/register` · `/auth/login` | Devuelven `{access_token, user}` |
| GET | `/auth/me` | Usuario autenticado |
| GET | `/plantas` | Catálogo de plantas |
| GET · POST | `/plantaciones` | Listar / crear (requiere JWT) |
| GET · PUT · DELETE | `/plantaciones/{id}` | Detalle / editar / eliminar |
| GET | `/plantaciones/{id}/recomendacion` | Estado de hoy: `regar`, `no_regar`, `lluvia`, `humedad_suficiente` |
| GET | `/plantaciones/{id}/riego` | Plan de riego de los próximos 6 días |
| GET | `/plantaciones/{id}/clima` | Pronóstico de 6 días |
| GET | `/plantaciones/{id}/humedad` | Humedad estimada del suelo |
| POST | `/plantaciones/{id}/riego` | Registra que se regó ahora |
| GET | `/health` | Estado del servicio |

## Cómo se decide cuándo regar

Balance hídrico diario del suelo (mm): `humedad = humedad_ayer + lluvia_efectiva − ET0 × Kc`.

- **Clima**: [Open-Meteo](https://open-meteo.com) (gratis, sin API key; datos CC BY 4.0). Entrega lluvia,
  probabilidad de lluvia, temperaturas y evapotranspiración de referencia (ET0).
- **Datos de la planta**: tabla local en `app/services/catalogo.py` con coeficientes de cultivo (Kc),
  profundidad de raíz y agotamiento permitido, aproximados de FAO-56. Cambian según la etapa.
- **Suelo**: agua útil por tipo de tierra (arenoso, franco, limoso, arcilloso).
- Se parte con el suelo a capacidad de campo el día del último riego registrado (o de la creación
  de la plantación). Se recomienda regar cuando la humedad cae bajo el umbral de la planta, salvo que
  llueva hoy, se pronostique lluvia fuerte mañana o el suelo esté saturado por lluvias recientes.

Es un modelo simplificado para un proyecto académico: sirve como apoyo, no reemplaza el criterio
de un agrónomo.
