from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recomendacion_riego():
    payload = {
        "tipo_planta": "tomate",
        "latitud": -29.95,
        "longitud": -71.34,
    }
    response = client.post("/riego/recomendacion", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["tipo_planta"] == "tomate"
    assert len(body["dias"]) == 5
