import pytest
from datetime import datetime
from uuid import uuid4

from app.schemas import AgronomoCreate, AgronomoResponse, PlantacionCreate, PlantacionUpdate


def test_agronomo_create_valid():
    schema = AgronomoCreate(nombre="Ana", correo="ana@tomatoapi.local", password="secret123")
    assert schema.nombre == "Ana"
    assert schema.correo == "ana@tomatoapi.local"


def test_agronomo_create_email_invalid():
    with pytest.raises(ValueError):
        AgronomoCreate(nombre="Ana", correo="correo_invalido", password="secret123")


def test_agronomo_create_password_too_short():
    with pytest.raises(ValueError):
        AgronomoCreate(nombre="Ana", correo="ana@tomatoapi.local", password="short")


def test_plantacion_create_valid():
    schema = PlantacionCreate(
        planta_externa_id="tomate-001",
        zona_ubicacion="San Miguel",
        tipo_tierra="Franco",
        etapa_desarrollo="Vegetativa",
        ultimo_riego=datetime.now(),
    )
    assert schema.zona_ubicacion == "San Miguel"
    assert schema.tipo_tierra == "Franco"


def test_plantacion_update_partial():
    schema = PlantacionUpdate(zona_ubicacion="Valle Central")
    assert schema.zona_ubicacion == "Valle Central"
    assert schema.tipo_tierra is None


def test_agronomo_response_excludes_password_hash():
    obj = AgronomoResponse(
        id=uuid4(),
        nombre="Ana",
        correo="ana@tomatoapi.local",
        fecha_registro=datetime.now(),
    )
    payload = obj.model_dump()
    assert "password" not in payload
    assert "password_hash" not in payload
