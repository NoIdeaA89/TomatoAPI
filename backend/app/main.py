from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import riego

app = FastAPI(
    title="API de Riego Inteligente",
    description="Recomienda los días más seguros para regar según clima y tipo de planta",
    version="0.1.0",
)

# Ajustá esto a la URL real de tu frontend en producción (Vercel, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que cualquier frontend (como tu React en el puerto 5173) se conecte
    allow_credentials=True,
    allow_methods=["*"], # Libera los permisos para peticiones POST, GET, PUT, DELETE
    allow_headers=["*"], # Permite el envío de datos en formato JSON
)

app.include_router(riego.router)


@app.get("/health", tags=["health"])
def health_check():
    """Usado por Render (y por vos) para saber si el servicio está vivo."""
    return {"status": "ok"}
