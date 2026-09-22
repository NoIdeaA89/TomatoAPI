from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class AgronomoBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    correo: str

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío.")
        return value

    @field_validator("correo")
    @classmethod
    def validate_correo(cls, value: str) -> str:
        value = value.strip()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("El correo no es válido.")
        return value


class AgronomoCreate(AgronomoBase):
    password: str = Field(..., min_length=8)


class AgronomoResponse(AgronomoBase):
    id: UUID
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)


class PlantacionBase(BaseModel):
    planta_externa_id: str | None = None
    zona_ubicacion: str = Field(..., min_length=1)
    tipo_tierra: str = Field(..., min_length=1)
    etapa_desarrollo: str = Field(..., min_length=1)
    ultimo_riego: datetime | None = None

    @field_validator("zona_ubicacion", "tipo_tierra", "etapa_desarrollo")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío.")
        return value


class PlantacionCreate(PlantacionBase):
    pass


class PlantacionUpdate(BaseModel):
    planta_externa_id: str | None = None
    zona_ubicacion: str | None = Field(default=None, min_length=1)
    tipo_tierra: str | None = Field(default=None, min_length=1)
    etapa_desarrollo: str | None = Field(default=None, min_length=1)
    ultimo_riego: datetime | None = None

    @field_validator("zona_ubicacion", "tipo_tierra", "etapa_desarrollo")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío.")
        return value


class PlantacionResponse(PlantacionBase):
    id: UUID
    agronomo_id: UUID
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)