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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(riego.router)


@app.get("/health", tags=["health"])
def health_check():
    """Usado por Render (y por vos) para saber si el servicio está vivo."""
    return {"status": "ok"}
