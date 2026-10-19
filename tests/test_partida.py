import pytest

import armamento
import flota
import partida
import tablero


def armar_configuracion():
    n = 8
    cubo1 = tablero.crear_cubo(n)
    flota1 = flota.crear_flota()
    cubo1, flota1 = flota.ubicar_nave(cubo1, flota1, "F", (1, 1, 1), (1, 1, 2))
    cubo2 = tablero.crear_cubo(n)
    flota2 = flota.crear_flota()
    cubo2, flota2 = flota.ubicar_nave(cubo2, flota2, "F", (8, 8, 7), (8, 8, 8))
    return {
        "n": n,
        "nombre_jugador_1": "Jugador 1", "cubo_jugador_1": cubo1, "flota_jugador_1": flota1,
        "nombre_jugador_2": "Jugador 2", "cubo_jugador_2": cubo2, "flota_jugador_2": flota2,
    }


def test_nueva_partida_1v1_arma_el_estado():
    estado = partida.nueva_partida_1v1(armar_configuracion())
    assert estado["turno_actual"] == "Jugador 1"
    assert estado["ganador"] is None
    assert estado["municiones"]["Jugador 1"]["T"] is None


def test_parsear_punto_y_tramo():
    punto = partida.parsear_punto("3,5,4", 8)
    assert punto == (3, 5, 4)
    desde, hasta = partida.parsear_tramo("3,4,2-3,4,7", 8)
    assert desde == (3, 4, 2)
    assert hasta == (3, 4, 7)


def test_parsear_punto_invalido():
    with pytest.raises(tablero.PuntoInvalidoError):
        partida.parsear_punto("abc", 8)


def test_ejecutar_turno_impacta_y_cambia_de_turno():
    estado = partida.nueva_partida_1v1(armar_configuracion())
    jugada = {"arma": "T", "punto": (8, 8, 7), "eje": None, "valor": None}
    partida.ejecutar_turno(estado, jugada)
    assert estado["turno_actual"] == "Jugador 2"
    assert estado["estadisticas"]["Jugador 1"]["aciertos"] == 1


def test_ejecutar_turno_hunde_y_declara_ganador():
    estado = partida.nueva_partida_1v1(armar_configuracion())
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (8, 8, 7), "eje": None, "valor": None})
    estado["turno_actual"] = "Jugador 1"
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (8, 8, 8), "eje": None, "valor": None})
    assert partida.hay_ganador(estado) == "Jugador 1"


def test_disparar_dos_veces_al_mismo_punto_lanza_excepcion():
    estado = partida.nueva_partida_1v1(armar_configuracion())
    punto = (4, 4, 4)
    partida.ejecutar_turno(estado, {"arma": "T", "punto": punto, "eje": None, "valor": None})
    estado["turno_actual"] = "Jugador 1"
    with pytest.raises(partida.ObjetivoYaDisparadoError):
        partida.ejecutar_turno(estado, {"arma": "T", "punto": punto, "eje": None, "valor": None})


def test_turno_maquina_dispara_y_avanza():
    estado = partida.nueva_partida_1v1(armar_configuracion())
    estado["es_vs_maquina"] = True
    partida.turno_maquina(estado)
    assert estado["estadisticas"]["Jugador 1"]["disparos"] == 1
