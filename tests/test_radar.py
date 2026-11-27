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
    for celda in celdas:
        assert celda[0] == 3


def test_obtener_celdas_plano_eje_invalido():
    with pytest.raises(radar.EjeInvalidoError):
        radar.obtener_celdas_plano("w", 1, 8)


def test_aplicar_sonar_revela_sin_hacer_dano():
    cubo = tablero.crear_cubo(8)
    tablero.escribir_celda(cubo, (3, 2, 2), tablero.NAVE_OCULTA)
    reveladas = radar.aplicar_sonar(cubo, "z", 3)
    assert (3, 2, 2) in reveladas
    assert tablero.leer_celda(cubo, (3, 2, 2)) == tablero.DETECTADO


def test_buscar_naves_recursiva_encuentra_nave():
    cubo = tablero.crear_cubo(4)
    tablero.escribir_celda(cubo, (3, 2, 1), tablero.NAVE_OCULTA)
    encontrados, metricas = radar.buscar_naves_recursiva(cubo)
    assert encontrados == [(3, 2, 1)]
    assert metricas["comparaciones"] == 4 * 4 * 4


def test_buscar_naves_recursiva_da_lo_mismo_que_la_lineal():
    cubo = tablero.crear_cubo(4)
    tablero.escribir_celda(cubo, (1, 1, 1), tablero.NAVE_OCULTA)
    tablero.escribir_celda(cubo, (4, 4, 4), tablero.DETECTADO)
    lineal, _ = radar.buscar_naves_lineal(cubo)
    recursiva, _ = radar.buscar_naves_recursiva(cubo)
    assert recursiva == lineal


def test_buscar_naves_recursiva_profundidad_es_la_cantidad_de_capas():
    cubo = tablero.crear_cubo(4)
    _, metricas = radar.buscar_naves_recursiva(cubo)
    assert metricas["profundidad_max"] == 4
    assert "tiempo_ms" in metricas


def test_mapa_probabilidad_tiene_el_tamano_del_cubo():
    cubo = tablero.crear_cubo(4)
    mapa = radar.mapa_probabilidad(cubo, [2])
    assert len(mapa) == 4
    assert len(mapa[0]) == 4
    assert len(mapa[0][0]) == 4


def test_mapa_probabilidad_el_centro_tiene_mas_que_la_esquina():
    cubo = tablero.crear_cubo(4)
    mapa = radar.mapa_probabilidad(cubo, [2])
    esquina = tablero.leer_celda(mapa, (1, 1, 1))
    centro = tablero.leer_celda(mapa, (2, 2, 2))
    assert centro > esquina


def test_mapa_probabilidad_agua_marcada_vale_cero():
    cubo = tablero.crear_cubo(4)
    tablero.escribir_celda(cubo, (1, 1, 1), tablero.AGUA_MARCADA)
    mapa = radar.mapa_probabilidad(cubo, [2])
    assert tablero.leer_celda(mapa, (1, 1, 1)) == 0


def test_recorrido_octantes_recursivo_visita_todas_las_celdas():
    puntos = radar.recorrido_octantes(4)
    assert len(puntos) == 64
    assert len(set(puntos)) == 64
    puntos_8 = radar.recorrido_octantes(8)
    assert len(puntos_8) == 512
    assert len(set(puntos_8)) == 512


def test_recorrido_espiral_recursivo_visita_todas_las_celdas():
    cubo = tablero.crear_cubo(4)
    puntos = radar.recorrido_espiral(cubo)
    assert len(puntos) == 64
    assert len(set(puntos)) == 64
    assert puntos[0] == (1, 1, 1)


def test_recorrido_propagacion_recursivo_visita_todas_las_celdas():
    puntos = radar.recorrido_propagacion(4)
    assert len(puntos) == 64
    assert len(set(puntos)) == 64


def test_recorrido_propagacion_con_origen_personalizado():
    origen = (1, 1, 1)
    puntos = radar.recorrido_propagacion(4, origen)
    assert puntos[0] == origen
    assert len(puntos) == 64
    assert len(set(puntos)) == 64


def test_recorrido_propagacion_origen_invalido_lanza_excepcion():
    with pytest.raises(tablero.PuntoInvalidoError):
        radar.recorrido_propagacion(4, (9, 9, 9))


def test_despacho_recorridos_por_diccionario():
    for nombre in [radar.NOMBRE_RECORRIDO_CAPAS,
                   radar.NOMBRE_RECORRIDO_OCTANTES,
                   radar.NOMBRE_RECORRIDO_ESPIRAL,
                   radar.NOMBRE_RECORRIDO_PROPAGACION,
                   radar.NOMBRE_RECORRIDO_CAPAS_X,
                   radar.NOMBRE_RECORRIDO_CAPAS_Y]:
        puntos = radar.obtener_recorrido(nombre, 4)
        assert len(puntos) == 64
        assert len(set(puntos)) == 64


def test_obtener_recorrido_invalido_lanza_excepcion():
    with pytest.raises(radar.RecorridoInvalidoError):
        radar.obtener_recorrido("recorrido_inexistente", 4)


def test_listar_nombres_recorridos():
    nombres = radar.listar_nombres_recorridos()
    assert radar.NOMBRE_RECORRIDO_CAPAS in nombres
    assert radar.NOMBRE_RECORRIDO_OCTANTES in nombres
    assert radar.NOMBRE_RECORRIDO_ESPIRAL in nombres
    assert radar.NOMBRE_RECORRIDO_PROPAGACION in nombres
