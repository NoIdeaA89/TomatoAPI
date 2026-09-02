from datetime import date, timedelta

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/riego", tags=["riego"])


class RecomendacionRequest(BaseModel):
    tipo_planta: str
    latitud: float
    longitud: float


class DiaRecomendado(BaseModel):
    fecha: date
    recomendable: bool
    motivo: str


class RecomendacionResponse(BaseModel):
    tipo_planta: str
    dias: list[DiaRecomendado]


@router.post("/recomendacion", response_model=RecomendacionResponse)
def recomendar_riego(payload: RecomendacionRequest):
    """
    Placeholder: acá después conectás la API de clima y la API de datos
    de plantas, y calculás días recomendados de verdad.
    """
    hoy = date.today()
    dias = [
        DiaRecomendado(
            fecha=hoy + timedelta(days=i),
            recomendable=(i % 2 == 0),
            motivo="Placeholder: reemplazar con lógica real de clima/planta",
        )
        for i in range(5)
    ]
    return RecomendacionResponse(tipo_planta=payload.tipo_planta, dias=dias)
