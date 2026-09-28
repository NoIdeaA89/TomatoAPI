from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import models  # noqa: F401  (registra las tablas en Base.metadata)
from app.config import settings
from app.database import Base, engine
from app.routers import auth, plantaciones, plantas


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TomatoAPI",
    description=(
        "API REST que recomienda qué días regar cada plantación según el clima "
        "(Open-Meteo), el tipo de planta, el tipo de suelo y la etapa de desarrollo."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def errores_de_validacion(request: Request, exc: RequestValidationError):
    """Deja los mensajes 422 limpios ({detail: [{msg}]}) para mostrarlos en el frontend."""
    errores = [
        {
            "loc": list(e.get("loc", [])),
            "msg": str(e.get("msg", "")).removeprefix("Value error, "),
            "type": e.get("type"),
        }
        for e in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errores})


app.include_router(auth.router)
app.include_router(plantas.router)
app.include_router(plantaciones.router)


@app.get("/health", tags=["health"])
def health():
    """Usado por Render (y por ti) para saber si el servicio está vivo."""
    return {"status": "ok"}
