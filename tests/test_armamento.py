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


def test_aplicar_disparo_primer_impacto_portaaviones_no_es_agua():
    cubo = tablero.crear_cubo(8)
    flota_rival = flota.crear_flota()
    cubo, flota_rival = flota.ubicar_nave(cubo, flota_rival, "P", (6, 2, 2), (6, 2, 6))
    resultado1 = armamento.aplicar_disparo(cubo, flota_rival, "T", (6, 2, 2), None, armamento.CATALOGO_ARMAS)
    assert len(resultado1["celdas_impactadas"]) == 1
    assert resultado1["celdas_impactadas"][0][0] == (6, 2, 2)
    assert resultado1["celdas_agua"] == []
    assert tablero.leer_celda(cubo, (6, 2, 2)) != tablero.IMPACTO

    # Segundo disparo sobre la misma celda la marca como IMPACTO
    resultado2 = armamento.aplicar_disparo(cubo, flota_rival, "T", (6, 2, 2), None, armamento.CATALOGO_ARMAS)
    assert len(resultado2["celdas_impactadas"]) == 1
    assert tablero.leer_celda(cubo, (6, 2, 2)) == tablero.IMPACTO


def test_armas_area_no_vuelven_a_contar_impactos_en_celdas_marcadas():
    cubo = tablero.crear_cubo(8)
    flota_rival = flota.crear_flota()
    cubo, flota_rival = flota.ubicar_nave(cubo, flota_rival, "F", (4, 4, 4), (4, 4, 5))
    # Primer impacto en (4, 4, 4) con torpedo
    resultado1 = armamento.aplicar_disparo(cubo, flota_rival, "T", (4, 4, 4), None, armamento.CATALOGO_ARMAS)
    assert len(resultado1["celdas_impactadas"]) == 1
    assert tablero.leer_celda(cubo, (4, 4, 4)) == tablero.IMPACTO

    # Disparo de racimo en (4, 4, 5) que tiene de vecina a (4, 4, 4) ya marcada
    resultado2 = armamento.aplicar_disparo(cubo, flota_rival, "R", (4, 4, 5), None, armamento.CATALOGO_ARMAS)
    impactadas = [celda for celda, _, _ in resultado2["celdas_impactadas"]]
    assert (4, 4, 5) in impactadas
    assert (4, 4, 4) not in impactadas


def test_municion_inicial_onda_y_torpedo_guiado():
    municion = armamento.crear_municion_inicial(armamento.CATALOGO_ARMAS)
    assert municion[armamento.LETRA_ONDA_EXPANSIVA] == 1
    assert municion[armamento.LETRA_TORPEDO_GUIADO] == 1


def test_onda_expansiva_recursiva_propaga_radio():
    celdas = armamento.obtener_celdas_onda_expansiva((4, 4, 4), 8, None, radio=1)
    # Radio 1: centro mas 6 vecinas ortogonales = 7 celdas
    assert len(celdas) == 7
    assert (4, 4, 4) in celdas
    assert (3, 4, 4) in celdas

    celdas_r2 = armamento.obtener_celdas_onda_expansiva((4, 4, 4), 8, None, radio=2)
    # Radio 2 alcanza mas celdas de forma decreciente
    assert len(celdas_r2) > len(celdas)
    assert (2, 4, 4) in celdas_r2


def test_onda_expansiva_en_esquina_respeta_limites():
    celdas = armamento.obtener_celdas_onda_expansiva((1, 1, 1), 8, None, radio=2)
    assert all(tablero.es_punto_valido(c, 8) for c in celdas)


def test_torpedo_guiado_sin_impactos_previos_usa_punto():
    flota_rival = flota.crear_flota()
    celdas = armamento.obtener_celdas_torpedo_guiado((2, 3, 4), 8, None, flota_rival, None)
    assert celdas == [(2, 3, 4)]


def test_torpedo_guiado_busca_recursivamente_celda_contigua():
    cubo = tablero.crear_cubo(8)
    flota_rival = flota.crear_flota()
    cubo, flota_rival = flota.ubicar_nave(cubo, flota_rival, "D", (3, 5, 4), (3, 5, 6))
    # Primer impacto en (3, 5, 4)
    flota.registrar_impacto(flota_rival, "D1", (3, 5, 4))
    assert not flota_rival["D1"]["hundida"]

    # Torpedo guiado apuntado a otro lado (por ejemplo 1,1,1) debe redirigirse a (3, 5, 5)
    celdas = armamento.obtener_celdas_torpedo_guiado((1, 1, 1), 8, None, flota_rival, cubo)
    assert celdas == [(3, 5, 5)]


def test_torpedo_guiado_ignora_naves_ya_hundidas():
    cubo = tablero.crear_cubo(8)
    flota_rival = flota.crear_flota()
    cubo, flota_rival = flota.ubicar_nave(cubo, flota_rival, "F", (1, 1, 1), (1, 1, 2))
    flota.registrar_impacto(flota_rival, "F1", (1, 1, 1))
    flota.registrar_impacto(flota_rival, "F1", (1, 1, 2))
    assert flota_rival["F1"]["hundida"]

    # Al estar ya hundida, torpedo guiado no busca ahi, usa el punto apuntado
    celdas = armamento.obtener_celdas_torpedo_guiado((5, 5, 5), 8, None, flota_rival, cubo)
    assert celdas == [(5, 5, 5)]


def test_aplicar_disparo_con_onda_expansiva_y_torpedo_guiado():
    cubo = tablero.crear_cubo(8)
    flota_rival = flota.crear_flota()
    cubo, flota_rival = flota.ubicar_nave(cubo, flota_rival, "F", (3, 3, 3), (3, 3, 4))

    # 1. Disparo con onda expansiva en (3, 3, 2): su radio 2 alcanza (3, 3, 3) y (3, 3, 4)
    res_onda = armamento.aplicar_disparo(cubo, flota_rival, "O", (3, 3, 2), None, armamento.CATALOGO_ARMAS)
    impactadas = [celda for celda, _, _ in res_onda["celdas_impactadas"]]
    assert (3, 3, 3) in impactadas

    # 2. Nueva nave averiada
    cubo2 = tablero.crear_cubo(8)
    flota_rival2 = flota.crear_flota()
    cubo2, flota_rival2 = flota.ubicar_nave(cubo2, flota_rival2, "D", (4, 4, 1), (4, 4, 3))
    # Impacto inicial
    armamento.aplicar_disparo(cubo2, flota_rival2, "T", (4, 4, 1), None, armamento.CATALOGO_ARMAS)
    # Disparo de torpedo guiado apuntando a (8, 8, 8)
    res_guiado = armamento.aplicar_disparo(cubo2, flota_rival2, "G", (8, 8, 8), None, armamento.CATALOGO_ARMAS)
    assert len(res_guiado["celdas_impactadas"]) == 1
    assert res_guiado["celdas_impactadas"][0][0] == (4, 4, 2)
