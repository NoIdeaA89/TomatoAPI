from pathlib import Path

import pytest
from sqlalchemy import text

from app.bootstrap import inicializar_bd


@pytest.mark.parametrize("estado", ["sin_fk", "pendiente", "invalida"])
def test_migracion_catalogo_idempotente_y_no_destructiva(test_engine, estado):
    if test_engine.dialect.name != "postgresql":
        pytest.skip("Requiere PostgreSQL")
    inicializar_bd(test_engine)
    schema = test_engine.get_execution_options()["schema_translate_map"][None]
    sql = (Path(__file__).resolve().parents[2] / "db/migrations/001_catalogo_fk.sql").read_text(encoding="utf8")
    with test_engine.connect() as connection:
        connection.execute(text(f'SET search_path TO "{schema}"'))
        connection.execute(text("ALTER TABLE plantaciones DROP CONSTRAINT plantaciones_planta_fkey"))
        connection.execute(text("INSERT INTO users (id,nombre,email,password_hash,creado_en) VALUES ('u','Ana','a@test.local','hash',now())"))
        planta = "desconocida" if estado == "invalida" else "tomate"
        connection.execute(text("""INSERT INTO plantaciones
            (id,user_id,planta,ubicacion,latitud,longitud,tipo_tierra,etapa,creado_en)
            VALUES ('p','u',:planta,'Coquimbo',-29,-71,'franco','floracion',now())"""), {"planta": planta})
        if estado == "pendiente":
            connection.execute(text("""ALTER TABLE plantaciones ADD CONSTRAINT otra_fk
                FOREIGN KEY (planta) REFERENCES plantas(id) NOT VALID"""))
        connection.commit()
        driver = connection.connection.driver_connection
        with driver.cursor() as cursor:
            if estado == "invalida":
                with pytest.raises(Exception) as error:
                    cursor.execute(sql)
                assert error.value.pgcode == "23503"
                driver.rollback()
            else:
                cursor.execute(sql)
                cursor.execute(sql)  # repetir debe conservar la restricción y los datos
        assert connection.execute(text("SELECT planta FROM plantaciones WHERE id='p'")).scalar_one() == planta
        assert connection.execute(text("SELECT count(*) FROM users")).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM plantas")).scalar_one() == 6
        restricciones = connection.execute(text("""SELECT convalidated FROM pg_constraint
            WHERE conrelid = 'plantaciones'::regclass AND contype='f'
            AND confrelid = 'plantas'::regclass""")).scalars().all()
        assert restricciones == ([] if estado == "invalida" else [True])
        connection.rollback()
        connection.execute(text("RESET search_path"))
        connection.commit()
