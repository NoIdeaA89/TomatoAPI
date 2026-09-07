from pydantic import BaseModel
from datetime import datetime

class ProyectoCreate(BaseModel):
    nombre_sector: str
    id_planta: int
    tipo_suelo: str
    etapa_desarrollo: str
    fecha_ultimo_riego: datetime
    latitud: float
    longitud: float

class DiaRiego(BaseModel):
    fecha: str
    regar: bool
    minutos_bomba: int
    motivo: str