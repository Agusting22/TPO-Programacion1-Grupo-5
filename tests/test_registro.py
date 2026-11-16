import os

import pytest

import flota
import partida
import registro
import tablero


def test_crear_historial_vacio():
    assert registro.crear_historial() == []


def test_registrar_evento():
    historial = registro.crear_historial()
    registro.registrar_evento(historial, "Jugador 1", {"arma": "T"})
    assert len(historial) == 1
    assert historial[0]["jugador"] == "Jugador 1"
    assert historial[0]["numero"] == 1


def test_obtener_eventos_devuelve_copia():
    historial = registro.crear_historial()
    registro.registrar_evento(historial, "Jugador 1", {"arma": "T"})
    copia = registro.obtener_eventos(historial)
    copia.append({"numero": 99})
    assert len(historial) == 1


def test_crear_estadisticas():
    estadisticas = registro.crear_estadisticas(["Jugador 1", "Jugador 2"])
    assert estadisticas["Jugador 1"]["disparos"] == 0
    assert estadisticas["Jugador 2"]["naves_hundidas"] == 0


def test_registrar_disparo_acierto_y_fallo():
    estadisticas = registro.crear_estadisticas(["Jugador 1"])
    registro.registrar_disparo(estadisticas, "Jugador 1", True)
    registro.registrar_disparo(estadisticas, "Jugador 1", False)
    assert estadisticas["Jugador 1"]["disparos"] == 2
    assert estadisticas["Jugador 1"]["aciertos"] == 1
    assert estadisticas["Jugador 1"]["fallos"] == 1


def test_formatear_resumen_incluye_a_cada_jugador():
    estadisticas = registro.crear_estadisticas(["Jugador 1", "Jugador 2"])
    texto = registro.formatear_resumen(estadisticas)
    assert "Jugador 1" in texto
    assert "Jugador 2" in texto


# ---------------------------------------------------------------------------
# Tests Entrega 3: persistencia
# ---------------------------------------------------------------------------

def _armar_estado_simple():
    n = 8
    cubo1 = tablero.crear_cubo(n)
    flota1 = flota.crear_flota()
    cubo1, flota1 = flota.ubicar_nave(cubo1, flota1, "F", (1, 1, 1), (1, 1, 2))
    cubo2 = tablero.crear_cubo(n)
    flota2 = flota.crear_flota()
    cubo2, flota2 = flota.ubicar_nave(cubo2, flota2, "F", (8, 8, 7), (8, 8, 8))
    configuracion = {
        "n": n,
        "nombre_jugador_1": "Jugador 1", "cubo_jugador_1": cubo1, "flota_jugador_1": flota1,
        "nombre_jugador_2": "Jugador 2", "cubo_jugador_2": cubo2, "flota_jugador_2": flota2,
    }
    return partida.nueva_partida_1v1(configuracion)


def test_guardar_y_cargar_partida_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    estado = _armar_estado_simple()
    registro.guardar_partida(estado, "test_partida")
    recuperado = registro.cargar_partida("test_partida")
    assert recuperado["jugador_1"] == estado["jugador_1"]
    assert recuperado["jugador_2"] == estado["jugador_2"]
    assert recuperado["n"] == estado["n"]
    assert recuperado["turno_actual"] == estado["turno_actual"]
    assert recuperado["ganador"] is None
    assert recuperado["es_vs_maquina"] == estado["es_vs_maquina"]


def test_cargar_partida_restaura_flotas(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    estado = _armar_estado_simple()
    registro.guardar_partida(estado, "test_flota")
    recuperado = registro.cargar_partida("test_flota")
    naves_orig = set(estado["flotas"]["Jugador 1"].keys())
    naves_rec = set(recuperado["flotas"]["Jugador 1"].keys())
    assert naves_orig == naves_rec


def test_listar_partidas_vacio(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert registro.listar_partidas() == []


def test_listar_partidas_muestra_guardadas(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    estado = _armar_estado_simple()
    registro.guardar_partida(estado, "partida_a")
    registro.guardar_partida(estado, "partida_b")
    nombres = registro.listar_partidas()
    assert "partida_a" in nombres
    assert "partida_b" in nombres


def test_cargar_partida_inexistente_lanza_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        registro.cargar_partida("no_existe")


def test_guardar_y_cargar_con_disparo_en_historial(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    estado = _armar_estado_simple()
    jugada = {"arma": "T", "punto": (3, 4, 5), "eje": None, "valor": None}
    partida.ejecutar_turno(estado, jugada)
    registro.guardar_partida(estado, "con_historial")
    recuperado = registro.cargar_partida("con_historial")
    assert len(recuperado["historial"]) == 1
    detalle = recuperado["historial"][0]["detalle"]
    assert detalle["punto"] == (3, 4, 5)


def test_guardar_ranking_y_listar(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registro.guardar_ranking("Jugador 1", "prueba", 10, False)
    ranking = registro.listar_ranking()
    assert len(ranking) == 1
    assert ranking[0]["ganador"] == "Jugador 1"
    assert ranking[0]["turnos"] == 10


def test_listar_ranking_vacio(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert registro.listar_ranking() == []


def test_formatear_ranking_vacio():
    texto = registro.formatear_ranking([])
    assert "No hay" in texto


def test_formatear_ranking_con_entradas():
    entradas = [{"ganador": "J1", "turnos": 5, "es_vs_maquina": False, "timestamp": "2026-01-01T00:00:00"}]
    texto = registro.formatear_ranking(entradas)
    assert "J1" in texto
    assert "5 turnos" in texto
