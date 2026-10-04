import re
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

TipoTierra = Literal["arenoso", "arcilloso", "limoso", "franco"]
Etapa = Literal["germinacion", "inicial", "vegetativa", "floracion", "fructificacion", "maduracion"]


# ---------- Auth ----------
def _validar_email(v: str) -> str:
    v = v.strip().lower()
    if not _EMAIL_RE.match(v):
        raise ValueError("Correo no válido.")
    return v


class RegisterIn(BaseModel):
    nombre: str = Field(max_length=120)
    email: str = Field(max_length=255)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("nombre")
    @classmethod
    def _nombre(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Ingresa tu nombre.")
        return v

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return _validar_email(v)


class LoginIn(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(max_length=128)

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return v.strip().lower()


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nombre: str
    email: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Plantas y plantaciones ----------
class PlantaIn(BaseModel):
    id: str = Field(max_length=40, description="Ej: nalca, tomate_cherry")
    nombre: str = Field(max_length=100)
    especie: str = Field(max_length=100)
    kc_ini: float = Field(ge=0.1, le=2.0)
    kc_mid: float = Field(ge=0.1, le=2.0)
    kc_end: float = Field(ge=0.1, le=2.0)
    raiz_m: float = Field(ge=0.1, le=5.0)
    agotamiento: float = Field(ge=0.1, le=0.9)

class PlantaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    nombre: str
    especie: str
    kc_ini: float
    kc_mid: float
    kc_end: float
    raiz_m: float
    agotamiento: float


class PlantacionIn(BaseModel):
    planta: str
    ubicacion: str = Field(max_length=160)
    tipo_tierra: TipoTierra
    etapa: Etapa
    ultimo_riego: Optional[datetime] = None

    @field_validator("ubicacion")
    @classmethod
    def _ubicacion(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Ingresa la ubicación.")
        return v


class PlantacionOut(BaseModel):
    id: str
    planta: str
    planta_nombre: str
    ubicacion: str
    tipo_tierra: str
    etapa: str
    ultimo_riego: Optional[datetime] = None
    proximo_riego: Optional[datetime] = None
    estado: Optional[str] = None
    creado_en: datetime


# ---------- Monitoreo ----------
class RecomendacionOut(BaseModel):
    estado: str
    titulo: str
    motivo: str


class DiaRiegoOut(BaseModel):
    fecha: datetime
    regar: bool
    motivo: str


class RiegoOut(BaseModel):
    dias: list[DiaRiegoOut]


class DiaClimaOut(BaseModel):
    fecha: datetime
    temp_min: int
    temp_max: int
    condicion: str
    prob_lluvia: int
    precipitacion: float


class ClimaOut(BaseModel):
    dias: list[DiaClimaOut]


class HumedadOut(BaseModel):
    porcentaje: int
    nivel: str
    dias_restantes: int
    detalle: str
