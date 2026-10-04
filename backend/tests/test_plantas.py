"""Regresiones del catálogo dinámico; toda la BD y el clima son aislados."""
import pytest
from fastapi.testclient import TestClient

from conftest import PLANTACION
from app.main import app


PLANTA = {
    "id": "nalca", "nombre": "Nalca", "especie": "Gunnera tinctoria",
    "kc_ini": 0.6, "kc_mid": 1.15, "kc_end": 0.8,
    "raiz_m": 0.7, "agotamiento": 0.4,
}


def test_creacion_requiere_autenticacion(client):
    assert client.post("/plantas", json=PLANTA).status_code == 401
    assert len(client.get("/plantas").json()) == 6


def test_crear_listar_y_usar_nueva_planta(client, auth):
    r = client.post("/plantas", json=PLANTA, headers=auth)
    assert r.status_code == 201, r.text
    assert r.json() == PLANTA
    assert PLANTA in client.get("/plantas").json()
    r = client.post("/plantaciones", json={**PLANTACION, "planta": "nalca"}, headers=auth)
    assert r.status_code == 201, r.text
    assert r.json()["planta_nombre"] == "Nalca"
    pid = r.json()["id"]
    assert client.get(f"/plantaciones/{pid}/recomendacion", headers=auth).status_code == 200
    assert len(client.get(f"/plantaciones/{pid}/riego", headers=auth).json()["dias"]) == 6
    humedad = client.get(f"/plantaciones/{pid}/humedad", headers=auth).json()
    assert 0 <= humedad["porcentaje"] <= 100


@pytest.mark.parametrize("cambio", [{"id": "otra"}, {"nombre": "Otra"}])
def test_duplicados_no_modifican_catalogo(client, auth, cambio):
    assert client.post("/plantas", json=PLANTA, headers=auth).status_code == 201
    assert client.post("/plantas", json={**PLANTA, **cambio}, headers=auth).status_code == 409
    assert [p for p in client.get("/plantas").json() if p["id"] == "nalca"] == [PLANTA]


@pytest.mark.parametrize("campo,valor", [
    (campo, valor)
    for campo, minimo, maximo in [
        ("kc_ini", 0.1, 2), ("kc_mid", 0.1, 2), ("kc_end", 0.1, 2),
        ("raiz_m", 0.1, 5), ("agotamiento", 0.1, 0.9),
    ]
    for valor in [minimo - 0.01, maximo + 0.01, "NaN", "Infinity", "-Infinity"]
])
def test_parametros_fuera_de_rango(client, auth, campo, valor):
    assert client.post("/plantas", json={**PLANTA, campo: valor}, headers=auth).status_code == 422
    assert len(client.get("/plantas").json()) == 6


@pytest.mark.parametrize("campo", ["id", "nombre", "especie"])
@pytest.mark.parametrize("valor", ["", "   ", "\t\n"])
def test_identificacion_vacia(client, auth, campo, valor):
    assert client.post("/plantas", json={**PLANTA, campo: valor}, headers=auth).status_code == 422
    assert len(client.get("/plantas").json()) == 6


@pytest.mark.parametrize("campo,limite", [("id", 40), ("nombre", 100), ("especie", 100)])
def test_identificacion_demasiado_larga(client, auth, campo, limite):
    assert client.post("/plantas", json={**PLANTA, campo: "x" * (limite + 1)}, headers=auth).status_code == 422


@pytest.mark.parametrize("alto", [False, True])
def test_limites_numericos_y_balance(client, auth, fake_clima, alto):
    limites = {"kc_ini": (0.1, 2), "kc_mid": (0.1, 2), "kc_end": (0.1, 2),
               "raiz_m": (0.1, 5), "agotamiento": (0.1, 0.9)}
    planta = {**PLANTA, **{k: v[int(alto)] for k, v in limites.items()}}
    assert client.post("/plantas", json=planta, headers=auth).status_code == 201
    fake_clima.kwargs_pronostico = {"et0": 100.0}
    r = client.post("/plantaciones", json={**PLANTACION, "planta": "nalca"}, headers=auth)
    assert r.status_code == 201
    pid = r.json()["id"]
    assert 0 <= client.get(f"/plantaciones/{pid}/humedad", headers=auth).json()["porcentaje"] <= 100


def test_planta_inexistente_no_se_persiste(client, auth):
    http = TestClient(app, raise_server_exceptions=False)
    r = http.post("/plantaciones", json={**PLANTACION, "planta": "inexistente"}, headers=auth)
    assert r.status_code == 422, r.text
    assert http.get("/plantaciones", headers=auth).json() == []


def test_actualizar_planta_actualiza_nombre(client, auth):
    assert client.post("/plantas", json=PLANTA, headers=auth).status_code == 201
    otra = {**PLANTA, "id": "otra", "nombre": "Otra"}
    assert client.post("/plantas", json=otra, headers=auth).status_code == 201
    r = client.post("/plantaciones", json={**PLANTACION, "planta": "nalca"}, headers=auth)
    pid = r.json()["id"]
    r = client.put(f"/plantaciones/{pid}", json={**PLANTACION, "planta": "otra"}, headers=auth)
    assert r.status_code == 200
    assert r.json()["planta_nombre"] == "Otra"


def test_actualizacion_invalida_conserva_plantacion(client, auth):
    r = client.post("/plantaciones", json=PLANTACION, headers=auth)
    original = r.json()
    r = client.put(f"/plantaciones/{original['id']}",
                   json={**PLANTACION, "planta": "inexistente", "ubicacion": "Otra ciudad"}, headers=auth)
    assert r.status_code == 422
    actual = client.get(f"/plantaciones/{original['id']}", headers=auth).json()
    assert actual == original

