def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recomendacion_riego(client):
    payload = {
        "tipo_planta": "tomate",
        "latitud": -29.95,
        "longitud": -71.34,
    }
    response = client.post("/riego/recomendacion", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert len(body["dias"]) == 5
    assert [dia["recomendable"] for dia in body["dias"]] == [True, False, False, True, False]
    assert all(dia["fecha"] and dia["motivo"] for dia in body["dias"])


def test_recomendacion_planta_desconocida(client):
    response = client.post(
        "/riego/recomendacion",
        json={"tipo_planta": "desconocida", "latitud": -29.95, "longitud": -71.34},
    )
    assert response.status_code == 404
    assert "desconocida" in response.json()["detail"]
