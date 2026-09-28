"""Lógica de recomendación de riego (balance hídrico diario del suelo).

Modelo simple, en milímetros de agua:
  humedad_hoy = humedad_ayer + lluvia_efectiva - ET0 * Kc
acotada entre 0 y la capacidad del suelo. Se parte de suelo a capacidad de campo el día del
último riego registrado (o el día de creación de la plantación). Se debe regar cuando la
humedad cae bajo el umbral: capacidad * (1 - agotamiento_permitido).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from app.services.catalogo import Planta, capacidad_mm, kc_para

LLUVIA_SIGNIFICATIVA_MM = 2.0   # bajo esto la lluvia no cuenta (se evapora / no infiltra)
LLUVIA_MANANA_MM = 5.0          # lluvia de mañana que justifica esperar
EFICIENCIA_LLUVIA = 0.8         # fracción de la lluvia que realmente entra al suelo
LLUVIA_SATURACION_MM = 10.0     # lluvia efectiva reciente que puede dejar el suelo saturado
DIAS_PLAN = 6

TITULOS = {
    "regar": "Regar hoy",
    "no_regar": "No regar hoy",
    "lluvia": "No regar hoy",
    "humedad_suficiente": "No es necesario regar",
}


@dataclass(frozen=True)
class DiaClima:
    fecha: date
    temp_min: float
    temp_max: float
    precipitacion: float   # mm
    prob_lluvia: int       # %
    condicion: str
    et0: float             # evapotranspiración de referencia, mm/día


@dataclass(frozen=True)
class Pronostico:
    hoy: date
    utc_offset_segundos: int
    dias: list[DiaClima]   # días pasados recientes + hoy + próximos días


@dataclass(frozen=True)
class DiaPlan:
    fecha: date
    regar: bool
    motivo: str


@dataclass(frozen=True)
class Evaluacion:
    estado: str
    titulo: str
    motivo: str
    humedad_pct: int
    nivel: str
    dias_restantes: int
    detalle_humedad: str
    plan: list[DiaPlan]
    proximo_riego: Optional[date]


def fecha_local(dt: datetime, offset_segundos: int) -> date:
    """Fecha calendario local (según el offset UTC de la ubicación) de un datetime."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (dt.astimezone(timezone.utc) + timedelta(seconds=offset_segundos)).date()


def _lluvia_efectiva(mm: float) -> float:
    return mm * EFICIENCIA_LLUVIA if mm >= LLUVIA_SIGNIFICATIVA_MM else 0.0


def _avanzar(humedad: float, capacidad: float, dia: DiaClima, kc: float) -> float:
    nueva = humedad + _lluvia_efectiva(dia.precipitacion) - dia.et0 * kc
    return min(capacidad, max(0.0, nueva))


def _decidir(
    humedad: float,
    umbral: float,
    hoy: DiaClima,
    manana: Optional[DiaClima],
    saturado: bool = False,
) -> tuple[str, bool, str]:
    """Devuelve (estado, regar, motivo) para un día."""
    if saturado:
        return (
            "no_regar",
            False,
            "Suelo saturado por lluvias recientes; regar podría generar encharcamiento.",
        )
    if hoy.precipitacion >= LLUVIA_SIGNIFICATIVA_MM:
        return (
            "lluvia",
            False,
            f"Se pronostica lluvia ({hoy.precipitacion:.1f} mm); el aporte natural será suficiente.",
        )
    if humedad >= umbral:
        return "humedad_suficiente", False, "El suelo conserva humedad suficiente para la etapa actual."
    if manana is not None and manana.precipitacion >= LLUVIA_MANANA_MM:
        return "lluvia", False, "Lluvia significativa prevista para mañana; conviene esperar."
    return "regar", True, "El terreno está por debajo del nivel óptimo de humedad."


def evaluar(
    pron: Pronostico,
    planta: Planta,
    tipo_tierra: str,
    etapa: str,
    fecha_base: date,
) -> Evaluacion:
    """Evalúa el estado de riego de una plantación.

    fecha_base: día del último riego (o de creación de la plantación). Ese día se asume
    el suelo a capacidad de campo.
    """
    dias = sorted(pron.dias, key=lambda d: d.fecha)
    futuros = [d for d in dias if d.fecha >= pron.hoy]
    if not futuros or futuros[0].fecha != pron.hoy:
        raise ValueError("El pronóstico no incluye el día de hoy.")

    capacidad = capacidad_mm(planta, tipo_tierra, etapa)
    umbral = capacidad * (1.0 - planta.agotamiento)
    kc = kc_para(planta, etapa)

    por_fecha = {d.fecha: d for d in dias}
    base = min(max(fecha_base, dias[0].fecha), pron.hoy)

    # 1) Historia: desde el día base hasta hoy.
    humedad = capacidad
    lluvia_reciente = 0.0
    dia = base + timedelta(days=1)
    while dia <= pron.hoy:
        d = por_fecha.get(dia)
        if d is not None:
            humedad = _avanzar(humedad, capacidad, d, kc)
            if (pron.hoy - dia).days <= 2:
                lluvia_reciente += _lluvia_efectiva(d.precipitacion)
        dia += timedelta(days=1)
    humedad_hoy = humedad
    saturado = lluvia_reciente >= LLUVIA_SATURACION_MM and humedad_hoy >= 0.9 * capacidad

    # 2) Plan de los próximos días (se asume que cada riego recomendado se realiza).
    plan: list[DiaPlan] = []
    estado_hoy = ""
    motivo_hoy = ""
    h = humedad_hoy
    for i, d in enumerate(futuros[:DIAS_PLAN]):
        if i > 0:
            h = _avanzar(h, capacidad, d, kc)
        manana = futuros[i + 1] if i + 1 < len(futuros) else None
        estado, regar, motivo = _decidir(h, umbral, d, manana, saturado=(saturado and i == 0))
        if i == 0:
            estado_hoy, motivo_hoy = estado, motivo
        if regar:
            h = capacidad
        plan.append(DiaPlan(fecha=d.fecha, regar=regar, motivo=motivo))

    # 3) Cuántos días aguanta el suelo sin regar.
    sin_cruce = False
    if humedad_hoy < umbral:
        dias_restantes = 0
    else:
        dias_restantes = -1
        h2 = humedad_hoy
        for k, d in enumerate(futuros[1:], start=1):
            h2 = _avanzar(h2, capacidad, d, kc)
            if h2 < umbral:
                dias_restantes = k
                break
        if dias_restantes == -1:
            dias_restantes = len(futuros) - 1
            sin_cruce = True

    if humedad_hoy < umbral:
        detalle = "El suelo ya está por debajo del umbral óptimo de humedad."
        nivel = "baja"
    else:
        if sin_cruce:
            detalle = (
                f"Se estima que el suelo mantendrá humedad suficiente al menos durante "
                f"{dias_restantes} días."
            )
        else:
            unidad = "día" if dias_restantes == 1 else "días"
            detalle = (
                f"Se estima que el suelo mantendrá humedad suficiente durante "
                f"{dias_restantes} {unidad}."
            )
        nivel = "media" if humedad_hoy < umbral + (capacidad - umbral) / 2 else "alta"

    return Evaluacion(
        estado=estado_hoy,
        titulo=TITULOS[estado_hoy],
        motivo=motivo_hoy,
        humedad_pct=round(100 * humedad_hoy / capacidad),
        nivel=nivel,
        dias_restantes=dias_restantes,
        detalle_humedad=detalle,
        plan=plan,
        proximo_riego=next((p.fecha for p in plan if p.regar), None),
    )
