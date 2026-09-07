from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
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