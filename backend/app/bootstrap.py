"""Inicialización no destructiva del catálogo para bases nuevas y existentes."""
from dataclasses import asdict

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.database import Base
from app.models import Planta
from app.services.catalogo import CATALOGO


def inicializar_bd(engine):
    Base.metadata.create_all(bind=engine)
    insertar = sqlite_insert if engine.dialect.name == "sqlite" else pg_insert
    with engine.begin() as connection:
        # No sobrescribir especies ni parámetros previamente registrados.
        connection.execute(
            insertar(Planta).values([asdict(p) for p in CATALOGO.values()])
            .on_conflict_do_nothing()
        )
