"""Pronóstico sintético y determinista para los tests (sin red)."""
from datetime import date, timedelta
from typing import Optional

from app.services.riego import DiaClima, Pronostico


def pronostico_sintetico(
    hoy: date,
    et0: float = 4.0,
    lluvia: Optional[dict[int, float]] = None,
    pasados: int = 7,
    futuros: int = 7,
    utc_offset_segundos: int = 0,
) -> Pronostico:
    """Días desde hoy-pasados hasta hoy+futuros-1. `lluvia` mapea offset de día -> mm."""
    lluvia = lluvia or {}
    dias = []
    for offset in range(-pasados, futuros):
        mm = lluvia.get(offset, 0.0)
        dias.append(
            DiaClima(
                fecha=hoy + timedelta(days=offset),
                temp_min=10.0,
                temp_max=22.0,
                precipitacion=mm,
                prob_lluvia=80 if mm >= 2 else 10,
                condicion="lluvia" if mm >= 2 else "soleado",
                et0=et0,
            )
        )
    return Pronostico(hoy=hoy, utc_offset_segundos=utc_offset_segundos, dias=dias)
