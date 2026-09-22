import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Planta(Base):
    __tablename__ = "plantas"
    id_planta = Column(Integer, primary_key=True, index=True)
    nombre_comun = Column(String, unique=True, index=True)
    profundidad_raiz_cm = Column(Integer)
    kc_inicial = Column(Float)
    kc_medio = Column(Float)
    kc_final = Column(Float)


class Agronomo(Base):
    __tablename__ = "agronomos"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    fecha_registro = Column(DateTime, nullable=False, default=datetime.utcnow)

    plantaciones = relationship("Plantacion", back_populates="agronomo", cascade="all, delete-orphan")


class Plantacion(Base):
    __tablename__ = "plantaciones"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    agronomo_id = Column(UUID(as_uuid=False), ForeignKey("agronomos.id"), nullable=False)
    planta_externa_id = Column(String(50), nullable=True)
    zona_ubicacion = Column(String(150), nullable=False)
    tipo_tierra = Column(String(50), nullable=False)
    etapa_desarrollo = Column(String(50), nullable=False)
    ultimo_riego = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)

    agronomo = relationship("Agronomo", back_populates="plantaciones")


class Sector(Base):
    __tablename__ = "sectores"
    id_sector = Column(Integer, primary_key=True, index=True)
    nombre_sector = Column(String)
    id_planta = Column(Integer, ForeignKey("plantas.id_planta"))
    tipo_suelo = Column(String)
    etapa_desarrollo = Column(String)
    fecha_ultimo_riego = Column(DateTime)
    zona_plantacion_latitud = Column(Float)
    zona_plantacion_longitud = Column(Float)