import pytest

import flota
import radar
import tablero


def test_buscar_naves_lineal_encuentra_nave():
    cubo = tablero.crear_cubo(4)
    tablero.escribir_celda(cubo, (1, 1, 1), tablero.NAVE_OCULTA)
    encontrados, metricas = radar.buscar_naves_lineal(cubo)
    assert (1, 1, 1) in encontrados
    assert metricas["comparaciones"] == 4 * 4 * 4
    assert metricas["profundidad_max"] == 0
    assert "tiempo_ms" in metricas


def test_buscar_naves_optimizada_usa_indice_de_la_flota():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    cubo, flota_jugador = flota.ubicar_nave(cubo, flota_jugador, "F", (1, 1, 1), (1, 1, 2))
    encontrados, metricas = radar.buscar_naves_optimizada(cubo, flota_jugador)
    assert set(encontrados) == {(1, 1, 1), (1, 1, 2)}
    assert metricas["comparaciones"] == 2


def test_buscar_naves_optimizada_hace_menos_comparaciones_que_la_lineal():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    cubo, flota_jugador = flota.ubicar_nave(cubo, flota_jugador, "F", (1, 1, 1), (1, 1, 2))
    _, metricas_lineal = radar.buscar_naves_lineal(cubo)
    _, metricas_optimizada = radar.buscar_naves_optimizada(cubo, flota_jugador)
    assert metricas_optimizada["comparaciones"] < metricas_lineal["comparaciones"]


def test_obtener_celdas_plano_fijando_z():
    celdas = radar.obtener_celdas_plano("z", 3, 8)
    assert len(celdas) == 64
    assert all(celda[0] == 3 for celda in celdas)


def test_obtener_celdas_plano_eje_invalido():
    with pytest.raises(radar.EjeInvalidoError):
        radar.obtener_celdas_plano("w", 1, 8)


def test_aplicar_sonar_revela_sin_hacer_dano():
    cubo = tablero.crear_cubo(8)
    tablero.escribir_celda(cubo, (3, 2, 2), tablero.NAVE_OCULTA)
    reveladas = radar.aplicar_sonar(cubo, "z", 3)
    assert (3, 2, 2) in reveladas
    assert tablero.leer_celda(cubo, (3, 2, 2)) == tablero.DETECTADO
