from datetime import date, datetime, timezone

from app.services.clima import (
    candidatos_busqueda,
    condicion_desde_codigo,
    elegir_resultado,
    parsear_pronostico,
)


def test_condicion_desde_codigo_wmo():
    assert condicion_desde_codigo(0) == "soleado"
    assert condicion_desde_codigo(2) == "parcialmente_nublado"
    assert condicion_desde_codigo(3) == "nublado"
    assert condicion_desde_codigo(45) == "nublado"
    assert condicion_desde_codigo(61) == "lluvia"
    assert condicion_desde_codigo(95) == "lluvia"


def test_candidatos_de_busqueda():
    assert candidatos_busqueda("Coquimbo, Chile") == [("Coquimbo", ["Chile"]), ("Chile", ["Coquimbo"])]
    assert candidatos_busqueda("Ovalle") == [("Ovalle", [])]
    assert candidatos_busqueda(" , ") == []


def test_elegir_resultado_prioriza_el_pais_indicado():
    resultados = [
        {"name": "Coquimbo", "country": "Argentina", "admin1": "Córdoba"},
        {"name": "Coquimbo", "country": "Chile", "admin1": "Coquimbo"},
    ]
    assert elegir_resultado(resultados, ["Chile"])["country"] == "Chile"
    assert elegir_resultado(resultados, ["chíle"])["country"] == "Chile"  # sin distinguir tildes
    assert elegir_resultado(resultados, [])["country"] == "Argentina"     # sin calificador: el primero
    assert elegir_resultado(resultados, ["Peru"])["country"] == "Argentina"  # sin coincidencia: el primero
    assert elegir_resultado([], ["Chile"]) is None


def _payload():
    return {
        "utc_offset_seconds": -10800,
        "daily": {
            "time": ["2026-09-26", "2026-09-27"],
            "weather_code": [0, 61],
            "temperature_2m_max": [21.4, 18.6],
            "temperature_2m_min": [9.2, 8.7],
            "precipitation_sum": [0.0, 4.26],
            "precipitation_probability_max": [None, 70],
            "et0_fao_evapotranspiration": [3.5, None],
        },
    }


def test_parsear_pronostico():
    ahora = datetime(2026, 9, 28, 2, 30, tzinfo=timezone.utc)  # en Chile aún es 27
    pron = parsear_pronostico(_payload(), ahora)
    assert pron.hoy == date(2026, 9, 27)
    assert pron.utc_offset_segundos == -10800
    assert [d.fecha for d in pron.dias] == [date(2026, 9, 26), date(2026, 9, 27)]
    assert pron.dias[0].prob_lluvia == 0            # None -> 0
    assert pron.dias[0].condicion == "soleado"
    assert pron.dias[1].condicion == "lluvia"
    assert pron.dias[1].precipitacion == 4.26
    assert pron.dias[1].et0 == 3.0                  # None -> valor por defecto


def test_parsear_pronostico_invalido():
    from app.services.clima import ClimaError

    try:
        parsear_pronostico({"sin": "daily"}, datetime.now(timezone.utc))
    except ClimaError:
        return
    raise AssertionError("Debió lanzar ClimaError")
