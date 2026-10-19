import pytest

import flota
import tablero


def test_ubicar_fragata_ok():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    cubo, flota_jugador = flota.ubicar_nave(cubo, flota_jugador, "F", (1, 1, 1), (1, 1, 2))
    assert flota.contar_naves_tipo(flota_jugador, "F") == 1
    assert tablero.leer_celda(cubo, (1, 1, 1)) == tablero.NAVE_OCULTA


def test_ubicar_nave_longitud_incorrecta():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    with pytest.raises(flota.UbicacionInvalidaError):
        flota.ubicar_nave(cubo, flota_jugador, "F", (1, 1, 1), (1, 1, 5))


def test_submarino_solo_en_mitad_inferior():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    with pytest.raises(flota.UbicacionInvalidaError):
        flota.ubicar_nave(cubo, flota_jugador, "S", (6, 1, 1), (8, 1, 1))


def test_crucero_no_puede_ir_en_extremos_de_z():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    with pytest.raises(flota.UbicacionInvalidaError):
        flota.ubicar_nave(cubo, flota_jugador, "C", (1, 1, 1), (1, 4, 1))


def test_portaaviones_solo_en_mitad_superior():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    with pytest.raises(flota.UbicacionInvalidaError):
        flota.ubicar_nave(cubo, flota_jugador, "P", (1, 1, 1), (5, 1, 1))


def test_estacion_no_toca_caras_exteriores():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    with pytest.raises(flota.UbicacionInvalidaError):
        flota.ubicar_nave(cubo, flota_jugador, "E", (1, 1, 1), (2, 2, 2))


def test_naves_necesitan_separacion():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    cubo, flota_jugador = flota.ubicar_nave(cubo, flota_jugador, "F", (4, 4, 4), (4, 4, 5))
    with pytest.raises(flota.UbicacionInvalidaError):
        flota.ubicar_nave(cubo, flota_jugador, "F", (5, 5, 6), (5, 5, 7))


def test_ubicacion_automatica_coloca_toda_la_flota():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.ubicacion_automatica(cubo, flota.CATALOGO_NAVES, semilla=1)
    cantidad_total = sum(datos["cantidad"] for datos in flota.CATALOGO_NAVES.values())
    assert len(flota_jugador) == cantidad_total


def test_registrar_impacto_y_estado_nave():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    cubo, flota_jugador = flota.ubicar_nave(cubo, flota_jugador, "F", (1, 1, 1), (1, 1, 2))
    id_nave = flota.buscar_nave_en_punto(flota_jugador, (1, 1, 1))
    assert flota.obtener_estado_nave(flota_jugador[id_nave]) == flota.ESTADO_SANA
    flota.registrar_impacto(flota_jugador, id_nave, (1, 1, 1))
    assert flota.obtener_estado_nave(flota_jugador[id_nave]) == flota.ESTADO_AVERIADA
    flota.registrar_impacto(flota_jugador, id_nave, (1, 1, 2))
    assert flota.obtener_estado_nave(flota_jugador[id_nave]) == flota.ESTADO_HUNDIDA
    assert flota_jugador[id_nave]["hundida"]


def test_portaaviones_necesita_dos_impactos_por_celda():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    cubo, flota_jugador = flota.ubicar_nave(cubo, flota_jugador, "P", (6, 1, 1), (6, 1, 5))
    id_nave = flota.buscar_nave_en_punto(flota_jugador, (6, 1, 1))
    flota.registrar_impacto(flota_jugador, id_nave, (6, 1, 1))
    assert flota.contar_celdas_impactadas(flota_jugador[id_nave]) == 0
    flota.registrar_impacto(flota_jugador, id_nave, (6, 1, 1))
    assert flota.contar_celdas_impactadas(flota_jugador[id_nave]) == 1


def test_pertenece_a_submarino():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    cubo, flota_jugador = flota.ubicar_nave(cubo, flota_jugador, "S", (1, 1, 1), (1, 1, 3))
    assert flota.pertenece_a_submarino(flota_jugador, (1, 1, 1))
    assert not flota.pertenece_a_submarino(flota_jugador, (8, 8, 8))


def test_flota_hundida_completa():
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    cubo, flota_jugador = flota.ubicar_nave(cubo, flota_jugador, "F", (1, 1, 1), (1, 1, 2))
    assert not flota.flota_hundida_completa(flota_jugador)
    id_nave = flota.buscar_nave_en_punto(flota_jugador, (1, 1, 1))
    flota.registrar_impacto(flota_jugador, id_nave, (1, 1, 1))
    flota.registrar_impacto(flota_jugador, id_nave, (1, 1, 2))
    assert flota.flota_hundida_completa(flota_jugador)
