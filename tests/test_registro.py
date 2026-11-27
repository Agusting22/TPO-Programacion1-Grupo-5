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

def _configuracion_simple():
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
    return configuracion


def _armar_estado_simple():
    return partida.nueva_partida_1v1(_configuracion_simple())


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


def test_cargar_partida_conserva_celdas_detectadas(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    estado = _armar_estado_simple()
    partida.ejecutar_turno(estado, {"arma": "S", "punto": None, "eje": "z", "valor": 8})
    registro.guardar_partida(estado, "con_sonar")
    recuperado = registro.cargar_partida("con_sonar")
    assert tablero.leer_celda(recuperado["cubos"]["Jugador 2"], (8, 8, 7)) == tablero.DETECTADO


def test_cargar_partida_maquina_vs_maquina_se_retoma(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    estado = partida.nueva_partida_maquina_vs_maquina(_configuracion_simple(), ("facil", "dificil"))
    partida.turno_maquina(estado)
    registro.guardar_partida(estado, "maquinas")
    recuperado = registro.cargar_partida("maquinas")
    assert recuperado["es_maquina_vs_maquina"] is True
    assert recuperado["dificultades"] == estado["dificultades"]
    assert recuperado["turno_actual"] == estado["turno_actual"]
    partida.turno_maquina(recuperado)
    assert len(recuperado["historial"]) == 2


def _escribir(ruta, texto):
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(texto)


def _datos_validos():
    return registro.serializar_estado(_armar_estado_simple())


@pytest.mark.parametrize("clave, valor", [
    ("n", "8"),
    ("n", 9),
    ("flotas", []),
    ("flotas", {"Jugador 1": [], "Jugador 2": []}),
    ("cubos", {"Jugador 1": [[[0]]], "Jugador 2": [[[0]]]}),
    ("municiones", 5),
    ("municiones", {"Jugador 1": {"T": None, "R": None}, "Jugador 2": {}}),
    ("estadisticas", {}),
    ("historial", 3),
    ("historial", [{"numero": 1, "jugador": "Jugador 1", "detalle": {"punto": 5}}]),
    ("turno_actual", "Otro"),
])
def test_deserializar_estructura_mala_lanza_error_controlado(clave, valor):
    datos = _datos_validos()
    datos[clave] = valor
    with pytest.raises((ValueError, KeyError, TypeError, AttributeError, IndexError, tablero.ErrorCubo)):
        registro.deserializar_estado(datos)


def test_cargar_partida_recupera_historial_identico(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    estado = _armar_estado_simple()
    partida.ejecutar_turno(estado, {"arma": "R", "punto": (8, 8, 6), "eje": None, "valor": None})
    registro.guardar_partida(estado, "con_agua")
    recuperado = registro.cargar_partida("con_agua")
    assert recuperado["historial"] == estado["historial"]


def test_cargar_partida_acepta_flota_vacia():
    datos = _datos_validos()
    datos["flotas"]["Jugador 1"] = {}
    assert registro.deserializar_estado(datos)["flotas"]["Jugador 1"] == {}


def test_deserializar_lista_raiz_lanza_error_controlado():
    with pytest.raises(registro.DatosInvalidosError):
        registro.deserializar_estado([1, 2])


@pytest.mark.parametrize("contenido", [b"{}", b'"x"', b"[1]", b"no es json", b"\xff\xfe\x00",
                                       pytest.param(b"[" * 200000, id="anidado")])
def test_ranking_danado_no_se_sobrescribe(tmp_path, monkeypatch, contenido):
    monkeypatch.chdir(tmp_path)
    ruta = tmp_path / registro.ARCHIVO_RANKING
    ruta.write_bytes(contenido)
    with pytest.raises(registro.RankingInvalidoError):
        registro.listar_ranking()
    with pytest.raises(registro.RankingInvalidoError):
        registro.guardar_ranking("Jugador 1", "prueba", 10, False)
    assert ruta.read_bytes() == contenido


def test_exportar_reporte_escribe_resumen_e_historial(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    estado = _armar_estado_simple()
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (8, 8, 7), "eje": None, "valor": None})
    partida.ejecutar_turno(estado, {"arma": "S", "punto": None, "eje": "z", "valor": 8})
    ruta = registro.exportar_reporte(estado, "informe")
    with open(ruta, "r", encoding="utf-8") as archivo:
        texto = archivo.read()
    assert ruta.endswith("informe.txt")
    assert "--- Estadisticas ---" in texto
    assert "1. Jugador 1: Torpedo apuntado a 8,8,7. Impactos: F1 en 8,8,7." in texto
    assert "2. Jugador 2: Sonar (eje z) valor 8." in texto


def test_guardar_partida_devuelve_la_ruta_escrita(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ruta = registro.guardar_partida(_armar_estado_simple(), "con_ruta")
    assert ruta.endswith("con_ruta.json")
    assert (tmp_path / ruta).exists()


def test_texto_no_codificable_no_destruye_archivos_existentes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    estado = _armar_estado_simple()
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (8, 8, 7), "eje": None, "valor": None})
    guardada = tmp_path / registro.guardar_partida(estado, "previa")
    reporte = tmp_path / registro.exportar_reporte(estado, "previa")
    registro.guardar_ranking("Jugador 1", "previa", 1, False)
    ranking = tmp_path / registro.ARCHIVO_RANKING
    antes = [guardada.read_bytes(), reporte.read_bytes(), ranking.read_bytes()]
    estado["historial"][0]["jugador"] = "\ud800"
    with pytest.raises(ValueError):
        registro.guardar_partida(estado, "previa")
    with pytest.raises(ValueError):
        registro.exportar_reporte(estado, "previa")
    with pytest.raises(ValueError):
        registro.guardar_ranking("\ud800", "previa", 1, False)
    assert [guardada.read_bytes(), reporte.read_bytes(), ranking.read_bytes()] == antes


def test_cargar_nombre_de_jugador_no_codificable_lanza_error():
    datos = _datos_validos()
    datos["jugador_1"] = "\ud800"
    for clave in ("cubos", "flotas", "municiones", "estadisticas"):
        datos[clave]["\ud800"] = datos[clave]["Jugador 1"]
    datos["turno_actual"] = "\ud800"
    with pytest.raises(ValueError):
        registro.deserializar_estado(datos)
