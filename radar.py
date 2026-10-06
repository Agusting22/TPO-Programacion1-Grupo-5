import time

import tablero

PROFUNDIDAD_BUSQUEDA_LINEAL = 0
MILISEGUNDOS_POR_SEGUNDO = 1000


def buscar_naves_lineal(cubo):
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
        "profundidad_max": PROFUNDIDAD_BUSQUEDA_LINEAL,
    }
    return (encontrados, metricas)
