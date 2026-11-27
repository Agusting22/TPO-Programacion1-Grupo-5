TAMANO_CUBO_POR_DEFECTO = 8
# Tamano N del cubo de las partidas nuevas: se configura unicamente aca
TAMANO_CUBO = TAMANO_CUBO_POR_DEFECTO
# Con menos de 7 la flota completa no siempre se puede ubicar; con mas de 15
# los turnos de la maquina dificil se vuelven demasiado lentos
TAMANO_CUBO_MINIMO = 7
TAMANO_CUBO_MAXIMO = 15


class ErrorCubo(Exception):
    """Excepcion base para errores relacionados con el cubo o matrices."""
    pass


class PuntoInvalidoError(ErrorCubo):
    """Se lanza cuando una coordenada (z, x, y) esta fuera de rango o mal formada."""
    pass


class MatrizInvalidaError(ErrorCubo):
    """Se lanza cuando una matriz es vacia, irregular o incompatible para operar."""
    pass


class TamanoInvalidoError(ErrorCubo):
    """Se lanza cuando el tamano configurado del cubo no permite jugar."""
    pass


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


def validar_tamano(n):
    """
    Objetivo: verificar que el tamano configurado permita jugar una partida.
    Parametros: n (int) dimension de cada eje del cubo.
    Retorna: int el mismo tamano si es valido.
    Lanza: TamanoInvalidoError si no es un entero entre el minimo y el maximo.
    """
    if not isinstance(n, int) or n < TAMANO_CUBO_MINIMO or n > TAMANO_CUBO_MAXIMO:
        raise TamanoInvalidoError(
            "Tamano de cubo invalido: " + str(n) + ". Debe ser un numero entre "
            + str(TAMANO_CUBO_MINIMO) + " y " + str(TAMANO_CUBO_MAXIMO) + "."
        )
    return n


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
    Lanza: PuntoInvalidoError si el punto esta fuera del cubo.
    """
    validar_punto(punto, len(cubo))
    iz, ix, iy = convertir_a_indices(punto)
    return cubo[iz][ix][iy]


def escribir_celda(cubo, punto, estado):
    """
    Objetivo: modificar el estado de una celda especifica del cubo.
    Parametros: cubo (list) matriz 3D del tablero, punto (tuple) coordenadas (z, x, y), estado (int) nuevo valor.
    Retorna: list el cubo actualizado.
    Lanza: PuntoInvalidoError si el punto esta fuera del cubo.
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
    Lanza: PuntoInvalidoError si el punto esta fuera del cubo.
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
    Lanza: PuntoInvalidoError si obtener_punto devuelve un punto fuera del cubo.
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
    Lanza: PuntoInvalidoError si z esta fuera del cubo.
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
    Lanza: PuntoInvalidoError si x esta fuera del cubo.
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
    Lanza: PuntoInvalidoError si y esta fuera del cubo.
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
    Lanza: MatrizInvalidaError si la matriz es vacia o irregular.
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
    Lanza: ErrorCubo si la dimension no es valida.
    """
    n = obtener_tamano(cubo_o_n)
    puntos = []
    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                puntos.append((z, x, y))
    return puntos


def recorrido_capas_x(cubo_o_n):
    """
    Objetivo: generar el recorrido del cubo capa por capa de x.
    Parametros: cubo_o_n (list o int) cubo tridimensional o dimension entera n.
    Retorna: list de tuplas (z, x, y) con las celdas ordenadas de x1 a xn.
    Lanza: ErrorCubo si la dimension no es valida.
    """
    n = obtener_tamano(cubo_o_n)
    puntos = []
    for x in range(1, n + 1):
        for z in range(1, n + 1):
            for y in range(1, n + 1):
                puntos.append((z, x, y))
    return puntos


def recorrido_capas_y(cubo_o_n):
    """
    Objetivo: generar el recorrido del cubo capa por capa de y.
    Parametros: cubo_o_n (list o int) cubo tridimensional o dimension entera n.
    Retorna: list de tuplas (z, x, y) con las celdas ordenadas de y1 a yn.
    Lanza: ErrorCubo si la dimension no es valida.
    """
    n = obtener_tamano(cubo_o_n)
    puntos = []
    for y in range(1, n + 1):
        for z in range(1, n + 1):
            for x in range(1, n + 1):
                puntos.append((z, x, y))
    return puntos
