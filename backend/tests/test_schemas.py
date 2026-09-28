import pytest
from datetime import datetime

from app.schemas import RegisterIn, UserOut, PlantacionIn

def test_agronomo_create_valid():
    schema = RegisterIn(nombre="Ana", email="ana@tomatoapi.local", password="secret123")
    assert schema.nombre == "Ana"
    assert schema.email == "ana@tomatoapi.local"

def test_agronomo_create_email_invalid():
    with pytest.raises(ValueError):
        RegisterIn(nombre="Ana", email="correo_invalido", password="secret123")

def test_agronomo_create_password_too_short():
    with pytest.raises(ValueError):
        RegisterIn(nombre="Ana", email="ana@tomatoapi.local", password="short")

def test_plantacion_create_valid():
    schema = PlantacionIn(
        planta="tomate",
        ubicacion="San Miguel",
        tipo_tierra="franco",
        etapa="vegetativa",
        ultimo_riego=datetime.now(),
    )
    assert schema.ubicacion == "San Miguel"
    assert schema.tipo_tierra == "franco"

def test_agronomo_response_excludes_password_hash():
    obj = UserOut(
        id="1234-abcd",
        nombre="Ana",
        email="ana@tomatoapi.local"
    )
    payload = obj.model_dump()
    assert "password" not in payload
    assert "password_hash" not in payload