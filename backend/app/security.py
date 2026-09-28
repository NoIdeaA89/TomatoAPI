import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from app.config import settings

_ITERACIONES = 600_000  # recomendación OWASP para PBKDF2-HMAC-SHA256


def hash_password(password: str) -> str:
    sal = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), sal, _ITERACIONES)
    return f"pbkdf2_sha256${_ITERACIONES}${sal.hex()}${dk.hex()}"


def verify_password(password: str, guardado: str) -> bool:
    try:
        algoritmo, iteraciones, sal_hex, hash_hex = guardado.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(sal_hex), int(iteraciones)
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(dk.hex(), hash_hex)


def create_access_token(user_id: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    sub = payload.get("sub")
    return sub if isinstance(sub, str) else None
