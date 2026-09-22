from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from pydantic import BaseModel
from app.database import get_db
from app.models import Planta

router = APIRouter(prefix="/riego", tags=["riego"])

# 1. Esquemas para validar lo que entra y sale hacia React
class RecomendacionRequest(BaseModel):
    tipo_planta: str
    latitud: float
    longitud: float

class DiaRecomendado(BaseModel):
    fecha: str
    recomendable: bool
    motivo: str

class RecomendacionResponse(BaseModel):
    dias: list[DiaRecomendado]

# 2. Endpoint de la tabla (Ya lo tienes funcionando)
@router.get("/plantas")
def obtener_plantas(db: Session = Depends(get_db)):
    return db.query(Planta).all()

# 3. El nuevo cerebro de recomendaciones
@router.post("/recomendacion", response_model=RecomendacionResponse)
async def recomendar_riego(payload: RecomendacionRequest, db: Session = Depends(get_db)):
    
    # Buscamos la planta en la base de datos (ilike ignora mayúsculas/minúsculas)
    planta = db.query(Planta).filter(Planta.nombre_comun.ilike(payload.tipo_planta)).first()
    
    if not planta:
        raise HTTPException(status_code=404, detail=f"La planta '{payload.tipo_planta}' no está en nuestro catálogo.")

    # Lógica agronómica matemática:
    # Raíces profundas retienen humedad más días que raíces superficiales.
    dias_retencion = 3 if planta.profundidad_raiz_cm >= 60 else 1

    hoy = date.today()
    dias_recomendados = []

    for i in range(5):
        fecha_actual = hoy + timedelta(days=i)
        
        # TODO: Aquí inyectaremos la API de clima usando payload.latitud y payload.longitud
        lluvia_pronosticada = False 

        if lluvia_pronosticada:
            dias_recomendados.append(DiaRecomendado(
                fecha=fecha_actual.strftime("%Y-%m-%d"),
                recomendable=False,
                motivo="Lluvia pronosticada en la zona. Riego suspendido."
            ))
        elif i % dias_retencion == 0:
            dias_recomendados.append(DiaRecomendado(
                fecha=fecha_actual.strftime("%Y-%m-%d"),
                recomendable=True,
                motivo=f"Requiere riego. Raíz a {planta.profundidad_raiz_cm}cm (Kc: {planta.kc_medio})."
            ))
        else:
            dias_recomendados.append(DiaRecomendado(
                fecha=fecha_actual.strftime("%Y-%m-%d"),
                recomendable=False,
                motivo="El suelo aún conserva humedad del riego anterior."
            ))

    return RecomendacionResponse(dias=dias_recomendados)