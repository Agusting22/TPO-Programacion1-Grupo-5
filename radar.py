import time

import tablero

PROFUNDIDAD_BUSQUEDA = 0
MILISEGUNDOS_POR_SEGUNDO = 1000


class EjeInvalidoError(tablero.ErrorCubo):
    pass


def buscar_naves_lineal(cubo):
    """
    Objetivo: buscar todas las celdas con nave recorriendo el cubo entero.
    Parametros: cubo.
    Retorna: tupla (lista de puntos encontrados, diccionario de metricas).
    """
    inicio = time.perf_counter()
    encontrados = []
    comparaciones = 0
    n = len(cubo)
    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                comparaciones = comparaciones + 1
                estado = tablero.leer_celda(cubo, (z, x, y))
                if estado == tablero.NAVE_OCULTA or estado == tablero.DETECTADO:
                    encontrados.append((z, x, y))
    tiempo_ms = (time.perf_counter() - inicio) * MILISEGUNDOS_POR_SEGUNDO
    metricas = {
        "comparaciones": comparaciones,
        "tiempo_ms": tiempo_ms,
        "profundidad_max": PROFUNDIDAD_BUSQUEDA,
    }
    return (encontrados, metricas)


def buscar_naves_optimizada(cubo, flota_jugador):
    """
    Objetivo: buscar las celdas con nave sin recorrer el cubo completo.
    Estrategia: la flota ya sabe que celdas ocupa cada nave, asi que en vez
    de mirar las N^3 celdas del cubo solo se consultan esas celdas puntuales.
    Parametros: cubo, flota_jugador (diccionario de naves con sus puntos).
    Retorna: tupla (lista de puntos encontrados, diccionario de metricas).
    """
    inicio = time.perf_counter()
    encontrados = []
    comparaciones = 0
    for id_nave in flota_jugador:
        for punto in flota_jugador[id_nave]["puntos"]:
            comparaciones = comparaciones + 1
            estado = tablero.leer_celda(cubo, punto)
            if estado == tablero.NAVE_OCULTA or estado == tablero.DETECTADO:
                encontrados.append(punto)
    tiempo_ms = (time.perf_counter() - inicio) * MILISEGUNDOS_POR_SEGUNDO
    metricas = {
        "comparaciones": comparaciones,
        "tiempo_ms": tiempo_ms,
        "profundidad_max": PROFUNDIDAD_BUSQUEDA,
    }
    return (encontrados, metricas)


def _buscar_capa_recursiva(cubo, z, encontrados, metricas):
    """
    Objetivo: revisar la capa z con ciclos y despues repetir lo mismo con la capa z + 1.
    El caso base es pasarse de la ultima capa.
    Parametros: cubo, z (capa a revisar), encontrados y metricas (se van completando).
    """
    if z > len(cubo):
        return
    metricas["profundidad_max"] = z
    for x in range(1, len(cubo) + 1):
        for y in range(1, len(cubo) + 1):
            metricas["comparaciones"] = metricas["comparaciones"] + 1
            estado = tablero.leer_celda(cubo, (z, x, y))
            if estado == tablero.NAVE_OCULTA or estado == tablero.DETECTADO:
                encontrados.append((z, x, y))
    _buscar_capa_recursiva(cubo, z + 1, encontrados, metricas)


def buscar_naves_recursiva(cubo):
    """
    Objetivo: buscar las celdas con nave capa por capa, con una funcion que se llama a si misma.
    Parametros: cubo.
    Retorna: tupla (lista de puntos encontrados, diccionario de metricas).
    """
    inicio = time.perf_counter()
    encontrados = []
    metricas = {"comparaciones": 0, "tiempo_ms": 0.0, "profundidad_max": 0}
    _buscar_capa_recursiva(cubo, 1, encontrados, metricas)
    metricas["tiempo_ms"] = (time.perf_counter() - inicio) * MILISEGUNDOS_POR_SEGUNDO
    return (encontrados, metricas)


def _celda_plano_z(valor, a, b):
    return (valor, a, b)


def _celda_plano_x(valor, a, b):
    return (a, valor, b)


def _celda_plano_y(valor, a, b):
    return (a, b, valor)


CONSTRUCTORES_PLANO = {
    tablero.EJE_Z: _celda_plano_z,
    tablero.EJE_X: _celda_plano_x,
    tablero.EJE_Y: _celda_plano_y,
}


def obtener_celdas_plano(eje, valor, n):
    """
    Objetivo: armar las celdas de un plano completo fijando un eje y su valor.
    Parametros: eje ("z", "x" o "y"), valor fijo del eje, n tamano del cubo.
    Retorna: lista con las N*N celdas de ese plano.
    Lanza: EjeInvalidoError si el eje no es valido.
    """
    if eje not in CONSTRUCTORES_PLANO:
        raise EjeInvalidoError("Eje invalido: " + str(eje))
    constructor = CONSTRUCTORES_PLANO[eje]
    celdas = []
    for a in range(1, n + 1):
        for b in range(1, n + 1):
            celdas.append(constructor(valor, a, b))
    return celdas


def aplicar_sonar(cubo, eje, valor):
    """
    Objetivo: aplicar el sonar, que revela un plano entero sin hacer dano.
    Parametros: cubo, eje ("z", "x" o "y"), valor fijo de ese eje.
    Retorna: lista de puntos con nave oculta que quedaron detectados.
    """
    n = len(cubo)
    celdas = obtener_celdas_plano(eje, valor, n)
    reveladas = []
    for punto in celdas:
        if tablero.leer_celda(cubo, punto) == tablero.NAVE_OCULTA:
            tablero.escribir_celda(cubo, punto, tablero.DETECTADO)
            reveladas.append(punto)
    return reveladas
