"""Datos agronómicos de las plantas soportadas.

Los coeficientes de cultivo (Kc) y las profundidades de raíz son valores aproximados
tomados de FAO-56 (Riego y drenaje N° 56). Están pensados para un proyecto académico:
sirven para estimar, no para reemplazar la asesoría de un agrónomo.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Planta:
    id: str
    nombre: str
    especie: str
    kc_ini: float        # coeficiente de cultivo, etapa inicial
    kc_mid: float        # etapa media (floración / fructificación)
    kc_end: float        # etapa final (maduración)
    raiz_m: float        # profundidad radicular máxima (m)
    agotamiento: float   # fracción del agua útil que se puede perder antes de regar (0-1)


_PLANTAS = [
    Planta("tomate", "Tomate", "Solanum lycopersicum", 0.60, 1.15, 0.80, 0.70, 0.40),
    Planta("lechuga", "Lechuga", "Lactuca sativa", 0.70, 1.00, 0.95, 0.40, 0.30),
    Planta("papa", "Papa", "Solanum tuberosum", 0.50, 1.15, 0.75, 0.50, 0.35),
    Planta("maiz", "Maíz", "Zea mays", 0.30, 1.20, 0.60, 1.00, 0.55),
    Planta("pimenton", "Pimentón", "Capsicum annuum", 0.60, 1.05, 0.90, 0.60, 0.30),
    Planta("zanahoria", "Zanahoria", "Daucus carota", 0.70, 1.05, 0.95, 0.50, 0.35),
]

CATALOGO: dict[str, Planta] = {p.id: p for p in _PLANTAS}

# Agua útil del suelo (mm de agua por metro de suelo). Valores medios aproximados.
AWC_MM_POR_M: dict[str, float] = {
    "arenoso": 90.0,
    "franco": 150.0,
    "limoso": 190.0,
    "arcilloso": 160.0,
}

# Qué fracción de la raíz máxima está desarrollada en cada etapa.
FACTOR_RAIZ_ETAPA: dict[str, float] = {
    "germinacion": 0.4,
    "inicial": 0.5,
    "vegetativa": 0.75,
    "floracion": 1.0,
    "fructificacion": 1.0,
    "maduracion": 1.0,
}


def kc_para(planta: Planta, etapa: str) -> float:
    if etapa in ("germinacion", "inicial"):
        return planta.kc_ini
    if etapa == "vegetativa":
        return (planta.kc_ini + planta.kc_mid) / 2
    if etapa in ("floracion", "fructificacion"):
        return planta.kc_mid
    if etapa == "maduracion":
        return planta.kc_end
    raise ValueError(f"Etapa desconocida: {etapa}")


def capacidad_mm(planta: Planta, tipo_tierra: str, etapa: str) -> float:
    """Agua útil (mm) que el suelo puede almacenar en la zona de raíces."""
    return AWC_MM_POR_M[tipo_tierra] * planta.raiz_m * FACTOR_RAIZ_ETAPA[etapa]
