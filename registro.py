def crear_historial():
    return []


def registrar_evento(historial, jugador, detalle):
    evento = {"numero": len(historial) + 1, "jugador": jugador, "detalle": detalle}
    historial.append(evento)
    return historial


def obtener_eventos(historial):
    return historial.copy()
