from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credenciales: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credenciales is None:
        raise HTTPException(status_code=401, detail="No autenticado.")
    user_id = decode_access_token(credenciales.credentials)
    user = db.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada.")
    return user
