from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_y_verificacion_de_password():
    guardado = hash_password("secreto1")
    assert "secreto1" not in guardado
    assert verify_password("secreto1", guardado)
    assert not verify_password("otra-clave", guardado)


def test_hash_usa_sal_distinta_cada_vez():
    assert hash_password("secreto1") != hash_password("secreto1")


def test_hash_corrupto_no_verifica():
    assert not verify_password("x", "basura")
    assert not verify_password("x", "md5$1$aa$bb")


def test_token_ida_y_vuelta():
    assert decode_access_token(create_access_token("user-123")) == "user-123"


def test_token_invalido_o_manipulado():
    assert decode_access_token("no-es-un-jwt") is None
    otro = jwt.encode({"sub": "u"}, "otra-clave-distinta-de-32-bytes-o-mas!!", algorithm="HS256")
    assert decode_access_token(otro) is None


def test_token_expirado():
    vencido = jwt.encode(
        {"sub": "u", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key,
        algorithm="HS256",
    )
    assert decode_access_token(vencido) is None
