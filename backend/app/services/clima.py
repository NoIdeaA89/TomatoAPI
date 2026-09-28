"""Cliente de Open-Meteo (https://open-meteo.com): geocodificación y pronóstico diario.

Gratuito y sin API key para uso no comercial. Los datos son CC BY 4.0 (atribuir a Open-Meteo).
"""
from __future__ import annotations

import threading
import time
import unicodedata
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import httpx

from app.config import settings
from app.services.riego import DiaClima, Pronostico

VARIABLES_DIARIAS = [
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "et0_fao_evapotranspiration",
]
DIAS_PASADOS = 7
DIAS_FUTUROS = 7
ET0_POR_DEFECTO = 3.0  # mm/día, solo si la API no entrega el dato


class ClimaError(Exception):
    """El servicio de clima no respondió o devolvió datos inválidos."""


class UbicacionNoEncontrada(ClimaError):
    """La ubicación indicada no pudo geocodificarse."""


def _normalizar(texto: str) -> str:
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return sin_tildes.lower().strip()


def condicion_desde_codigo(codigo: int) -> str:
    """Traduce el weather_code WMO a las condiciones que entiende el frontend."""
    if codigo in (0, 1):
        return "soleado"
    if codigo == 2:
        return "parcialmente_nublado"
    if codigo in (3, 45, 48):
        return "nublado"
    return "lluvia"  # llovizna, lluvia, nieve, chubascos y tormenta


def candidatos_busqueda(ubicacion: str) -> list[tuple[str, list[str]]]:
    """'Coquimbo, Chile' -> busca 'Coquimbo' priorizando resultados de 'Chile'.

    La API de geocodificación busca por nombre de lugar, no por texto libre con coma.
    Si el primer nombre no existe, se intenta con los siguientes ('Fundo X, Ovalle' -> 'Ovalle').
    """
    partes = [p.strip() for p in ubicacion.split(",") if p.strip()]
    if not partes:
        return []
    candidatos = [(partes[0], partes[1:])]
    for parte in partes[1:]:
        candidatos.append((parte, [q for q in partes if q != parte]))
    return candidatos


def elegir_resultado(resultados: list[dict], calificadores: list[str]) -> Optional[dict]:
    if not resultados:
        return None
    quals = [_normalizar(q) for q in calificadores if q.strip()]
    if not quals:
        return resultados[0]

    def texto(r: dict) -> str:
        campos = ("country", "country_code", "admin1", "admin2", "admin3")
        return _normalizar(" ".join(str(r.get(c, "")) for c in campos))

    for r in resultados:
        if all(q in texto(r) for q in quals):
            return r
    for r in resultados:
        if any(q in texto(r) for q in quals):
            return r
    return resultados[0]


def parsear_pronostico(payload: dict, ahora_utc: datetime) -> Pronostico:
    try:
        daily = payload["daily"]
        fechas = daily["time"]
        offset = int(payload.get("utc_offset_seconds", 0))
    except (KeyError, TypeError, ValueError) as exc:
        raise ClimaError("Respuesta de clima inválida.") from exc

    def valor(clave: str, i: int, defecto: float = 0.0) -> float:
        serie = daily.get(clave) or []
        v = serie[i] if i < len(serie) else None
        return defecto if v is None else v

    dias: list[DiaClima] = []
    try:
        for i, f in enumerate(fechas):
            dias.append(
                DiaClima(
                    fecha=date.fromisoformat(f),
                    temp_min=float(valor("temperature_2m_min", i)),
                    temp_max=float(valor("temperature_2m_max", i)),
                    precipitacion=float(valor("precipitation_sum", i)),
                    prob_lluvia=int(valor("precipitation_probability_max", i)),
                    condicion=condicion_desde_codigo(int(valor("weather_code", i))),
                    et0=float(valor("et0_fao_evapotranspiration", i, ET0_POR_DEFECTO)),
                )
            )
    except (TypeError, ValueError) as exc:
        raise ClimaError("Datos de clima con formato inesperado.") from exc

    hoy = (ahora_utc + timedelta(seconds=offset)).date()
    return Pronostico(hoy=hoy, utc_offset_segundos=offset, dias=sorted(dias, key=lambda d: d.fecha))


class OpenMeteoClient:
    def __init__(self, ttl_segundos: int = 1800, timeout: float = 8.0) -> None:
        self._ttl = ttl_segundos
        self._timeout = timeout
        self._cache: dict[tuple[float, float], tuple[float, Pronostico]] = {}
        self._lock = threading.Lock()

    def _get(self, url: str, params: dict) -> dict:
        try:
            respuesta = httpx.get(url, params=params, timeout=self._timeout)
            respuesta.raise_for_status()
            return respuesta.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ClimaError(str(exc)) from exc

    def geocodificar(self, ubicacion: str) -> tuple[float, float]:
        for nombre, calificadores in candidatos_busqueda(ubicacion):
            data = self._get(
                settings.geocoding_url,
                {"name": nombre, "count": 10, "language": "es", "format": "json"},
            )
            resultado = elegir_resultado(data.get("results") or [], calificadores)
            if resultado:
                try:
                    return float(resultado["latitude"]), float(resultado["longitude"])
                except (KeyError, TypeError, ValueError) as exc:
                    raise ClimaError("Respuesta de geocodificación inválida.") from exc
        raise UbicacionNoEncontrada(ubicacion)

    def pronostico(self, latitud: float, longitud: float) -> Pronostico:
        clave = (round(latitud, 2), round(longitud, 2))
        with self._lock:
            guardado = self._cache.get(clave)
            if guardado and time.monotonic() - guardado[0] < self._ttl:
                return guardado[1]

        data = self._get(
            settings.forecast_url,
            {
                "latitude": latitud,
                "longitude": longitud,
                "daily": ",".join(VARIABLES_DIARIAS),
                "past_days": DIAS_PASADOS,
                "forecast_days": DIAS_FUTUROS,
                "timezone": "auto",
            },
        )
        pron = parsear_pronostico(data, datetime.now(timezone.utc))
        with self._lock:
            self._cache[clave] = (time.monotonic(), pron)
        return pron


_cliente: Optional[OpenMeteoClient] = None


def get_clima_client() -> OpenMeteoClient:
    """Dependencia de FastAPI (los tests la reemplazan por un cliente falso)."""
    global _cliente
    if _cliente is None:
        _cliente = OpenMeteoClient()
    return _cliente
