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


def test_realizar_disparo_con_punto_invalido_no_corta_programa(monkeypatch, capsys):
    estado = partida.nueva_partida_1v1(armar_configuracion())
    # Simula ingresar arma "T" y luego un objetivo invalido "99,99,99"
    respuestas = iter(["T", "99,99,99"])
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))
    # No debe levantar excepcion
    partida.realizar_disparo(estado, "Jugador 1")
    salida = capsys.readouterr().out
    assert partida.MENSAJE_INVALIDO in salida
    # El turno no debe avanzar
    assert estado["turno_actual"] == "Jugador 1"


def test_formatear_mensaje_primer_impacto_portaaviones_no_es_agua():
    flota_rival = flota.crear_flota()
    cubo = tablero.crear_cubo(8)
    cubo, flota_rival = flota.ubicar_nave(cubo, flota_rival, "P", (6, 1, 1), (6, 1, 5))
    resultado = armamento.aplicar_disparo(cubo, flota_rival, "T", (6, 1, 1), None, armamento.CATALOGO_ARMAS)
    mensaje = partida.formatear_mensaje_resultado(flota_rival, resultado)
    assert "Agua." not in mensaje
    assert "Impacto" in mensaje
    assert "Portaaviones" in mensaje


def test_accion_radar_muestra_metricas(capsys):
    estado = partida.nueva_partida_1v1(armar_configuracion())
    resultado = partida.accion_radar(estado, "Jugador 1")
    assert resultado is True
    salida = capsys.readouterr().out
    assert "Reporte de Radar" in salida
    assert "Busqueda lineal" in salida
    assert "Busqueda optimizada" in salida
    assert "Comparaciones" in salida


# ---------------------------------------------------------------------------
# Tests Entrega 3
# ---------------------------------------------------------------------------

def test_menu_principal_acepta_opciones_1_a_5():
    for opcion in ["1", "2", "3", "4", "5"]:
        assert partida.validar_opcion(opcion, partida.PATRON_OPCION_MENU)


def test_menu_principal_no_acepta_opcion_6():
    assert not partida.validar_opcion("6", partida.PATRON_OPCION_MENU)


def test_opcion_salir_es_5():
    assert partida.OPCION_SALIR == "5"


def test_nueva_partida_maquina_vs_maquina_tiene_bandera():
    estado = partida.nueva_partida_maquina_vs_maquina(armar_configuracion())
    assert estado["es_maquina_vs_maquina"] is True
    assert estado["es_vs_maquina"] is True


def test_menu_turno_acepta_guardar_opcion_3():
    assert partida.validar_opcion("3", partida.PATRON_OPCION_TURNO)


def test_menu_turno_opcion_5_es_salir():
    assert partida.OPCION_TURNO_SALIR == "5"
    assert partida.OPCION_TURNO_GUARDAR == "3"
    assert partida.OPCION_TURNO_RADAR == "4"
    assert "3 - Guardar y salir" in partida.TEXTO_MENU_TURNO
    assert partida.ACCIONES_TURNO["3"] == partida.accion_guardar_partida
    assert partida.ACCIONES_TURNO["4"] == partida.accion_radar


def test_accion_guardar_partida_guarda_archivo(tmp_path, monkeypatch, capsys):
    import registro
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.input", lambda _: "mi_partida")
    estado = partida.nueva_partida_1v1(armar_configuracion())
    resultado = partida.accion_guardar_partida(estado, "Jugador 1")
    assert resultado is False
    recuperado = registro.cargar_partida("mi_partida")
    assert recuperado["jugador_1"] == "Jugador 1"


def test_accion_salir_partida_devuelve_false():
    estado = partida.nueva_partida_1v1(armar_configuracion())
    assert partida.accion_salir_partida(estado, "Jugador 1") is False


def test_turno_maquina_en_maquina_vs_maquina_avanza_turno():
    estado = partida.nueva_partida_maquina_vs_maquina(armar_configuracion())
    turno_antes = estado["turno_actual"]
    partida.turno_maquina(estado)
    # El turno debe haber avanzado (si no hay ganador)
    if partida.hay_ganador(estado) is None:
        assert estado["turno_actual"] != turno_antes


def test_nueva_partida_vs_maquina_guarda_dificultad():
    estado = partida.nueva_partida_vs_maquina(armar_configuracion(), "dificil")
    assert estado["dificultad"] == "dificil"
    assert estado["es_vs_maquina"] is True


def test_nueva_partida_maquina_vs_maquina_acepta_tupla_dificultades():
    config = armar_configuracion()
    config["nombre_jugador_1"] = "M1"
    config["nombre_jugador_2"] = "M2"
    estado = partida.nueva_partida_maquina_vs_maquina(config, ("facil", "dificil"))
    assert estado["dificultades"]["M1"] == "facil"
    assert estado["dificultades"]["M2"] == "dificil"


def test_turno_maquina_dificil_caza_nave_averiada():
    estado = partida.nueva_partida_vs_maquina(armar_configuracion(), "dificil")
    # Forzar el turno para Jugador 2 (la maquina) atacando a Jugador 1
    estado["turno_actual"] = "Jugador 2"
    # Agotar torpedo guiado para que use torpedo normal en modo caza
    estado["municiones"]["Jugador 2"]["G"] = 0
    # Jugador 1 tiene fragata en (1,1,1) y (1,1,2). Marcamos (1,1,1) como IMPACTO (averiada)
    cubo_j1 = estado["cubos"]["Jugador 1"]
    tablero.escribir_celda(cubo_j1, (1, 1, 1), tablero.IMPACTO)
    nave = list(estado["flotas"]["Jugador 1"].values())[0]
    nave["impactos"][(1, 1, 1)] = 1
    # La maquina dificil debe disparar a una celda vecina ortogonal a (1,1,1), en particular (1,1,2)
    partida.turno_maquina(estado)
    jugada = estado["ultima_jugada"]
    vecinos_111 = set(tablero.vecinos_ortogonales((1, 1, 1), estado["n"]))
    assert jugada["punto"] in vecinos_111


def test_turno_maquina_dificil_usa_torpedo_guiado_si_hay_averiada():
    estado = partida.nueva_partida_vs_maquina(armar_configuracion(), "dificil")
    estado["turno_actual"] = "Jugador 2"
    cubo_j1 = estado["cubos"]["Jugador 1"]
    tablero.escribir_celda(cubo_j1, (1, 1, 1), tablero.IMPACTO)
    nave = list(estado["flotas"]["Jugador 1"].values())[0]
    nave["impactos"][(1, 1, 1)] = 1
    # Con torpedo guiado disponible (G=1), debe disparar G
    partida.turno_maquina(estado)
    jugada = estado["ultima_jugada"]
    assert jugada["arma"] == "G"


def test_pedir_dificultad_maquina_opcion_1_y_2(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")
    assert partida.pedir_dificultad_maquina() == "facil"

    monkeypatch.setattr("builtins.input", lambda _: "2")
    assert partida.pedir_dificultad_maquina() == "dificil"


def test_vistas_recorridos_alternativos_cubo():
    cubo = tablero.crear_cubo(4)
    tablero.escribir_celda(cubo, (1, 1, 1), tablero.NAVE_OCULTA)
    letras = {(1, 1, 1): "F"}
    
    # Octantes
    texto_oct = partida.vista_octantes(cubo, letras, 4, None)
    assert "Recorrido por octantes" in texto_oct
    assert "(1,1,1) F" in texto_oct
    
    # Espiral
    texto_esp = partida.vista_espiral(cubo, letras, 4, None)
    assert "Recorrido en espiral" in texto_esp
    assert "(1,1,1) F" in texto_esp
    
    # Propagacion
    texto_prop = partida.vista_propagacion(cubo, letras, 4, (1, 1, 1))
    assert "Recorrido por propagacion" in texto_prop
    assert "(1,1,1) F" in texto_prop

    # Verificacion de que esten en el diccionario de acciones de vista
    assert partida.OPCION_VISTA_OCTANTES in partida.ACCIONES_VISTA_CUBO
    assert partida.OPCION_VISTA_ESPIRAL in partida.ACCIONES_VISTA_CUBO
    assert partida.OPCION_VISTA_PROPAGACION in partida.ACCIONES_VISTA_CUBO


# ---------------------------------------------------------------------------
# Tests de regresion
# ---------------------------------------------------------------------------

def simular_entradas(monkeypatch, entradas):
    respuestas = iter(entradas)
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))


def test_limite_de_turnos_entre_maquinas():
    assert partida.calcular_limite_turnos(8) == 1100
    for n in (8, 10, 12):
        assert partida.calcular_limite_turnos(n) > 2 * (n ** 3 + 5)


def test_guardar_con_error_no_sale_de_la_partida(monkeypatch, capsys):
    def fallar(estado, nombre):
        raise OSError("disco lleno")

    monkeypatch.setattr("registro.guardar_partida", fallar)
    simular_entradas(monkeypatch, ["mi_partida"])
    estado = partida.nueva_partida_1v1(armar_configuracion())
    assert partida.accion_guardar_partida(estado, "Jugador 1") is True
    assert "Error al guardar" in capsys.readouterr().out


def test_maquina_vs_maquina_guarda_sale_y_se_retoma(tmp_path, monkeypatch):
    import registro
    monkeypatch.chdir(tmp_path)
    estado = partida.nueva_partida_maquina_vs_maquina(armar_configuracion())
    # Avanza dos turnos de a uno y despues guarda y sale
    simular_entradas(monkeypatch, ["2", "2", "3", "demo"])
    partida.ejecutar_bucle_turnos(estado)
    assert len(estado["historial"]) == 2
    recuperado = registro.cargar_partida("demo")
    simular_entradas(monkeypatch, ["2", "4"])
    partida.ejecutar_bucle_turnos(recuperado)
    assert len(recuperado["historial"]) == 3


def test_maquina_vs_maquina_sin_confirmar_no_juega(monkeypatch, capsys):
    simular_entradas(monkeypatch, ["1", "1", "n"])
    partida.iniciar_partida_maquina_vs_maquina()
    assert "Dispara a" not in capsys.readouterr().out


@pytest.mark.parametrize("error", [KeyboardInterrupt, EOFError])
def test_menu_principal_sale_con_mensaje_si_se_interrumpe(monkeypatch, capsys, error):
    def interrumpir(_):
        raise error

    monkeypatch.setattr("builtins.input", interrumpir)
    partida.ejecutar_menu_principal()
    assert "Saliendo del juego" in capsys.readouterr().out


@pytest.mark.parametrize("contenido", [
    "[1, 2]",
    '{"n": "8"}',
    "5",
    "no es json",
])
def test_cargar_partida_danada_vuelve_al_menu(tmp_path, monkeypatch, capsys, contenido):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "partidas").mkdir()
    (tmp_path / "partidas" / "mala.json").write_text(contenido, encoding="utf-8")
    simular_entradas(monkeypatch, ["mala"])
    partida.continuar_partida_guardada()
    assert "Error al cargar la partida" in capsys.readouterr().out


def test_fin_de_partida_muestra_ranking_y_exporta(tmp_path, monkeypatch, capsys):
    import registro
    monkeypatch.chdir(tmp_path)
    estado = partida.nueva_partida_1v1(armar_configuracion())
    registro.guardar_partida(estado, "final")
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (8, 8, 7), "eje": None, "valor": None})
    estado["turno_actual"] = "Jugador 1"
    registro.guardar_partida(estado, "final")
    # Carga la partida, hunde la ultima celda y exporta el reporte
    simular_entradas(monkeypatch, ["final", "1", "T", "8,8,8", "s"])
    partida.continuar_partida_guardada()
    salida = capsys.readouterr().out
    assert "=== Ranking de partidas ===" in salida
    assert registro.listar_ranking()[0]["partida"] == "final"
    assert (tmp_path / "exportaciones" / "final.txt").exists()


def test_fin_de_partida_con_ranking_danado_avisa(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "ranking.json").write_text("{}", encoding="utf-8")
    estado = partida.nueva_partida_1v1(armar_configuracion())
    estado["ganador"] = "Jugador 1"
    simular_entradas(monkeypatch, ["n"])
    partida.ejecutar_bucle_turnos(estado)
    assert partida.MENSAJE_RANKING_DANADO in capsys.readouterr().out
    assert (tmp_path / "ranking.json").read_text(encoding="utf-8") == "{}"


@pytest.mark.parametrize("opcion, entradas, titulo", [
    ("1", [], "CAPA z = 1"),
    ("2", ["3"], "CORTE x = 3"),
    ("3", ["4"], "CORTE y = 4"),
    ("4", [], "Recorrido por octantes"),
    ("5", [], "Recorrido en espiral"),
    ("6", [""], "Recorrido por propagacion"),
    ("7", [], "Recorrido por capas de x"),
    ("8", [], "Recorrido por capas de y"),
])
def test_ver_cubo_resuelve_cada_opcion(monkeypatch, capsys, opcion, entradas, titulo):
    simular_entradas(monkeypatch, [opcion] + entradas)
    estado = partida.nueva_partida_1v1(armar_configuracion())
    partida.mostrar_cubo_propio_y_rival(estado, "Jugador 1")
    assert titulo in capsys.readouterr().out


def test_ubicacion_manual_reinicia_si_una_nave_queda_sin_lugar(monkeypatch, capsys):
    cubo = tablero.crear_cubo(8)
    flota_jugador = flota.crear_flota()
    flota.ubicar_nave(cubo, flota_jugador, "F", (1, 1, 1), (1, 1, 2))
    # La primera consulta informa que no hay lugar; despues se corta la entrada
    consultas = iter(["E", None])
    monkeypatch.setattr("partida.obtener_nave_sin_lugar", lambda cubo_actual, pendientes: next(consultas))

    def interrumpir(_):
        raise EOFError

    monkeypatch.setattr("builtins.input", interrumpir)
    with pytest.raises(EOFError):
        partida.ubicar_flota_manual(cubo, flota_jugador)
    assert "Se reinicia la flota" in capsys.readouterr().out
    assert flota_jugador == {}
    assert cubo == tablero.crear_cubo(8)


def test_torpedo_guiado_informa_la_celda_alcanzada(capsys):
    estado = partida.nueva_partida_vs_maquina(armar_configuracion(), "dificil")
    estado["turno_actual"] = "Jugador 2"
    partida.ejecutar_turno(estado, {"arma": "T", "punto": (1, 1, 1), "eje": None, "valor": None})
    estado["turno_actual"] = "Jugador 2"
    partida.ejecutar_turno_maquina(estado)
    assert estado["ultima_jugada"]["arma"] == "G"
    salida = capsys.readouterr().out
    assert "--- Turno de la maquina ---" in salida
    assert "Dispara a 1,1,2. Impacto. Fragata hundida (2 de 2)." in salida
    mensaje = partida.formatear_mensaje_jugada(estado["flotas"]["Jugador 1"], estado["ultima_jugada"])
    assert mensaje.startswith("Torpedo guiado sobre la celda 1,1,2.")


@pytest.mark.parametrize("letra, desde, hasta, esperado", [
    ("F", (1, 1, 1), (1, 1, 2), "Impacto. Fragata averiada (1 de 2)."),
    ("D", (1, 1, 1), (1, 1, 3), "Impacto. Destructor averiado (1 de 3)."),
    ("S", (1, 1, 1), (1, 1, 3), "Impacto. Submarino averiado (1 de 3)."),
    ("C", (3, 1, 1), (3, 1, 4), "Impacto. Crucero averiado (1 de 4)."),
    ("P", (6, 1, 1), (6, 1, 5), "Impacto. Portaaviones averiado (0 de 5)."),
    ("E", (2, 2, 2), (3, 3, 3), "Impacto. Estacion orbital averiada (1 de 8)."),
])
def test_mensaje_de_impacto_concuerda_con_la_nave(letra, desde, hasta, esperado):
    cubo = tablero.crear_cubo(8)
    flota_rival = flota.crear_flota()
    flota.ubicar_nave(cubo, flota_rival, letra, desde, hasta)
    resultado = armamento.aplicar_disparo(cubo, flota_rival, "T", desde, None, armamento.CATALOGO_ARMAS)
    assert partida.formatear_mensaje_resultado(flota_rival, resultado) == esperado


def test_mensaje_del_sonar_indica_plano_y_contactos(monkeypatch, capsys):
    estado = partida.nueva_partida_1v1(armar_configuracion())
    simular_entradas(monkeypatch, ["S", "z", "8"])
    partida.realizar_disparo(estado, "Jugador 1")
    assert "Sonar sobre el plano z = 8. 2 contactos detectados." in capsys.readouterr().out


@pytest.mark.parametrize("jugada, error", [
    ({"arma": "Z", "punto": (4, 4, 4), "eje": None, "valor": None}, armamento.ArmaInvalidaError),
    ({"arma": "L", "punto": (4, 4, 4), "eje": "z", "valor": None}, armamento.ArmaInvalidaError),
    ({"arma": "R", "punto": (9, 9, 9), "eje": None, "valor": None}, tablero.PuntoInvalidoError),
    ({"arma": "S", "punto": None, "eje": "z", "valor": 9}, tablero.PuntoInvalidoError),
])
def test_jugada_invalida_no_descuenta_municion_ni_avanza(jugada, error):
    estado = partida.nueva_partida_1v1(armar_configuracion())
    municion = dict(estado["municiones"]["Jugador 1"])
    with pytest.raises(error):
        partida.ejecutar_turno(estado, jugada)
    assert estado["municiones"]["Jugador 1"] == municion
    assert estado["turno_actual"] == "Jugador 1"
    assert estado["historial"] == []


@pytest.mark.parametrize("nombre", ["CON", "nul", "Aux", "prn", "com1", "LPT9"])
def test_nombre_reservado_se_vuelve_a_pedir(monkeypatch, capsys, nombre):
    simular_entradas(monkeypatch, [nombre, "consola"])
    assert partida.pedir_nombre_partida() == "consola"
    assert "Nombre invalido" in capsys.readouterr().out


def test_entrada_no_decodificable_sale_con_mensaje(monkeypatch, capsys):
    def fallar(_):
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "byte invalido")

    monkeypatch.setattr("builtins.input", fallar)
    partida.ejecutar_menu_principal()
    assert partida.MENSAJE_ENTRADA_FINALIZADA in capsys.readouterr().out


def test_guardar_nombre_no_codificable_avisa_y_sigue(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    estado = partida.nueva_partida_1v1(armar_configuracion())
    estado["historial"] = [{"numero": 1, "jugador": "\ud800", "detalle": {"arma": "T"}}]
    simular_entradas(monkeypatch, ["rota"])
    assert partida.accion_guardar_partida(estado, "Jugador 1") is True
    assert "Error al guardar" in capsys.readouterr().out
    assert not (tmp_path / "partidas" / "rota.json").exists()


@pytest.mark.parametrize("n", [3, 5, 6, 16])
def test_tamano_invalido_avisa_y_vuelve_al_menu(monkeypatch, capsys, n):
    monkeypatch.setattr("tablero.TAMANO_CUBO", n)
    simular_entradas(monkeypatch, ["1", "2", "3", "5"])
    partida.ejecutar_menu_principal()
    assert capsys.readouterr().out.count("Tamano de cubo invalido") == 3


@pytest.mark.parametrize("n", [7, 12])
def test_partida_completa_con_otro_tamano(tmp_path, monkeypatch, capsys, n):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("tablero.TAMANO_CUBO", n)
    # Maquina contra maquina en facil, avanzando de a 50 turnos hasta el final
    pausas = partida.calcular_limite_turnos(n) // partida.TURNOS_ENTRE_PAUSAS + 1
    respuestas = iter(["1", "1", "s"] + ["1"] * pausas)

    def responder(mensaje):
        if mensaje.startswith("Exportar"):
            return "n"
        return next(respuestas)

    monkeypatch.setattr("builtins.input", responder)
    partida.iniciar_partida_maquina_vs_maquina()
    assert "Gano " in capsys.readouterr().out
