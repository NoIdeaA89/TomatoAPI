from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import Planta
from app.schemas import ProyectoCreate, DiaRiego

router = APIRouter(prefix="/riego", tags=["riego"])

# Diccionario de retención hídrica por tipo de suelo (Días que dura la humedad)
RETENCION_SUELO = {
    "arenoso": 1,   # Drena rápido, riegos diarios
    "franco": 2,    # Retención equilibrada
    "limoso": 3,    # Retención moderada-alta
    "arcilloso": 4  # Retiene mucha agua, riegos espaciados
}

@router.post("/simular", response_model=list[DiaRiego])
def simular_riego_proyecto(proyecto: ProyectoCreate, db: Session = Depends(get_db)):
    # 1. Buscar la biología de la planta seleccionada en la BD
    planta = db.query(Planta).filter(Planta.id_planta == proyecto.id_planta).first()
    
    if not planta:
        raise HTTPException(status_code=404, detail="Planta no encontrada en el catálogo")

    # 2. Extraer propiedades del suelo
    tipo_suelo = proyecto.tipo_suelo.lower()
    dias_humedad = RETENCION_SUELO.get(tipo_suelo, 2) # Franco como valor por defecto

    # 3. Calcular tiempo de hardware (Bomba Pentax CHT350)
    # Raíces profundas requieren riegos más largos para saturar la tierra hasta abajo
    minutos_base = 30 + (planta.profundidad_raiz_cm // 10) * 5

    calendario = []
    fecha_actual = proyecto.fecha_ultimo_riego
    
    # 4. Proyectar los próximos 5 días 
    for i in range(1, 6):
        fecha_actual += timedelta(days=1)
        
        # TODO: Conectar con httpx a la API del clima para la zona (ej. Altovalsol)
        pronostico_lluvia_mm = 0 # Valor simulado temporalmente
        
        if pronostico_lluvia_mm > 5:
            calendario.append(DiaRiego(
                fecha=fecha_actual.strftime("%Y-%m-%d"),
                regar=False,
                minutos_bomba=0,
                motivo=f"Lluvia de {pronostico_lluvia_mm}mm. Riego de aspersores Xcel Wobbler suspendido."
            ))
        elif i % dias_humedad == 0:
            calendario.append(DiaRiego(
                fecha=fecha_actual.strftime("%Y-%m-%d"),
                regar=True,
                minutos_bomba=minutos_base,
                motivo=f"Humedad agotada tras {dias_humedad} día(s) en suelo {tipo_suelo}."
            ))
        else:
             calendario.append(DiaRiego(
                fecha=fecha_actual.strftime("%Y-%m-%d"),
                regar=False,
                minutos_bomba=0,
                motivo=f"Suelo {tipo_suelo} mantiene humedad. Raíz a {planta.profundidad_raiz_cm}cm."
            ))
            
    return calendario