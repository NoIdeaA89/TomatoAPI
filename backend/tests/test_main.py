from typing import get_args

from app.schemas import Etapa, TipoTierra
from app.services.catalogo import AWC_MM_POR_M, FACTOR_RAIZ_ETAPA


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_swagger_disponible(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_contrato_con_el_frontend(client):
    """Todos los endpoints que llama el frontend existen con el método correcto."""
    paths = client.get("/openapi.json").json()["paths"]
    esperados = {
        "/auth/register": {"post"},
        "/auth/login": {"post"},
        "/auth/me": {"get"},
        "/plantas": {"get"},
        "/plantaciones": {"get", "post"},
        "/plantaciones/{plantacion_id}": {"get", "put", "delete"},
        "/plantaciones/{plantacion_id}/recomendacion": {"get"},
        "/plantaciones/{plantacion_id}/riego": {"get", "post"},
        "/plantaciones/{plantacion_id}/clima": {"get"},
        "/plantaciones/{plantacion_id}/humedad": {"get"},
    }
    for ruta, metodos in esperados.items():
        assert ruta in paths, f"Falta {ruta}"
        assert metodos <= set(paths[ruta]), f"{ruta} debería soportar {metodos}"


def test_cors_permite_el_frontend_local(client):
    r = client.options(
        "/plantaciones",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_opciones_del_esquema_coinciden_con_el_catalogo():
    assert set(get_args(TipoTierra)) == set(AWC_MM_POR_M)
    assert set(get_args(Etapa)) == set(FACTOR_RAIZ_ETAPA)
