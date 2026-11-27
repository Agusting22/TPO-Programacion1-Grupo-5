TAMANO_CUBO_POR_DEFECTO = 8


class ErrorCubo(Exception):
    """Excepcion base para errores relacionados con el cubo o matrices."""
    pass


class PuntoInvalidoError(ErrorCubo):
    """Se lanza cuando una coordenada (z, x, y) esta fuera de rango o mal formada."""
    pass


class MatrizInvalidaError(ErrorCubo):
    """Se lanza cuando una matriz es vacia, irregular o incompatible para operar."""
    pass


class RecorridoInvalidoError(ErrorCubo):
    """Se lanza cuando se solicita un recorrido del cubo no soportado o desconocido."""
    pass


# Identificadores de recorridos alternativos
NOMBRE_RECORRIDO_CAPAS = "capas"
NOMBRE_RECORRIDO_OCTANTES = "octantes"
NOMBRE_RECORRIDO_ESPIRAL = "espiral"
NOMBRE_RECORRIDO_PROPAGACION = "propagacion"


# Estados de cada celda
AGUA_SIN_EXPLORAR = 0
NAVE_OCULTA = 1
AGUA_MARCADA = 2
IMPACTO = 3
HUNDIDO = 4
DETECTADO = 5

SIMBOLOS = {
    AGUA_SIN_EXPLORAR: "~",
    AGUA_MARCADA: "o",
    IMPACTO: "X",
    HUNDIDO: "#",
    DETECTADO: "?",
}

CANTIDAD_EJES = 3
PRIMER_VALOR = 1

EJE_Z = "z"
EJE_X = "x"
EJE_Y = "y"

DESPLAZAMIENTOS_ORTOGONALES = (
    (-1, 0, 0), (1, 0, 0),
    (0, -1, 0), (0, 1, 0),
    (0, 0, -1), (0, 0, 1),
)


def crear_cubo(n):
    """
    Objetivo: crear un cubo tridimensional de tamano n x n x n inicializado en agua sin explorar.
    Parametros: n (int) dimension de cada eje del cubo.
    Retorna: lista de listas de listas representando el cubo [z][x][y].
    """
    cubo = []
    for z in range(0, n):
        capa = []
        for x in range(0, n):
            capa.append([AGUA_SIN_EXPLORAR] * n)
        cubo.append(capa)
    return cubo


def es_punto_valido(punto, n):
    """
    Objetivo: verificar si una tupla de coordenadas tiene 3 ejes dentro del rango [1, n].
    Parametros: punto (tuple) coordenadas (z, x, y), n (int) tamano del cubo.
    Retorna: bool True si el punto es valido, False en caso contrario.
    """
    if len(punto) != CANTIDAD_EJES:
        return False
    for i in range(0, CANTIDAD_EJES):
        if punto[i] < PRIMER_VALOR or punto[i] > n:
            return False
    return True


def validar_punto(punto, n):
    """
    Objetivo: validar un punto del cubo y lanzar una excepcion si es invalido.
    Parametros: punto (tuple) coordenadas (z, x, y), n (int) tamano del cubo.
    Retorna: tuple el mismo punto si es valido.
    Lanza: PuntoInvalidoError si el punto esta fuera del cubo o mal formado.
    """
    if not es_punto_valido(punto, n):
        raise PuntoInvalidoError("Punto invalido: " + str(punto))
    return punto


def convertir_a_indices(punto):
    """
    Objetivo: transformar coordenadas en base 1 (z, x, y) a indices en base 0 para listas.
    Parametros: punto (tuple) coordenadas (z, x, y) entre 1 y n.
    Retorna: tuple de indices (iz, ix, iy) entre 0 y n - 1.
    """
    return (punto[0] - 1, punto[1] - 1, punto[2] - 1)


def leer_celda(cubo, punto):
    """
    Objetivo: obtener el estado almacenado en una celda especifica del cubo.
    Parametros: cubo (list) matriz 3D del tablero, punto (tuple) coordenadas (z, x, y).
    Retorna: int constante de estado de la celda.
    """
    validar_punto(punto, len(cubo))
    iz, ix, iy = convertir_a_indices(punto)
    return cubo[iz][ix][iy]


def escribir_celda(cubo, punto, estado):
    """
    Objetivo: modificar el estado de una celda especifica del cubo.
    Parametros: cubo (list) matriz 3D del tablero, punto (tuple) coordenadas (z, x, y), estado (int) nuevo valor.
    Retorna: list el cubo actualizado.
    """
    validar_punto(punto, len(cubo))
    iz, ix, iy = convertir_a_indices(punto)
    cubo[iz][ix][iy] = estado
    return cubo


def rellenar_texto(texto, ancho):
    """
    Objetivo: completar una cadena con espacios a la derecha hasta alcanzar un ancho fijo.
    Parametros: texto (str) cadena original, ancho (int) longitud total deseada.
    Retorna: str cadena alineada a la izquierda con relleno de espacios.
    """
    return texto + " " * (ancho - len(texto))


def obtener_simbolo_celda(cubo, punto, letras_por_punto):
    """
    Objetivo: determinar el caracter visual que representa una celda segun su estado y visibilidad.
    Parametros: cubo (list) tablero 3D, punto (tuple) coordenada (z, x, y), letras_por_punto (dict o None) mapa de naves visibles.
    Retorna: str simbolo de un caracter para dibujar la celda.
    """
    estado = leer_celda(cubo, punto)
    if estado == NAVE_OCULTA:
        if letras_por_punto is not None and punto in letras_por_punto:
            return letras_por_punto[punto]
        return SIMBOLOS[AGUA_SIN_EXPLORAR]
    return SIMBOLOS[estado]


def construir_grilla_2d(cubo, titulo, prefijo_fila, prefijo_col, obtener_punto, letras_por_punto):
    """
    Objetivo: armar las lineas de texto (titulo, encabezados y filas) de una vista bidimensional del cubo.
    Parametros: cubo (list) tablero 3D, titulo (str) encabezado superior, prefijo_fila (str) etiqueta de eje vertical,
                prefijo_col (str) etiqueta de eje horizontal, obtener_punto (callable) funcion (fila, col) -> (z, x, y),
                letras_por_punto (dict o None) mapa de letras de naves propias.
    Retorna: list de cadenas con cada renglon formateado de la grilla.
    """
    n = len(cubo)
    ancho = len(str(n)) + 1
    lineas = [titulo]
    encabezado = " " * ancho
    for col in range(1, n + 1):
        encabezado = encabezado + " " + rellenar_texto(prefijo_col + str(col), ancho)
    lineas.append(encabezado.rstrip())
    for fila_idx in range(1, n + 1):
        fila = rellenar_texto(prefijo_fila + str(fila_idx), ancho)
        for col in range(1, n + 1):
            punto = obtener_punto(fila_idx, col)
            simbolo = obtener_simbolo_celda(cubo, punto, letras_por_punto)
            fila = fila + " " + rellenar_texto(simbolo, ancho)
        lineas.append(fila.rstrip())
    return lineas


def dibujar_capa(cubo, z, letras_por_punto):
    """
    Objetivo: dibujar una capa horizontal del cubo fijando la coordenada z, incluyendo referencias.
    Parametros: cubo (list) tablero 3D, z (int) numero de capa, letras_por_punto (dict o None) naves visibles.
    Retorna: str representacion en texto de la capa y sus referencias de simbolos.
    """
    n = len(cubo)
    validar_punto((z, PRIMER_VALOR, PRIMER_VALOR), n)
    titulo = "========= CAPA z = " + str(z) + " ========="
    lineas = construir_grilla_2d(
        cubo,
        titulo,
        EJE_Y,
        EJE_X,
        lambda y, x: (z, x, y),
        letras_por_punto,
    )
    lineas.append(
        "Referencias: " + SIMBOLOS[AGUA_SIN_EXPLORAR] + " sin explorar  "
        + SIMBOLOS[AGUA_MARCADA] + " agua  " + SIMBOLOS[IMPACTO] + " impacto  "
        + SIMBOLOS[HUNDIDO] + " hundido  " + SIMBOLOS[DETECTADO] + " detectado"
    )
    return "\n".join(lineas)


def dibujar_corte_x(cubo, x, letras_por_punto):
    """
    Objetivo: dibujar el corte vertical del cubo fijando el valor de x.
    Parametros: cubo (list) tablero 3D, x (int) coordenada fija en x, letras_por_punto (dict o None) naves visibles.
    Retorna: str texto con filas por z y columnas por y.
    """
    n = len(cubo)
    validar_punto((PRIMER_VALOR, x, PRIMER_VALOR), n)
    titulo = "========= CORTE x = " + str(x) + " ========="
    lineas = construir_grilla_2d(
        cubo,
        titulo,
        EJE_Z,
        EJE_Y,
        lambda z, y: (z, x, y),
        letras_por_punto,
    )
    return "\n".join(lineas)


def dibujar_corte_y(cubo, y, letras_por_punto):
    """
    Objetivo: dibujar el corte vertical del cubo fijando el valor de y.
    Parametros: cubo (list) tablero 3D, y (int) coordenada fija en y, letras_por_punto (dict o None) naves visibles.
    Retorna: str texto con filas por z y columnas por x.
    """
    n = len(cubo)
    validar_punto((PRIMER_VALOR, PRIMER_VALOR, y), n)
    titulo = "========= CORTE y = " + str(y) + " ========="
    lineas = construir_grilla_2d(
        cubo,
        titulo,
        EJE_Z,
        EJE_X,
        lambda z, x: (z, x, y),
        letras_por_punto,
    )
    return "\n".join(lineas)


def vecinos_ortogonales(punto, n):
    """
    Objetivo: dar las celdas pegadas a un punto sobre los 3 ejes (sin diagonales).
    Parametros: punto (tuple) coordenada (z, x, y), n (int) tamano del cubo.
    Retorna: list de puntos vecinos que caen dentro del cubo.
    """
    vecinos = []
    for dz, dx, dy in DESPLAZAMIENTOS_ORTOGONALES:
        vecino = (punto[0] + dz, punto[1] + dx, punto[2] + dy)
        if es_punto_valido(vecino, n):
            vecinos.append(vecino)
    return vecinos


def validar_matriz(matriz):
    """
    Objetivo: verificar que una lista de listas sea una matriz rectangular no vacia.
    Parametros: matriz (list) lista bidimensional a validar.
    Retorna: tuple (cantidad_filas, cantidad_columnas) de la matriz.
    Lanza: MatrizInvalidaError si la matriz es vacia o irregular.
    """
    if len(matriz) == 0:
        raise MatrizInvalidaError("Matriz vacia o invalida")
    columnas = len(matriz[0])
    if columnas == 0:
        raise MatrizInvalidaError("Matriz sin columnas")
    for i in range(0, len(matriz)):
        if len(matriz[i]) != columnas:
            raise MatrizInvalidaError("Filas de distinto largo")
    return (len(matriz), columnas)


def sumar_matrices(a, b):
    """
    Objetivo: sumar elemento a elemento dos matrices de iguales dimensiones.
    Parametros: a (list) primera matriz, b (list) segunda matriz.
    Retorna: list nueva matriz resultante de la suma a + b.
    Lanza: MatrizInvalidaError si las matrices son invalidas o de distinto tamano.
    """
    if validar_matriz(a) != validar_matriz(b):
        raise MatrizInvalidaError("Las matrices deben tener el mismo tamano")
    resultado = []
    for i in range(0, len(a)):
        fila = []
        for j in range(0, len(a[0])):
            fila.append(a[i][j] + b[i][j])
        resultado.append(fila)
    return resultado


def restar_matrices(a, b):
    """
    Objetivo: restar elemento a elemento dos matrices de iguales dimensiones.
    Parametros: a (list) primera matriz, b (list) segunda matriz.
    Retorna: list nueva matriz resultante de la resta a - b.
    Lanza: MatrizInvalidaError si las matrices son invalidas o de distinto tamano.
    """
    if validar_matriz(a) != validar_matriz(b):
        raise MatrizInvalidaError("Las matrices deben tener el mismo tamano")
    resultado = []
    for i in range(0, len(a)):
        fila = []
        for j in range(0, len(a[0])):
            fila.append(a[i][j] - b[i][j])
        resultado.append(fila)
    return resultado


def multiplicar_matrices(a, b):
    """
    Objetivo: calcular el producto matricial entre a y b.
    Parametros: a (list) matriz de m x k, b (list) matriz de k x n.
    Retorna: list nueva matriz resultante de m x n.
    Lanza: MatrizInvalidaError si las matrices son invalidas o incompatibles.
    """
    filas_a, columnas_a = validar_matriz(a)
    filas_b, columnas_b = validar_matriz(b)
    if columnas_a != filas_b:
        raise MatrizInvalidaError("Columnas de a distintas de filas de b")
    resultado = []
    for i in range(0, filas_a):
        fila = []
        for j in range(0, columnas_b):
            suma = 0
            for k in range(0, columnas_a):
                suma = suma + a[i][k] * b[k][j]
            fila.append(suma)
        resultado.append(fila)
    return resultado


def transponer_matriz(a):
    """
    Objetivo: obtener la matriz transpuesta intercambiando filas por columnas.
    Parametros: a (list) matriz de m x n.
    Retorna: list nueva matriz transpuesta de n x m.
    """
    filas, columnas = validar_matriz(a)
    resultado = []
    for j in range(0, columnas):
        fila = []
        for i in range(0, filas):
            fila.append(a[i][j])
        resultado.append(fila)
    return resultado


# ---------------------------------------------------------------------------
# Recorridos alternativos del cubo (Entrega 3)
# ---------------------------------------------------------------------------

def obtener_tamano(cubo_o_n):
    """
    Objetivo: obtener la dimension n a partir de una matriz de cubo o de un entero.
    Parametros: cubo_o_n (list o int) cubo tridimensional o dimension entera n.
    Retorna: int dimension n del cubo.
    Lanza: ErrorCubo si la dimension no es valida (menor a 1).
    """
    if isinstance(cubo_o_n, list):
        n = len(cubo_o_n)
    else:
        n = cubo_o_n
    if n < PRIMER_VALOR:
        raise ErrorCubo("Dimension de cubo invalida: " + str(n))
    return n


def recorrido_capas_z(cubo_o_n):
    """
    Objetivo: generar el recorrido secuencial canonico del cubo capa por capa de z.
    Parametros: cubo_o_n (list o int) cubo tridimensional o dimension entera n.
    Retorna: list de tuplas (z, x, y) con las celdas ordenadas de z1 a zn.
    """
    n = obtener_tamano(cubo_o_n)
    puntos = []
    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                puntos.append((z, x, y))
    return puntos


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
    """
    n = obtener_tamano(cubo_o_n)
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
    """
    n = obtener_tamano(cubo_o_n)
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
        for dz, dx, dy in DESPLAZAMIENTOS_ORTOGONALES:
            vecino = (punto[0] + dz, punto[1] + dx, punto[2] + dy)
            if es_punto_valido(vecino, n):
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
    Lanza: PuntoInvalidoError si el origen provisto esta fuera del cubo.
    """
    n = obtener_tamano(cubo_o_n)
    if origen is None:
        origen = ((n + 1) // 2, (n + 1) // 2, (n + 1) // 2)
    else:
        validar_punto(origen, n)
    visitados = set()
    visitados.add(origen)
    resultado = [origen]
    return _propagar_recursivo([origen], visitados, n, resultado)


# Diccionario de despacho para la seleccion de recorridos
RECORRIDOS_CUBO = {
    NOMBRE_RECORRIDO_CAPAS: recorrido_capas_z,
    NOMBRE_RECORRIDO_OCTANTES: recorrido_octantes,
    NOMBRE_RECORRIDO_ESPIRAL: recorrido_espiral,
    NOMBRE_RECORRIDO_PROPAGACION: recorrido_propagacion,
}


def obtener_recorrido(nombre, cubo_o_n, *args):
    """
    Objetivo: obtener la lista de puntos de un recorrido usando el despacho por diccionario.
    Parametros: nombre (str) identificador del recorrido ("capas", "octantes", "espiral", "propagacion"),
                cubo_o_n (list o int) cubo tridimensional o dimension entera n,
                *args argumentos adicionales para el recorrido (como coordenada de origen).
    Retorna: list de tuplas (z, x, y) segun el recorrido seleccionado.
    Lanza: RecorridoInvalidoError si el nombre no existe en el diccionario de recorridos.
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
