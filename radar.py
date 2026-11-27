import time

import tablero

PROFUNDIDAD_BUSQUEDA = 0
MILISEGUNDOS_POR_SEGUNDO = 1000

# Identificadores de los recorridos del cubo
NOMBRE_RECORRIDO_CAPAS = "capas"
NOMBRE_RECORRIDO_OCTANTES = "octantes"
NOMBRE_RECORRIDO_ESPIRAL = "espiral"
NOMBRE_RECORRIDO_PROPAGACION = "propagacion"
NOMBRE_RECORRIDO_CAPAS_X = "capas_x"
NOMBRE_RECORRIDO_CAPAS_Y = "capas_y"


class EjeInvalidoError(tablero.ErrorCubo):
    """Se lanza cuando el eje de un plano no es z, x ni y."""
    pass


class RecorridoInvalidoError(tablero.ErrorCubo):
    """Se lanza cuando se solicita un recorrido del cubo no soportado o desconocido."""
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
    Lanza: PuntoInvalidoError si la flota tiene puntos fuera del cubo.
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
    Retorna: None.
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


DIRECCIONES_DE_NAVE = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def _recta_de_celdas(inicio, direccion, largo):
    """
    Objetivo: generar las celdas de una recta desde un punto.
    Parametros: inicio (tuple) punto inicial, direccion (tuple) avance por eje, largo (int).
    Retorna: list de puntos (pueden quedar fuera del cubo).
    """
    celdas = []
    for i in range(largo):
        celdas.append((inicio[0] + i * direccion[0], inicio[1] + i * direccion[1], inicio[2] + i * direccion[2]))
    return celdas


def _recta_es_posible(cubo, recta):
    """
    Objetivo: verificar si una nave todavia podria ocupar una recta.
    Parametros: cubo (list) tablero 3D, recta (list) de puntos.
    Retorna: True si la recta entra en el cubo y no tiene agua marcada ni hundido.
    """
    for punto in recta:
        if not tablero.es_punto_valido(punto, len(cubo)):
            return False
        if tablero.leer_celda(cubo, punto) in (tablero.AGUA_MARCADA, tablero.HUNDIDO):
            return False
    return True


def mapa_probabilidad(cubo, largos):
    """
    Objetivo: contar, para cada celda, en cuantas posiciones posibles de las naves restantes esta.
    Una posicion es una recta de celdas (sobre z, x o y) que no tiene agua marcada ni hundido.
    La nave oculta cuenta como sin explorar, para no filtrar donde esta la flota.
    La estacion orbital (bloque 2x2x2) no se cuenta.
    Parametros: cubo, largos (lista con el largo de cada nave restante).
    Retorna: matriz [z][x][y] de enteros con el mismo tamano que el cubo.
    """
    n = len(cubo)
    mapa = tablero.crear_cubo(n)
    for largo in largos:
        for direccion in DIRECCIONES_DE_NAVE:
            for z in range(1, n + 1):
                for x in range(1, n + 1):
                    for y in range(1, n + 1):
                        recta = _recta_de_celdas((z, x, y), direccion, largo)
                        if _recta_es_posible(cubo, recta):
                            for punto in recta:
                                tablero.escribir_celda(mapa, punto, tablero.leer_celda(mapa, punto) + 1)
    return mapa


def _celda_plano_z(valor, a, b):
    """
    Objetivo: armar un punto del plano con z fijo.
    Parametros: valor de z, a (x), b (y).
    Retorna: tuple punto (z, x, y).
    """
    return (valor, a, b)


def _celda_plano_x(valor, a, b):
    """
    Objetivo: armar un punto del plano con x fijo.
    Parametros: valor de x, a (z), b (y).
    Retorna: tuple punto (z, x, y).
    """
    return (a, valor, b)


def _celda_plano_y(valor, a, b):
    """
    Objetivo: armar un punto del plano con y fijo.
    Parametros: valor de y, a (z), b (x).
    Retorna: tuple punto (z, x, y).
    """
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
    Lanza: EjeInvalidoError si el eje no es valido, PuntoInvalidoError si el valor
    esta fuera del cubo.
    """
    n = len(cubo)
    celdas = obtener_celdas_plano(eje, valor, n)
    reveladas = []
    for punto in celdas:
        if tablero.leer_celda(cubo, punto) == tablero.NAVE_OCULTA:
            tablero.escribir_celda(cubo, punto, tablero.DETECTADO)
            reveladas.append(punto)
    return reveladas


# ---------------------------------------------------------------------------
# Recorridos recursivos del cubo (Entrega 3)
# ---------------------------------------------------------------------------

def _recorrer_octante(z1, z2, x1, x2, y1, y2):
    """
    Objetivo: funcion recursiva auxiliar para recorrer un sub-bloque dividiendolo en octantes.
    Parametros: z1, z2 (int) rango en z; x1, x2 (int) rango en x; y1, y2 (int) rango en y.
    Retorna: list de tuplas (z, x, y) de las celdas del sub-bloque.
    """
    if z1 > z2 or x1 > x2 or y1 > y2:
        return []
    if z1 == z2 and x1 == x2 and y1 == y2:
        return [(z1, x1, y1)]

    zm = (z1 + z2) // 2
    xm = (x1 + x2) // 2
    ym = (y1 + y2) // 2

    if z1 < z2:
        rangos_z = [(z1, zm), (zm + 1, z2)]
    else:
        rangos_z = [(z1, z2)]

    if x1 < x2:
        rangos_x = [(x1, xm), (xm + 1, x2)]
    else:
        rangos_x = [(x1, x2)]

    if y1 < y2:
        rangos_y = [(y1, ym), (ym + 1, y2)]
    else:
        rangos_y = [(y1, y2)]

    puntos = []
    for rz1, rz2 in rangos_z:
        for rx1, rx2 in rangos_x:
            for ry1, ry2 in rangos_y:
                sub_puntos = _recorrer_octante(rz1, rz2, rx1, rx2, ry1, ry2)
                for punto in sub_puntos:
                    puntos.append(punto)
    return puntos


def recorrido_octantes(cubo_o_n):
    """
    Objetivo: generar el recorrido del cubo mediante subdivision recursiva por octantes (3D).
    Parametros: cubo_o_n (list o int) cubo tridimensional o dimension entera n.
    Retorna: list de tuplas (z, x, y) con las celdas agrupadas por subcubos jerarquicos.
    Lanza: ErrorCubo si la dimension no es valida.
    """
    n = tablero.obtener_tamano(cubo_o_n)
    return _recorrer_octante(1, n, 1, n, 1, n)


def _recorrer_capa_espiral(z, x1, x2, y1, y2):
    """
    Objetivo: funcion recursiva auxiliar que recorre una capa 2D de afuera hacia adentro en espiral.
    Parametros: z (int) capa actual; x1, x2 (int) rango de filas; y1, y2 (int) rango de columnas.
    Retorna: list de tuplas (z, x, y) de la capa en espiral.
    """
    if x1 > x2 or y1 > y2:
        return []
    if x1 == x2:
        puntos = []
        for y in range(y1, y2 + 1):
            puntos.append((z, x1, y))
        return puntos
    if y1 == y2:
        puntos = []
        for x in range(x1, x2 + 1):
            puntos.append((z, x, y1))
        return puntos

    anillo = []
    for y in range(y1, y2 + 1):
        anillo.append((z, x1, y))
    for x in range(x1 + 1, x2 + 1):
        anillo.append((z, x, y2))
    for paso in range(y1, y2):
        anillo.append((z, x2, y1 + y2 - 1 - paso))
    for paso in range(x1 + 1, x2):
        anillo.append((z, x1 + x2 - paso, y1))

    sub_espiral = _recorrer_capa_espiral(z, x1 + 1, x2 - 1, y1 + 1, y2 - 1)
    for punto in sub_espiral:
        anillo.append(punto)
    return anillo


def _recorrer_capas_espiral(z_actual, n):
    """
    Objetivo: recorrer recursivamente las capas de 1 a n aplicando espiral en cada una.
    Parametros: z_actual (int) indice de capa actual, n (int) dimension total.
    Retorna: list de tuplas (z, x, y) acumuladas.
    """
    if z_actual > n:
        return []
    capa = _recorrer_capa_espiral(z_actual, 1, n, 1, n)
    resto = _recorrer_capas_espiral(z_actual + 1, n)
    resultado = []
    for punto in capa:
        resultado.append(punto)
    for punto in resto:
        resultado.append(punto)
    return resultado


def recorrido_espiral(cubo_o_n):
    """
    Objetivo: generar el recorrido del cubo en espiral concentrica capa por capa de forma recursiva.
    Parametros: cubo_o_n (list o int) cubo tridimensional o dimension entera n.
    Retorna: list de tuplas (z, x, y) recorriendo los bordes exteriores hacia el centro en cada capa.
    Lanza: ErrorCubo si la dimension no es valida.
    """
    n = tablero.obtener_tamano(cubo_o_n)
    return _recorrer_capas_espiral(1, n)


def _propagar_recursivo(frontera, visitados, n, resultado):
    """
    Objetivo: propagar recursivamente por niveles de distancia ortogonal desde una frontera de celdas.
    Parametros: frontera (list) celdas del nivel actual, visitados (set) celdas ya recorridas,
                n (int) dimension del cubo, resultado (list) puntos acumulados en orden de visita.
    Retorna: list de tuplas (z, x, y) ordenadas por proximidad.
    """
    if len(frontera) == 0:
        return resultado
    siguiente_frontera = []
    for punto in frontera:
        for vecino in tablero.vecinos_ortogonales(punto, n):
            if vecino not in visitados:
                visitados.add(vecino)
                siguiente_frontera.append(vecino)
                resultado.append(vecino)
    return _propagar_recursivo(siguiente_frontera, visitados, n, resultado)


def recorrido_propagacion(cubo_o_n, origen=None):
    """
    Objetivo: generar un recorrido del cubo por propagacion recursiva (onda/flood fill) desde un origen.
    Parametros: cubo_o_n (list o int) cubo tridimensional o dimension entera n,
                origen (tuple o None) coordenada (z, x, y) de inicio. Si es None, inicia en el centro.
    Retorna: list de tuplas (z, x, y) visitadas en orden de distancia al origen.
    Lanza: PuntoInvalidoError si el origen provisto esta fuera del cubo, ErrorCubo si la
    dimension no es valida.
    """
    n = tablero.obtener_tamano(cubo_o_n)
    if origen is None:
        origen = ((n + 1) // 2, (n + 1) // 2, (n + 1) // 2)
    else:
        tablero.validar_punto(origen, n)
    visitados = set()
    visitados.add(origen)
    resultado = [origen]
    return _propagar_recursivo([origen], visitados, n, resultado)


# Diccionario de despacho para la seleccion de recorridos
RECORRIDOS_CUBO = {
    NOMBRE_RECORRIDO_CAPAS: tablero.recorrido_capas_z,
    NOMBRE_RECORRIDO_OCTANTES: recorrido_octantes,
    NOMBRE_RECORRIDO_ESPIRAL: recorrido_espiral,
    NOMBRE_RECORRIDO_PROPAGACION: recorrido_propagacion,
    NOMBRE_RECORRIDO_CAPAS_X: tablero.recorrido_capas_x,
    NOMBRE_RECORRIDO_CAPAS_Y: tablero.recorrido_capas_y,
}


def obtener_recorrido(nombre, cubo_o_n, *args):
    """
    Objetivo: obtener la lista de puntos de un recorrido usando el despacho por diccionario.
    Parametros: nombre (str) identificador del recorrido ("capas", "octantes", "espiral", "propagacion",
                "capas_x", "capas_y"),
                cubo_o_n (list o int) cubo tridimensional o dimension entera n,
                *args argumentos adicionales para el recorrido (como coordenada de origen).
    Retorna: list de tuplas (z, x, y) segun el recorrido seleccionado.
    Lanza: RecorridoInvalidoError si el nombre no existe en el diccionario de recorridos,
    PuntoInvalidoError si el origen esta fuera del cubo, ErrorCubo si la dimension
    no es valida.
    """
    if nombre not in RECORRIDOS_CUBO:
        raise RecorridoInvalidoError("Recorrido desconocido: " + str(nombre))
    funcion_recorrido = RECORRIDOS_CUBO[nombre]
    return funcion_recorrido(cubo_o_n, *args)


def listar_nombres_recorridos():
    """
    Objetivo: obtener los identificadores de todos los recorridos disponibles en el catalogo.
    Parametros: ninguno.
    Retorna: list de str con los nombres de recorridos validos.
    """
    return list(RECORRIDOS_CUBO.keys())
