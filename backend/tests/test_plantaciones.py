from datetime import datetime, timedelta, timezone

from conftest import PLANTACION, registrar


def _crear(client, auth, **cambios):
    r = client.post("/plantaciones", json={**PLANTACION, **cambios}, headers=auth)
    assert r.status_code == 201, r.text
    return r.json()


def test_todo_requiere_autenticacion(client):
    assert client.get("/plantaciones").status_code == 401
    assert client.post("/plantaciones", json=PLANTACION).status_code == 401
    assert client.get("/plantaciones/x/clima").status_code == 401


def test_catalogo_de_plantas(client):
    r = client.get("/plantas")
    assert r.status_code == 200
    plantas = {p["id"]: p for p in r.json()}
    assert len(plantas) == 6
    assert plantas["tomate"] == {"id": "tomate", "nombre": "Tomate", "especie": "Solanum lycopersicum"}


def test_crear_plantacion(client, auth):
    p = _crear(client, auth)
    assert isinstance(p["id"], str) and p["id"]
    assert p["planta"] == "tomate"
    assert p["planta_nombre"] == "Tomate"
    assert p["ubicacion"] == "Coquimbo, Chile"
    assert p["tipo_tierra"] == "franco"
    assert p["etapa"] == "floracion"
    assert p["estado"] == "humedad_suficiente"   # recién creada: suelo a capacidad de campo
    assert p["proximo_riego"] is None
    assert p["creado_en"]


def test_crear_con_datos_invalidos(client, auth):
    for cambio in ({"planta": "banano"}, {"tipo_tierra": "roca"}, {"etapa": "cosecha"}, {"ubicacion": " "}):
        r = client.post("/plantaciones", json={**PLANTACION, **cambio}, headers=auth)
        assert r.status_code == 422, cambio


def test_crear_con_ubicacion_inexistente(client, auth):
    r = client.post("/plantaciones", json={**PLANTACION, "ubicacion": "Lugar Inexistente"}, headers=auth)
    assert r.status_code == 422
    assert "ubicación" in r.json()["detail"]


def test_listar_solo_las_propias(client, auth):
    propia = _crear(client, auth)
    otro = registrar(client, email="beto@example.com", nombre="Beto")
    assert client.get("/plantaciones", headers=otro).json() == []
    lista = client.get("/plantaciones", headers=auth).json()
    assert [p["id"] for p in lista] == [propia["id"]]


def test_no_se_puede_acceder_a_plantaciones_ajenas(client, auth):
    propia = _crear(client, auth)
    otro = registrar(client, email="beto@example.com", nombre="Beto")
    pid = propia["id"]
    assert client.get(f"/plantaciones/{pid}", headers=otro).status_code == 404
    assert client.put(f"/plantaciones/{pid}", json=PLANTACION, headers=otro).status_code == 404
    assert client.delete(f"/plantaciones/{pid}", headers=otro).status_code == 404
    assert client.get(f"/plantaciones/{pid}/clima", headers=otro).status_code == 404


def test_obtener_actualizar_y_eliminar(client, auth):
    pid = _crear(client, auth)["id"]

    r = client.get(f"/plantaciones/{pid}", headers=auth)
    assert r.status_code == 200 and r.json()["id"] == pid

    r = client.put(
        f"/plantaciones/{pid}",
        json={**PLANTACION, "planta": "lechuga", "etapa": "vegetativa", "ubicacion": "La Serena, Chile"},
        headers=auth,
    )
    assert r.status_code == 200
    assert r.json()["planta_nombre"] == "Lechuga"
    assert r.json()["etapa"] == "vegetativa"
    assert r.json()["ubicacion"] == "La Serena, Chile"

    assert client.delete(f"/plantaciones/{pid}", headers=auth).status_code == 204
    assert client.get(f"/plantaciones/{pid}", headers=auth).status_code == 404
    assert client.delete(f"/plantaciones/{pid}", headers=auth).status_code == 404


def test_actualizar_con_ubicacion_inexistente(client, auth):
    pid = _crear(client, auth)["id"]
    r = client.put(f"/plantaciones/{pid}", json={**PLANTACION, "ubicacion": "Lugar Inexistente"}, headers=auth)
    assert r.status_code == 422


def test_endpoints_de_monitoreo_tienen_la_forma_que_espera_el_frontend(client, auth):
    pid = _crear(client, auth)["id"]

    rec = client.get(f"/plantaciones/{pid}/recomendacion", headers=auth).json()
    assert set(rec) == {"estado", "titulo", "motivo"}
    assert rec["estado"] in {"regar", "no_regar", "lluvia", "humedad_suficiente"}

    riego = client.get(f"/plantaciones/{pid}/riego", headers=auth).json()
    assert len(riego["dias"]) == 6
    assert set(riego["dias"][0]) == {"fecha", "regar", "motivo"}
    assert isinstance(riego["dias"][0]["regar"], bool)

    clima = client.get(f"/plantaciones/{pid}/clima", headers=auth).json()
    assert len(clima["dias"]) == 6
    assert set(clima["dias"][0]) == {
        "fecha", "temp_min", "temp_max", "condicion", "prob_lluvia", "precipitacion"
    }
    assert clima["dias"][0]["condicion"] in {"soleado", "parcialmente_nublado", "nublado", "lluvia"}

    hum = client.get(f"/plantaciones/{pid}/humedad", headers=auth).json()
    assert set(hum) == {"porcentaje", "nivel", "dias_restantes", "detalle"}
    assert 0 <= hum["porcentaje"] <= 100
    assert hum["nivel"] in {"alta", "media", "baja"}


def test_recomienda_regar_y_registrar_riego_reinicia_el_balance(client, auth, fake_clima):
    fake_clima.kwargs_pronostico = {"et0": 6.0}   # días muy secos y con mucha evaporación
    hace_8_dias = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
    p = _crear(client, auth, ultimo_riego=hace_8_dias)
    pid = p["id"]

    assert p["estado"] == "regar"
    assert p["proximo_riego"] is not None
    rec = client.get(f"/plantaciones/{pid}/recomendacion", headers=auth).json()
    assert rec["estado"] == "regar" and rec["titulo"] == "Regar hoy"
    assert client.get(f"/plantaciones/{pid}/humedad", headers=auth).json()["nivel"] == "baja"

    r = client.post(f"/plantaciones/{pid}/riego", headers=auth)
    assert r.status_code == 200
    assert r.json()["ultimo_riego"] is not None
    assert r.json()["estado"] == "humedad_suficiente"


def test_lluvia_pronosticada_evita_el_riego(client, auth, fake_clima):
    fake_clima.kwargs_pronostico = {"et0": 6.0, "lluvia": {0: 9.0}}
    hace_8_dias = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
    p = _crear(client, auth, ultimo_riego=hace_8_dias)
    assert p["estado"] == "lluvia"


def test_si_el_clima_falla_el_listado_sigue_funcionando(client, auth, fake_clima):
    pid = _crear(client, auth)["id"]
    fake_clima.caido = True

    lista = client.get("/plantaciones", headers=auth)
    assert lista.status_code == 200
    assert lista.json()[0]["estado"] is None

    r = client.get(f"/plantaciones/{pid}/clima", headers=auth)
    assert r.status_code == 502
    assert "clima" in r.json()["detail"]
