from pathlib import Path

import pytest
from sqlalchemy import text

from app.bootstrap import inicializar_bd


def test_archivar_legacy_conserva_datos_y_permite_arrancar(test_engine):
    if test_engine.dialect.name != "postgresql":
        pytest.skip("Requiere PostgreSQL")
    schema = test_engine.get_execution_options()["schema_translate_map"][None]
    archivo = schema + "_legacy"
    sql = (Path(__file__).resolve().parents[2] / "db/migrations/000_archivar_esquema_legacy.sql").read_text(encoding="utf8")
    sql = sql.replace("public", schema).replace("tomato_legacy_v1", archivo)
    with test_engine.connect() as connection:
        try:
            connection.execute(text(f"CREATE TABLE {schema}.plantas (id_planta serial PRIMARY KEY, nombre_comun text)"))
            connection.execute(text(f"INSERT INTO {schema}.plantas (nombre_comun) VALUES ('Alfalfa')"))
            connection.execute(text(f"CREATE TABLE {schema}.sectores (id_sector serial PRIMARY KEY, id_planta int REFERENCES {schema}.plantas(id_planta))"))
            connection.execute(text(f"INSERT INTO {schema}.sectores (id_planta) VALUES (1)"))
            connection.commit()
            driver = connection.connection.driver_connection
            with driver.cursor() as cursor:
                cursor.execute(sql)
                cursor.execute(sql)
            inicializar_bd(test_engine)
            assert connection.execute(text(f"SELECT nombre_comun FROM {archivo}.plantas")).scalar_one() == "Alfalfa"
            assert connection.execute(text(f"SELECT count(*) FROM {archivo}.sectores")).scalar_one() == 1
            assert connection.execute(text(f"SELECT count(*) FROM {schema}.plantas")).scalar_one() == 6
        finally:
            connection.rollback()
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{archivo}" CASCADE'))
            connection.commit()
