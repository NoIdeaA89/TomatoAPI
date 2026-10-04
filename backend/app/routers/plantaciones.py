from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Plantacion, User
from app.schemas import (
    ClimaOut,
    DiaClimaOut,
    DiaRiegoOut,
    HumedadOut,
    PlantacionIn,
    PlantacionOut,
    RecomendacionOut,
    RiegoOut,
)
from app.services.catalogo import CATALOGO
from app.services.clima import ClimaError, OpenMeteoClient, UbicacionNoEncontrada, get_clima_client
from app.services.riego import DIAS_PLAN, Evaluacion, Pronostico, evaluar, fecha_local

router = APIRouter(
    prefix="/plantaciones",
    tags=["plantaciones"],
    dependencies=[Depends(get_current_user)],
)


# ---------- helpers ----------
def _utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _mediodia(d: date) -> datetime:
    """Mediodía UTC: evita que el navegador muestre el día anterior por zona horaria."""
    return datetime(d.year, d.month, d.day, 12, 0, tzinfo=timezone.utc)


def _obtener(db: Session, user: User, plantacion_id: str) -> Plantacion:
    p = db.get(Plantacion, plantacion_id)
    if p is None or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="Plantación no encontrada.")
    return p


def _geocodificar(clima: OpenMeteoClient, ubicacion: str) -> tuple[float, float]:
    try:
        return clima.geocodificar(ubicacion)
    except UbicacionNoEncontrada:
        raise HTTPException(
            status_code=422,
            detail="No se encontró la ubicación indicada. Prueba con el formato 'Ciudad, País'.",
        )
    except ClimaError:
        raise HTTPException(
            status_code=502,
            detail="No se pudo verificar la ubicación en este momento. Inténtalo nuevamente.",
        )


def _pronostico(clima: OpenMeteoClient, p: Plantacion) -> Pronostico:
    try:
        return clima.pronostico(p.latitud, p.longitud)
    except ClimaError:
        raise HTTPException(
            status_code=502,
            detail="No se pudo obtener el pronóstico del clima. Inténtalo nuevamente en unos minutos.",
        )


def _evaluar(p: Plantacion, pron: Pronostico) -> Evaluacion:
    base = fecha_local(p.ultimo_riego or p.creado_en, pron.utc_offset_segundos)
    try:
        return evaluar(pron, CATALOGO[p.planta], p.tipo_tierra, p.etapa, base)
    except ValueError:
        raise HTTPException(status_code=502, detail="El pronóstico recibido está incompleto.")


def _evaluar_seguro(clima: OpenMeteoClient, p: Plantacion) -> Optional[Evaluacion]:
    """Para listados: si el clima falla, la plantación se muestra igual, sin estado."""
    try:
        return _evaluar(p, _pronostico(clima, p))
    except HTTPException:
        return None


def _serializar(p: Plantacion, ev: Optional[Evaluacion]) -> PlantacionOut:
    return PlantacionOut(
        id=p.id,
        planta=p.planta,
        planta_nombre=CATALOGO[p.planta].nombre,
        ubicacion=p.ubicacion,
        tipo_tierra=p.tipo_tierra,
        etapa=p.etapa,
        ultimo_riego=_utc(p.ultimo_riego),
        proximo_riego=_mediodia(ev.proximo_riego) if ev and ev.proximo_riego else None,
        estado=ev.estado if ev else None,
        creado_en=_utc(p.creado_en),
    )


# ---------- CRUD ----------
@router.get("", response_model=list[PlantacionOut])
def listar(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    clima: OpenMeteoClient = Depends(get_clima_client),
):
    plantaciones = db.scalars(
        select(Plantacion)
        .where(Plantacion.user_id == user.id)
        .order_by(Plantacion.creado_en.desc())
    ).all()
    return [_serializar(p, _evaluar_seguro(clima, p)) for p in plantaciones]


@router.post("", response_model=PlantacionOut, status_code=201)
def crear(
    payload: PlantacionIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    clima: OpenMeteoClient = Depends(get_clima_client),
):
    latitud, longitud = _geocodificar(clima, payload.ubicacion)
    p = Plantacion(
        user_id=user.id,
        planta=payload.planta,
        ubicacion=payload.ubicacion,
        latitud=latitud,
        longitud=longitud,
        tipo_tierra=payload.tipo_tierra,
        etapa=payload.etapa,
        ultimo_riego=payload.ultimo_riego,
    )
    db.add(p)
    db.commit()

    db.refresh(p)
    
    return _serializar(p, _evaluar_seguro(clima, p))


@router.get("/{plantacion_id}", response_model=PlantacionOut)
def obtener(
    plantacion_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    clima: OpenMeteoClient = Depends(get_clima_client),
):
    p = _obtener(db, user, plantacion_id)
    return _serializar(p, _evaluar_seguro(clima, p))


@router.put("/{plantacion_id}", response_model=PlantacionOut)
def actualizar(
    plantacion_id: str,
    payload: PlantacionIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    clima: OpenMeteoClient = Depends(get_clima_client),
):
    p = _obtener(db, user, plantacion_id)
    if payload.ubicacion != p.ubicacion:
        p.latitud, p.longitud = _geocodificar(clima, payload.ubicacion)
        p.ubicacion = payload.ubicacion
    p.planta = payload.planta
    p.tipo_tierra = payload.tipo_tierra
    p.etapa = payload.etapa
    if payload.ultimo_riego is not None:
        p.ultimo_riego = payload.ultimo_riego
    db.commit()
    return _serializar(p, _evaluar_seguro(clima, p))


@router.delete("/{plantacion_id}", status_code=204)
def eliminar(
    plantacion_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    p = _obtener(db, user, plantacion_id)
    db.delete(p)
    db.commit()
    return Response(status_code=204)


# ---------- Monitoreo ----------
@router.get("/{plantacion_id}/recomendacion", response_model=RecomendacionOut)
def ver_recomendacion(
    plantacion_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    clima: OpenMeteoClient = Depends(get_clima_client),
):
    p = _obtener(db, user, plantacion_id)
    ev = _evaluar(p, _pronostico(clima, p))
    return RecomendacionOut(estado=ev.estado, titulo=ev.titulo, motivo=ev.motivo)


@router.get("/{plantacion_id}/riego", response_model=RiegoOut)
def ver_plan_de_riego(
    plantacion_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    clima: OpenMeteoClient = Depends(get_clima_client),
):
    p = _obtener(db, user, plantacion_id)
    ev = _evaluar(p, _pronostico(clima, p))
    return RiegoOut(
        dias=[DiaRiegoOut(fecha=_mediodia(d.fecha), regar=d.regar, motivo=d.motivo) for d in ev.plan]
    )


@router.get("/{plantacion_id}/clima", response_model=ClimaOut)
def ver_clima(
    plantacion_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    clima: OpenMeteoClient = Depends(get_clima_client),
):
    p = _obtener(db, user, plantacion_id)
    pron = _pronostico(clima, p)
    futuros = [d for d in pron.dias if d.fecha >= pron.hoy][:DIAS_PLAN]
    return ClimaOut(
        dias=[
            DiaClimaOut(
                fecha=_mediodia(d.fecha),
                temp_min=round(d.temp_min),
                temp_max=round(d.temp_max),
                condicion=d.condicion,
                prob_lluvia=d.prob_lluvia,
                precipitacion=round(d.precipitacion, 1),
            )
            for d in futuros
        ]
    )


@router.get("/{plantacion_id}/humedad", response_model=HumedadOut)
def ver_humedad(
    plantacion_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    clima: OpenMeteoClient = Depends(get_clima_client),
):
    p = _obtener(db, user, plantacion_id)
    ev = _evaluar(p, _pronostico(clima, p))
    return HumedadOut(
        porcentaje=ev.humedad_pct,
        nivel=ev.nivel,
        dias_restantes=ev.dias_restantes,
        detalle=ev.detalle_humedad,
    )


@router.post("/{plantacion_id}/riego", response_model=PlantacionOut)
def registrar_riego(
    plantacion_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    clima: OpenMeteoClient = Depends(get_clima_client),
):
    """Registra que se regó ahora. Reinicia el balance de humedad del suelo."""
    p = _obtener(db, user, plantacion_id)
    p.ultimo_riego = datetime.now(timezone.utc)
    db.commit()
    return _serializar(p, _evaluar_seguro(clima, p))
