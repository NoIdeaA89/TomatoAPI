# Sistema de Gestión de Riego Agrícola

## Descripción
Página web para la gestión de riego agrícola. Permite a un agrónomo ingresar datos iniciales (tipo de tierra, último riego, tipo de planta, zona, etapa de desarrollo) y obtener un calendario de riego con aspersores. El sistema evalúa el clima, omite el riego en días de lluvia y calcula el tiempo de humedad del terreno basado en el catálogo de plantas de un supermercado.

## Arquitectura y Stack Tecnológico
* **Patrón:** Monolito (Frontend y Backend independientes, comunicación vía REST API).
* **Frontend:** React.
* **Backend:** Python con FastAPI (tomatoAPI).
* **Base de Datos:** PostgreSQL.
* **Documentación de API:** Swagger.

## Estructura del Proyecto
```text
/
├── .github/workflows/   # Pipeline de CI/CD
├── backend/             # Código fuente FastAPI y pruebas
├── frontend/            # Código fuente React
└── docker-compose.yml   # Orquestación de contenedores
```

## Configuración y Ejecución (Docker)
El backend está completamente dockerizado. Para levantar el entorno local:

1. Configurar las variables de entorno en el archivo `.env`.
2. Construir y levantar los contenedores:
   ```bash
   docker compose up -d --build
   ```
3. La documentación de la API (Swagger) estará disponible en la ruta configurada (ej. `http://localhost:8000/docs`).

## Pruebas (Testing)
El proyecto requiere un mínimo de 60% de cobertura de código (coverage) en el backend. Las pruebas se ejecutan mediante `pytest` directamente en el contenedor:

```bash
docker compose exec backend pytest --cov=.
```

## Integración Continua (CI/CD)
El repositorio utiliza GitHub Actions. El pipeline está configurado para:
1. Ejecutar las pruebas automatizadas en cada subida de código.
2. Validar que la cobertura cumpla con el estándar mínimo del 60%.
3. Ejecutar el autodespliegue del sistema en el entorno de producción.
