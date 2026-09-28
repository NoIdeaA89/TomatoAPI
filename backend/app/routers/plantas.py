from fastapi import APIRouter

from app.schemas import PlantaOut
from app.services.catalogo import CATALOGO

router = APIRouter(prefix="/plantas", tags=["plantas"])


@router.get("", response_model=list[PlantaOut])
def listar_plantas():
    """Catálogo de plantas disponibles para crear una plantación."""
    return [PlantaOut(id=p.id, nombre=p.nombre, especie=p.especie) for p in CATALOGO.values()]
