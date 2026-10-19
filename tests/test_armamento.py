import pytest

import armamento
import flota
import tablero


def test_celdas_torpedo():
    celdas = armamento.obtener_celdas_torpedo((4, 4, 4), 8, None)
    assert celdas == [(4, 4, 4)]


def test_celdas_racimo_incluye_vecinos():
    celdas = armamento.obtener_celdas_racimo((4, 4, 4), 8, None)
    assert len(celdas) == 7
    assert (4, 4, 4) in celdas
    assert (3, 4, 4) in celdas


def test_celdas_carga_profundidad_recorre_todo_el_eje_z():
    celdas = armamento.obtener_celdas_carga_profundidad((1, 5, 6), 8, None)
    assert len(celdas) == 8
    assert all(celda[1] == 5 and celda[2] == 6 for celda in celdas)


def test_celdas_laser_eje_x():
    celdas = armamento.obtener_celdas_laser((3, 1, 1), 8, "x")
    assert len(celdas) == 8
    assert all(celda[0] == 3 and celda[2] == 1 for celda in celdas)


def test_celdas_laser_eje_invalido():
    with pytest.raises(armamento.ArmaInvalidaError):
        armamento.obtener_celdas_laser((3, 1, 1), 8, "z")


def test_municion_torpedo_es_ilimitada():
    municion = armamento.crear_municion_inicial(armamento.CATALOGO_ARMAS)
    assert armamento.hay_municion(municion, "T")
    armamento.descontar_municion(municion, "T")
    assert municion["T"] is None


def test_municion_se_agota():
    municion = armamento.crear_municion_inicial(armamento.CATALOGO_ARMAS)
    for _ in range(municion["C"]):
        armamento.descontar_municion(municion, "C")
    with pytest.raises(armamento.MunicionAgotadaError):
        armamento.descontar_municion(municion, "C")


def test_aplicar_disparo_impacta_nave():
    cubo = tablero.crear_cubo(8)
    flota_rival = flota.crear_flota()
    cubo, flota_rival = flota.ubicar_nave(cubo, flota_rival, "F", (2, 2, 2), (2, 2, 3))
    resultado = armamento.aplicar_disparo(cubo, flota_rival, "T", (2, 2, 2), None, armamento.CATALOGO_ARMAS)
    assert len(resultado["celdas_impactadas"]) == 1
    assert tablero.leer_celda(cubo, (2, 2, 2)) == tablero.IMPACTO


def test_aplicar_disparo_en_agua():
    cubo = tablero.crear_cubo(8)
    flota_rival = flota.crear_flota()
    resultado = armamento.aplicar_disparo(cubo, flota_rival, "T", (1, 1, 1), None, armamento.CATALOGO_ARMAS)
    assert resultado["celdas_impactadas"] == []
    assert tablero.leer_celda(cubo, (1, 1, 1)) == tablero.AGUA_MARCADA


def test_laser_no_afecta_submarino():
    cubo = tablero.crear_cubo(8)
    flota_rival = flota.crear_flota()
    cubo, flota_rival = flota.ubicar_nave(cubo, flota_rival, "S", (1, 1, 1), (1, 1, 3))
    resultado = armamento.aplicar_disparo(cubo, flota_rival, "L", (1, 1, 1), "x", armamento.CATALOGO_ARMAS)
    assert resultado["celdas_impactadas"] == []


def test_sonar_no_tiene_funcion_de_celdas_de_dano():
    with pytest.raises(armamento.ArmaInvalidaError):
        armamento.aplicar_disparo(tablero.crear_cubo(8), flota.crear_flota(), "S", (1, 1, 1), None, armamento.CATALOGO_ARMAS)
