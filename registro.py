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


def guardar_partida(estado, nombre):
    raise NotImplementedError("El guardado de partidas se agrega en la Entrega 3")


def cargar_partida(nombre):
    raise NotImplementedError("La carga de partidas se agrega en la Entrega 3")


def listar_partidas():
    raise NotImplementedError("El listado de partidas se agrega en la Entrega 3")
