from datetime import date, datetime, timedelta, timezone

from fakes import pronostico_sintetico

from app.services.catalogo import CATALOGO, capacidad_mm, kc_para
from app.services.riego import Pronostico, evaluar, fecha_local

HOY = date(2026, 9, 28)
TOMATE = CATALOGO["tomate"]


def _tomate(pron, dias_desde_riego, etapa="floracion", suelo="franco"):
    return evaluar(pron, TOMATE, suelo, etapa, HOY - timedelta(days=dias_desde_riego))


def test_plantacion_recien_creada_tiene_humedad_suficiente():
    ev = _tomate(pronostico_sintetico(HOY, et0=4.0), 0)
    assert ev.estado == "humedad_suficiente"
    assert ev.titulo == "No es necesario regar"
    assert ev.humedad_pct == 100
    assert ev.nivel == "alta"
    assert len(ev.plan) == 6
    assert not any(d.regar for d in ev.plan)
    assert ev.proximo_riego is None


def test_sin_lluvia_llega_el_momento_de_regar():
    # capacidad 105 mm, umbral 63 mm, ETc = 5 * 1.15 = 5.75 mm/día
    ev = _tomate(pronostico_sintetico(HOY, et0=5.0), 7)
    assert ev.estado == "humedad_suficiente"      # hoy: 64.75 mm, aún sobre el umbral
    assert ev.dias_restantes == 1
    assert ev.proximo_riego == HOY + timedelta(days=1)
    assert [d.regar for d in ev.plan] == [False, True, False, False, False, False]


def test_bajo_el_umbral_recomienda_regar_hoy():
    ev = _tomate(pronostico_sintetico(HOY, et0=6.0), 7)
    assert ev.estado == "regar"
    assert ev.titulo == "Regar hoy"
    assert ev.humedad_pct == 54
    assert ev.nivel == "baja"
    assert ev.dias_restantes == 0
    assert ev.proximo_riego == HOY


def test_lluvia_hoy_no_se_riega():
    ev = _tomate(pronostico_sintetico(HOY, et0=4.0, lluvia={0: 8.0}), 7)
    assert ev.estado == "lluvia"
    assert ev.titulo == "No regar hoy"
    assert "8.0 mm" in ev.motivo


def test_lluvia_significativa_manana_hace_esperar():
    ev = _tomate(pronostico_sintetico(HOY, et0=6.0, lluvia={1: 10.0}), 7)
    assert ev.estado == "lluvia"
    assert "mañana" in ev.motivo
    assert ev.plan[0].regar is False


def test_lluvia_debil_no_cuenta():
    con = _tomate(pronostico_sintetico(HOY, et0=6.0, lluvia={-2: 1.5}), 7)
    sin = _tomate(pronostico_sintetico(HOY, et0=6.0), 7)
    assert con.humedad_pct == sin.humedad_pct


def test_suelo_saturado_por_lluvias_recientes():
    ev = _tomate(pronostico_sintetico(HOY, et0=4.0, lluvia={-1: 30.0}), 3)
    assert ev.estado == "no_regar"
    assert "saturado" in ev.motivo


def test_riego_registrado_reinicia_el_balance():
    pron = pronostico_sintetico(HOY, et0=6.0)
    antes = _tomate(pron, 7)
    despues = _tomate(pron, 0)
    assert antes.estado == "regar"
    assert despues.estado == "humedad_suficiente"


def test_kc_por_etapa():
    assert kc_para(TOMATE, "germinacion") == TOMATE.kc_ini
    assert kc_para(TOMATE, "inicial") == TOMATE.kc_ini
    assert kc_para(TOMATE, "vegetativa") == (TOMATE.kc_ini + TOMATE.kc_mid) / 2
    assert kc_para(TOMATE, "floracion") == TOMATE.kc_mid
    assert kc_para(TOMATE, "fructificacion") == TOMATE.kc_mid
    assert kc_para(TOMATE, "maduracion") == TOMATE.kc_end


def test_capacidad_depende_de_etapa_y_suelo():
    assert capacidad_mm(TOMATE, "franco", "germinacion") < capacidad_mm(TOMATE, "franco", "floracion")
    assert capacidad_mm(TOMATE, "arenoso", "floracion") < capacidad_mm(TOMATE, "arcilloso", "floracion")


def test_suelo_arenoso_pide_riego_antes_que_arcilloso():
    pron = pronostico_sintetico(HOY, et0=4.0)
    arenoso = _tomate(pron, 7, suelo="arenoso")
    arcilloso = _tomate(pron, 7, suelo="arcilloso")
    assert arenoso.humedad_pct < arcilloso.humedad_pct


def test_fecha_local_respeta_zona_horaria():
    dt = datetime(2026, 9, 28, 2, 0, tzinfo=timezone.utc)
    assert fecha_local(dt, -3 * 3600) == date(2026, 9, 27)
    assert fecha_local(dt, 0) == date(2026, 9, 28)
    assert fecha_local(dt.replace(tzinfo=None), 0) == date(2026, 9, 28)  # naive = UTC


def test_pronostico_sin_hoy_falla():
    viejo = pronostico_sintetico(HOY - timedelta(days=30))  # solo contiene fechas pasadas
    pron = Pronostico(hoy=HOY, utc_offset_segundos=0, dias=viejo.dias)
    try:
        _tomate(pron, 0)
    except ValueError:
        return
    raise AssertionError("Debió lanzar ValueError")
