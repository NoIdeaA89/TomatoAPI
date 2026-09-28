from datetime import datetime, timezone

import pytest
from fakes import pronostico_sintetico
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, crear_engine, get_db
from app.main import app
from app.services.clima import ClimaError, UbicacionNoEncontrada, get_clima_client


class FakeClima:
    """Reemplaza a Open-Meteo: sin red y con datos controlados por cada test."""

    def __init__(self):
        self.kwargs_pronostico: dict = {}
        self.caido = False
        self.desconocidas = {"lugar inexistente"}

    def geocodificar(self, ubicacion: str):
        if ubicacion.strip().lower() in self.desconocidas:
            raise UbicacionNoEncontrada(ubicacion)
        return (-29.95, -71.34)

    def pronostico(self, latitud: float, longitud: float):
        if self.caido:
            raise ClimaError("servicio caído")
        hoy = datetime.now(timezone.utc).date()
        return pronostico_sintetico(hoy, **self.kwargs_pronostico)


@pytest.fixture()
def fake_clima():
    return FakeClima()


@pytest.fixture()
def client(fake_clima):
    engine = crear_engine("sqlite://")  # base en memoria, aislada por test
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_clima_client] = lambda: fake_clima
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()


def registrar(client, email="ana@example.com", nombre="Ana Rojas"):
    r = client.post(
        "/auth/register", json={"nombre": nombre, "email": email, "password": "secreto1"}
    )
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def auth(client):
    return registrar(client)


PLANTACION = {
    "planta": "tomate",
    "ubicacion": "Coquimbo, Chile",
    "tipo_tierra": "franco",
    "etapa": "floracion",
}
