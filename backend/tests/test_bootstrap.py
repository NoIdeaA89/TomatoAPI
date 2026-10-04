from sqlalchemy.orm import Session

from app.bootstrap import inicializar_bd
from app.models import Planta


def test_inicializacion_repetida_conserva_parametros_y_especies(test_engine):
    engine = test_engine
    inicializar_bd(engine)
    with Session(engine) as db:
        db.get(Planta, "tomate").kc_mid = 1.9
        db.add(Planta(id="nalca", nombre="Nalca", especie="Gunnera tinctoria",
                      kc_ini=0.6, kc_mid=1.15, kc_end=0.8, raiz_m=0.7, agotamiento=0.4))
        db.commit()
    inicializar_bd(engine)
    with Session(engine) as db:
        assert db.query(Planta).count() == 7
        assert db.get(Planta, "tomate").kc_mid == 1.9
        assert db.get(Planta, "nalca").nombre == "Nalca"
