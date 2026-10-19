import pytest

import registro


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


def test_guardar_partida_no_implementado_en_esta_entrega():
    with pytest.raises(NotImplementedError):
        registro.guardar_partida({}, "nombre")
