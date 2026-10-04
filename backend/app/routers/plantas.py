from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.deps import get_current_user
from app.models import Planta
from app.schemas import PlantaIn, PlantaOut

router = APIRouter(prefix="/plantas", tags=["plantas"])

@router.get("", response_model=list[PlantaOut])
def listar_plantas(db: Session = Depends(get_db)):
    """Devuelve el catálogo de plantas desde la base de datos."""
    return db.query(Planta).all()

@router.post("", response_model=PlantaOut, status_code=201, dependencies=[Depends(get_current_user)])
def crear_planta(payload: PlantaIn, db: Session = Depends(get_db)):
    """Permite a los usuarios registrar un cultivo nuevo en el catálogo."""
    nueva_planta = Planta(**payload.model_dump())
    db.add(nueva_planta)
    try:
        db.commit()
        db.refresh(nueva_planta)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Esta planta o ID ya existe en el catálogo.")
    return nueva_planta
