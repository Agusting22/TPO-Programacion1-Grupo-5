import json
import os
import time

import armamento
import flota
import tablero

DIRECTORIO_PARTIDAS = "partidas"
DIRECTORIO_EXPORTACIONES = "exportaciones"
ARCHIVO_RANKING = "ranking.json"
ESTADOS_CELDA = (
    tablero.AGUA_SIN_EXPLORAR, tablero.NAVE_OCULTA, tablero.AGUA_MARCADA,
    tablero.IMPACTO, tablero.HUNDIDO, tablero.DETECTADO,
)
CONTADORES_ESTADISTICAS = ("disparos", "aciertos", "fallos", "naves_hundidas")


class DatosInvalidosError(tablero.ErrorCubo):
    """Se lanza cuando los datos de una partida guardada estan mal formados."""
    pass


class RankingInvalidoError(tablero.ErrorCubo):
    """Se lanza cuando el archivo de ranking existe pero esta danado."""
    pass


# ---------------------------------------------------------------------------
# Historial y estadisticas (funciones existentes de Entrega 2)
# ---------------------------------------------------------------------------

def crear_historial():
    """
    Objetivo: iniciar el historial de una partida.
    Parametros: ninguno.
    Retorna: lista vacia.
    """
    return []


def registrar_evento(historial, jugador, detalle):
    """
    Objetivo: agregar un evento numerado al historial.
    Parametros: historial (list), jugador (str), detalle (dict) de la jugada.
    Retorna: historial actualizado.
    """
    evento = {"numero": len(historial) + 1, "jugador": jugador, "detalle": detalle}
    historial.append(evento)
    return historial


def obtener_eventos(historial):
    """
    Objetivo: consultar los eventos sin modificar el historial.
    Parametros: historial (list).
    Retorna: copia de la lista de eventos.
    """
    return historial.copy()


def crear_estadisticas(jugadores):
    """
    Objetivo: iniciar las estadisticas de la partida en cero.
    Parametros: lista con los nombres de los jugadores.
    Retorna: diccionario jugador -> contadores de disparos, aciertos, etc.
    """
    estadisticas = {}
    for nombre in jugadores:
        estadisticas[nombre] = {
            "disparos": 0,
            "aciertos": 0,
            "fallos": 0,
            "naves_hundidas": 0,
        }
    return estadisticas


def registrar_disparo(estadisticas, jugador, impacto):
    """
    Objetivo: sumar un disparo y su acierto o fallo.
    Parametros: estadisticas (dict), jugador (str), impacto (bool).
    Retorna: estadisticas actualizadas.
    """
    estadisticas[jugador]["disparos"] = estadisticas[jugador]["disparos"] + 1
    if impacto:
        estadisticas[jugador]["aciertos"] = estadisticas[jugador]["aciertos"] + 1
    else:
        estadisticas[jugador]["fallos"] = estadisticas[jugador]["fallos"] + 1
    return estadisticas


def registrar_nave_hundida(estadisticas, jugador):
    """
    Objetivo: sumar una nave hundida a un jugador.
    Parametros: estadisticas (dict), jugador (str).
    Retorna: estadisticas actualizadas.
    """
    estadisticas[jugador]["naves_hundidas"] = estadisticas[jugador]["naves_hundidas"] + 1
    return estadisticas


def formatear_resumen(estadisticas):
    """
    Objetivo: armar un texto prolijo con el resumen final de la partida.
    Parametros: diccionario de estadisticas.
    Retorna: texto con una linea por jugador.
    """
    lineas = ["--- Estadisticas ---"]
    for jugador in estadisticas:
        datos = estadisticas[jugador]
        lineas.append(
            jugador + ": " + str(datos["disparos"]) + " disparos, "
            + str(datos["aciertos"]) + " aciertos, " + str(datos["fallos"]) + " fallos, "
            + str(datos["naves_hundidas"]) + " naves hundidas"
        )
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Serializacion / deserializacion del estado
# ---------------------------------------------------------------------------

def _serializar_jugada(jugada):
    """
    Objetivo: convertir una jugada a un dict JSON-serializable (tuplas -> listas).
    Parametros: jugada (dict con claves arma, punto, eje, valor, resultado).
    Retorna: dict serializable.
    """
    copia = dict(jugada)
    if copia.get("punto") is not None:
        copia["punto"] = list(copia["punto"])
    resultado = copia.get("resultado")
    if isinstance(resultado, dict):
        resultado_copia = dict(resultado)
        if "celdas_impactadas" in resultado_copia:
            resultado_copia["celdas_impactadas"] = [
                [list(celda) if isinstance(celda, tuple) else celda, id_nave, tipo]
                for celda, id_nave, tipo in resultado_copia["celdas_impactadas"]
            ]
        if "reveladas" in resultado_copia:
            resultado_copia["reveladas"] = [
                list(p) if isinstance(p, tuple) else p
                for p in resultado_copia["reveladas"]
            ]
        copia["resultado"] = resultado_copia
    return copia


def _deserializar_jugada(jugada_datos):
    """
    Objetivo: reconstruir una jugada desde los datos JSON (listas -> tuplas).
    Parametros: jugada_datos (dict leido de JSON).
    Retorna: jugada con tuplas donde corresponde.
    """
    copia = dict(jugada_datos)
    if copia.get("punto") is not None:
        copia["punto"] = tuple(copia["punto"])
    resultado = copia.get("resultado")
    if isinstance(resultado, dict):
        resultado_copia = dict(resultado)
        if "celdas_impactadas" in resultado_copia:
            resultado_copia["celdas_impactadas"] = [
                (tuple(celda), id_nave, tipo)
                for celda, id_nave, tipo in resultado_copia["celdas_impactadas"]
            ]
        if "celdas_agua" in resultado_copia:
            resultado_copia["celdas_agua"] = [
                tuple(p) for p in resultado_copia["celdas_agua"]
            ]
        if "reveladas" in resultado_copia:
            resultado_copia["reveladas"] = [
                tuple(p) for p in resultado_copia["reveladas"]
            ]
        copia["resultado"] = resultado_copia
    return copia


def _serializar_flota_jugador(flota_jugador):
    """
    Objetivo: convertir la flota a formato JSON-serializable usando flota.guardar_datos_flota.
    Parametros: flota_jugador.
    Retorna: dict serializable.
    """
    return flota.guardar_datos_flota(flota_jugador)


def _deserializar_flota_jugador(datos_flota):
    """
    Objetivo: reconstruir la flota desde los datos JSON.
    Parametros: datos_flota (dict).
    Retorna: flota_jugador reconstruida.
    """
    return flota.reponer_flota(datos_flota)


# ---------------------------------------------------------------------------
# Validacion de los datos leidos de archivos
# ---------------------------------------------------------------------------

def _exigir(condicion, mensaje):
    """
    Objetivo: cortar la carga de una partida si no se cumple una condicion.
    Parametros: condicion (bool), mensaje (str) descripcion del problema.
    Retorna: None.
    Lanza: DatosInvalidosError si la condicion es falsa.
    """
    if not condicion:
        raise DatosInvalidosError(mensaje)


def _validar_cubo(cubo, n):
    """
    Objetivo: verificar que un cubo guardado sea de n x n x n con estados conocidos.
    Parametros: cubo (dato leido), n (int) tamano esperado.
    Retorna: None.
    Lanza: DatosInvalidosError si el cubo esta mal formado.
    """
    _exigir(isinstance(cubo, list) and len(cubo) == n, "Cubo incompleto")
    for capa in cubo:
        _exigir(isinstance(capa, list) and len(capa) == n, "Capa incompleta")
        for fila in capa:
            _exigir(isinstance(fila, list) and len(fila) == n, "Fila incompleta")
            for celda in fila:
                _exigir(celda in ESTADOS_CELDA, "Estado de celda invalido")


def _validar_datos_jugador(datos, nombre, n):
    """
    Objetivo: verificar cubo, flota, municion y estadisticas guardadas de un jugador.
    Parametros: datos (dict) leido de JSON, nombre (str) del jugador, n (int).
    Retorna: None.
    Lanza: ErrorCubo, KeyError o TypeError si los datos estan mal formados.
    """
    _validar_cubo(datos["cubos"][nombre], n)
    flota.validar_datos_flota(datos["flotas"][nombre])
    for letra in armamento.CATALOGO_ARMAS:
        cantidad = datos["municiones"][nombre][letra]
        ilimitada = armamento.CATALOGO_ARMAS[letra]["municion_inicial"] is None
        _exigir(isinstance(cantidad, int) or (ilimitada and cantidad is None), "Municion invalida")
    for contador in CONTADORES_ESTADISTICAS:
        valor = datos["estadisticas"][nombre][contador]
        _exigir(isinstance(valor, int), "Estadisticas invalidas")


def _validar_datos_partida(datos):
    """
    Objetivo: verificar la estructura de una partida guardada antes de reconstruirla.
    Parametros: datos (dato leido de JSON).
    Retorna: None.
    Lanza: ErrorCubo, KeyError o TypeError si los datos estan mal formados.
    """
    _exigir(isinstance(datos, dict), "El archivo no contiene una partida")
    n = datos["n"]
    _exigir(isinstance(n, int) and n > 0, "Tamano de cubo invalido")
    jugadores = [datos["jugador_1"], datos["jugador_2"]]
    for nombre in jugadores:
        _exigir(isinstance(nombre, str), "Nombre de jugador invalido")
        _validar_datos_jugador(datos, nombre, n)
    _exigir(jugadores[0] != jugadores[1], "Jugadores repetidos")
    _exigir(datos["turno_actual"] in jugadores, "Turno invalido")
    _exigir(datos["ganador"] is None or datos["ganador"] in jugadores, "Ganador invalido")
    dificultad = datos.get("dificultad")
    _exigir(dificultad is None or isinstance(dificultad, str), "Dificultad invalida")
    dificultades = datos.get("dificultades")
    if dificultades is not None:
        _exigir(isinstance(dificultades, dict), "Dificultades invalidas")
        for valor in dificultades.values():
            _exigir(isinstance(valor, str), "Dificultades invalidas")
    _exigir(isinstance(datos["historial"], list), "Historial invalido")
    for evento in datos["historial"]:
        _exigir(isinstance(evento["detalle"], dict), "Historial invalido")


def serializar_estado(estado):
    """
    Objetivo: convertir el estado completo de una partida a un dict JSON-serializable.
    Parametros: estado (dict con cubos, flotas, municiones, etc.).
    Retorna: dict JSON-serializable.
    """
    datos = {}
    datos["n"] = estado["n"]
    datos["jugador_1"] = estado["jugador_1"]
    datos["jugador_2"] = estado["jugador_2"]
    datos["turno_actual"] = estado["turno_actual"]
    datos["ganador"] = estado["ganador"]
    datos["es_vs_maquina"] = estado["es_vs_maquina"]
    datos["es_maquina_vs_maquina"] = estado.get("es_maquina_vs_maquina", False)
    datos["dificultad"] = estado.get("dificultad", None)
    datos["dificultades"] = estado.get("dificultades", None)
    # Cubos: 3D list de ints, ya es serializable
    datos["cubos"] = estado["cubos"]
    # Flotas
    datos["flotas"] = {
        nombre: _serializar_flota_jugador(f)
        for nombre, f in estado["flotas"].items()
    }
    # Municiones: {letra: int o None}, serializable
    datos["municiones"] = estado["municiones"]
    # Estadisticas: {jugador: {disparos, aciertos, fallos, naves_hundidas}}, serializable
    datos["estadisticas"] = estado["estadisticas"]
    # Historial: cada evento contiene una jugada con posibles tuplas
    eventos_serializados = []
    for evento in estado["historial"]:
        evento_copia = {
            "numero": evento["numero"],
            "jugador": evento["jugador"],
            "detalle": _serializar_jugada(evento["detalle"]),
        }
        eventos_serializados.append(evento_copia)
    datos["historial"] = eventos_serializados
    return datos


def deserializar_estado(datos):
    """
    Objetivo: reconstruir el estado de partida desde un dict leido de JSON.
    Parametros: datos (dict).
    Retorna: estado de partida listo para usar.
    Lanza: ErrorCubo, KeyError, TypeError, ValueError o AttributeError si los datos
    estan mal formados.
    """
    _validar_datos_partida(datos)
    estado = {}
    estado["n"] = datos["n"]
    estado["jugador_1"] = datos["jugador_1"]
    estado["jugador_2"] = datos["jugador_2"]
    estado["turno_actual"] = datos["turno_actual"]
    estado["ganador"] = datos["ganador"]
    estado["es_vs_maquina"] = datos["es_vs_maquina"]
    estado["es_maquina_vs_maquina"] = datos.get("es_maquina_vs_maquina", False)
    if datos.get("dificultad") is not None:
        estado["dificultad"] = datos["dificultad"]
    if datos.get("dificultades") is not None:
        estado["dificultades"] = datos["dificultades"]
    # Cubos
    estado["cubos"] = datos["cubos"]
    # Flotas
    estado["flotas"] = {
        nombre: _deserializar_flota_jugador(f_datos)
        for nombre, f_datos in datos["flotas"].items()
    }
    # Reparar estados del cubo segun la flota restaurada
    for nombre in estado["flotas"]:
        flota.reponer_flota_en_cubo(estado["cubos"][nombre], estado["flotas"][nombre])
        for nave in estado["flotas"][nombre].values():
            for cantidad in nave["impactos"].values():
                _exigir(isinstance(cantidad, int), "Impactos invalidos")
    # Municiones
    estado["municiones"] = datos["municiones"]
    # Estadisticas
    estado["estadisticas"] = datos["estadisticas"]
    # Historial
    estado["historial"] = [
        {
            "numero": ev["numero"],
            "jugador": ev["jugador"],
            "detalle": _deserializar_jugada(ev["detalle"]),
        }
        for ev in datos["historial"]
    ]
    return estado


# ---------------------------------------------------------------------------
# Persistencia de partidas (Entrega 3)
# ---------------------------------------------------------------------------

def _ruta_partida(nombre):
    """
    Objetivo: armar la ruta relativa del archivo de una partida.
    Parametros: nombre (str sin extension).
    Retorna: str ruta del archivo.
    """
    return os.path.join(DIRECTORIO_PARTIDAS, nombre + ".json")


def guardar_partida(estado, nombre):
    """
    Objetivo: guardar el estado de la partida en un archivo JSON.
    Parametros: estado (dict), nombre (str sin extension).
    Retorna: None.
    Lanza: OSError si no se puede escribir el archivo.
    """
    os.makedirs(DIRECTORIO_PARTIDAS, exist_ok=True)
    datos = serializar_estado(estado)
    ruta = _ruta_partida(nombre)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def cargar_partida(nombre):
    """
    Objetivo: cargar el estado de una partida guardada desde JSON.
    Parametros: nombre (str sin extension).
    Retorna: estado reconstruido (dict).
    Lanza: FileNotFoundError si el archivo no existe, ValueError si el JSON es invalido,
    ErrorCubo, KeyError, TypeError o AttributeError si la estructura es incorrecta,
    RecursionError si el JSON esta anidado en exceso.
    """
    ruta = _ruta_partida(nombre)
    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return deserializar_estado(datos)


def listar_partidas():
    """
    Objetivo: listar los nombres de las partidas guardadas.
    Parametros: ninguno.
    Retorna: lista de nombres (str) sin extension, ordenada alfabeticamente.
    """
    if not os.path.isdir(DIRECTORIO_PARTIDAS):
        return []
    nombres = []
    for archivo in os.listdir(DIRECTORIO_PARTIDAS):
        if archivo.endswith(".json"):
            nombres.append(archivo[:-5])
    return sorted(nombres)


# ---------------------------------------------------------------------------
# Ranking (Entrega 3)
# ---------------------------------------------------------------------------

def guardar_ranking(ganador, nombre_partida, turnos, es_vs_maquina):
    """
    Objetivo: agregar una entrada al ranking de partidas terminadas.
    Parametros: ganador (str), nombre_partida (str), turnos (int),
    es_vs_maquina (bool).
    Retorna: None.
    Lanza: RankingInvalidoError si el archivo existente esta danado (no se modifica),
    OSError si no se puede escribir.
    """
    ranking = listar_ranking()
    entrada = {
        "ganador": ganador,
        "partida": nombre_partida,
        "turnos": turnos,
        "es_vs_maquina": es_vs_maquina,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    ranking.append(entrada)
    with open(ARCHIVO_RANKING, "w", encoding="utf-8") as archivo:
        json.dump(ranking, archivo, ensure_ascii=False, indent=2)


def _es_entrada_valida(entrada):
    """
    Objetivo: verificar que una entrada del ranking tenga los datos necesarios.
    Parametros: entrada (dato leido de JSON).
    Retorna: True si la entrada es valida.
    """
    if not isinstance(entrada, dict):
        return False
    return (
        isinstance(entrada.get("ganador"), str)
        and isinstance(entrada.get("turnos"), int)
        and isinstance(entrada.get("timestamp", ""), str)
    )


def listar_ranking():
    """
    Objetivo: leer el archivo de ranking y devolver la lista de entradas.
    Parametros: ninguno.
    Retorna: lista de dicts con ganador, partida, turnos, timestamp.
    Lanza: RankingInvalidoError si el archivo existe pero esta danado.
    """
    if not os.path.exists(ARCHIVO_RANKING):
        return []
    try:
        with open(ARCHIVO_RANKING, "r", encoding="utf-8") as archivo:
            ranking = json.load(archivo)
    except (ValueError, OSError, RecursionError) as error:
        raise RankingInvalidoError("No se pudo leer el ranking: " + str(error))
    if not isinstance(ranking, list):
        raise RankingInvalidoError("El ranking no es una lista")
    for entrada in ranking:
        if not _es_entrada_valida(entrada):
            raise RankingInvalidoError("El ranking tiene entradas invalidas")
    return ranking


def formatear_ranking(entradas):
    """
    Objetivo: armar un texto con el ranking de partidas.
    Parametros: lista de entradas del ranking.
    Retorna: texto con una linea por entrada.
    """
    if not entradas:
        return "No hay partidas registradas en el ranking."
    lineas = ["=== Ranking de partidas ==="]
    for i in range(len(entradas)):
        entrada = entradas[i]
        modo = "vs maquina" if entrada.get("es_vs_maquina") else "1v1"
        lineas.append(
            str(i + 1) + ". " + entrada["ganador"]
            + " | " + str(entrada.get("partida", ""))
            + " | " + str(entrada["turnos"]) + " turnos"
            + " | " + modo
            + " | " + entrada.get("timestamp", "")
        )
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Exportacion de reportes (Entrega 3)
# ---------------------------------------------------------------------------

def _formatear_celda(punto):
    """
    Objetivo: representar un punto del cubo como texto.
    Parametros: punto (tuple) coordenada (z, x, y).
    Retorna: str con el formato "z,x,y".
    """
    return ",".join([str(valor) for valor in punto])


def _describir_jugada(jugada):
    """
    Objetivo: describir en una linea una jugada del historial.
    Parametros: jugada (dict con claves arma, punto, eje, valor, resultado).
    Retorna: str con el arma, el objetivo y el resultado.
    """
    letra = str(jugada.get("arma"))
    texto = armamento.CATALOGO_ARMAS.get(letra, {}).get("nombre", letra)
    if jugada.get("punto") is not None:
        texto = texto + " apuntado a " + _formatear_celda(jugada["punto"])
    if jugada.get("eje") is not None:
        texto = texto + " (eje " + str(jugada["eje"]) + ")"
    if jugada.get("valor") is not None:
        texto = texto + " valor " + str(jugada["valor"])
    resultado = jugada.get("resultado")
    if resultado is None:
        return texto + "."
    if resultado.get("tipo") == "sonar":
        return texto + ". Celdas reveladas: " + str(len(resultado.get("reveladas", []))) + "."
    impactos = [
        id_nave + " en " + _formatear_celda(celda)
        for celda, id_nave, tipo in resultado.get("celdas_impactadas", [])
    ]
    if impactos:
        texto = texto + ". Impactos: " + "; ".join(impactos)
    else:
        texto = texto + ". Sin impactos"
    if resultado.get("naves_hundidas"):
        texto = texto + ". Hundidas: " + ", ".join(resultado["naves_hundidas"])
    return texto + "."


def _obtener_modo(estado):
    """
    Objetivo: obtener el nombre del formato de una partida.
    Parametros: estado (dict).
    Retorna: str con el formato.
    """
    if estado.get("es_maquina_vs_maquina", False):
        return "maquina contra maquina"
    if estado.get("es_vs_maquina", False):
        return "uno contra la maquina"
    return "uno contra uno"


def formatear_reporte(estado, nombre):
    """
    Objetivo: armar el texto del reporte de una partida (resumen e historial).
    Parametros: estado (dict), nombre (str) de la partida.
    Retorna: str con el reporte completo.
    """
    ganador = estado["ganador"]
    if ganador is None:
        ganador = "sin ganador"
    lineas = [
        "===== Reporte de partida: " + nombre + " =====",
        "Fecha: " + time.strftime("%Y-%m-%dT%H:%M:%S"),
        "Modo: " + _obtener_modo(estado),
        "Jugadores: " + estado["jugador_1"] + " y " + estado["jugador_2"],
        "Ganador: " + ganador,
        "Turnos jugados: " + str(len(estado["historial"])),
        "",
        formatear_resumen(estado["estadisticas"]),
        "",
        "--- Historial ---",
    ]
    for evento in estado["historial"]:
        lineas.append(
            str(evento["numero"]) + ". " + evento["jugador"] + ": "
            + _describir_jugada(evento["detalle"])
        )
    return "\n".join(lineas) + "\n"


def exportar_reporte(estado, nombre):
    """
    Objetivo: escribir el reporte de una partida en un archivo de texto.
    Parametros: estado (dict), nombre (str sin extension).
    Retorna: str ruta relativa del archivo escrito.
    Lanza: OSError si no se puede escribir el archivo.
    """
    os.makedirs(DIRECTORIO_EXPORTACIONES, exist_ok=True)
    ruta = os.path.join(DIRECTORIO_EXPORTACIONES, nombre + ".txt")
    texto = formatear_reporte(estado, nombre)
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(texto)
    return ruta
