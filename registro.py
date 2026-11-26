import json
import os
import time

import flota

DIRECTORIO_PARTIDAS = "partidas"
ARCHIVO_RANKING = "ranking.json"


# ---------------------------------------------------------------------------
# Historial y estadisticas (funciones existentes de Entrega 2)
# ---------------------------------------------------------------------------

def crear_historial():
    return []


def registrar_evento(historial, jugador, detalle):
    evento = {"numero": len(historial) + 1, "jugador": jugador, "detalle": detalle}
    historial.append(evento)
    return historial


def obtener_eventos(historial):
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
    estadisticas[jugador]["disparos"] = estadisticas[jugador]["disparos"] + 1
    if impacto:
        estadisticas[jugador]["aciertos"] = estadisticas[jugador]["aciertos"] + 1
    else:
        estadisticas[jugador]["fallos"] = estadisticas[jugador]["fallos"] + 1
    return estadisticas


def registrar_nave_hundida(estadisticas, jugador):
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
    """
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
    Lanza: FileNotFoundError si el archivo no existe, ValueError si el JSON es invalido.
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


def eliminar_partida(nombre):
    """
    Objetivo: eliminar una partida guardada.
    Parametros: nombre (str sin extension).
    Retorna: True si se elimino, False si no existia.
    """
    ruta = _ruta_partida(nombre)
    if os.path.exists(ruta):
        os.remove(ruta)
        return True
    return False


# ---------------------------------------------------------------------------
# Ranking (Entrega 3)
# ---------------------------------------------------------------------------

def guardar_ranking(ganador, nombre_partida, turnos, es_vs_maquina):
    """
    Objetivo: agregar una entrada al ranking de partidas terminadas.
    Parametros: ganador (str), nombre_partida (str), turnos (int),
    es_vs_maquina (bool).
    Retorna: None.
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


def listar_ranking():
    """
    Objetivo: leer el archivo de ranking y devolver la lista de entradas.
    Parametros: ninguno.
    Retorna: lista de dicts con ganador, partida, turnos, timestamp.
    """
    if not os.path.exists(ARCHIVO_RANKING):
        return []
    try:
        with open(ARCHIVO_RANKING, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return []


def formatear_ranking(entradas):
    """
    Objetivo: armar un texto con el ranking de partidas.
    Parametros: lista de entradas del ranking.
    Retorna: texto con una linea por entrada.
    """
    if not entradas:
        return "No hay partidas registradas en el ranking."
    lineas = ["=== Ranking de partidas ==="]
    for i, entrada in enumerate(entradas, 1):
        modo = "vs maquina" if entrada.get("es_vs_maquina") else "1v1"
        lineas.append(
            str(i) + ". " + entrada["ganador"]
            + " | " + str(entrada["turnos"]) + " turnos"
            + " | " + modo
            + " | " + entrada.get("timestamp", "")
        )
    return "\n".join(lineas)
