TAMANO_CUBO_POR_DEFECTO = 8


class ErrorCubo(Exception):
    pass


class PuntoInvalidoError(ErrorCubo):
    pass


class MatrizInvalidaError(ErrorCubo):
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


def crear_cubo(n):
    cubo = []
    for z in range(0, n):
        capa = []
        for x in range(0, n):
            capa.append([AGUA_SIN_EXPLORAR] * n)
        cubo.append(capa)
    return cubo


def es_punto_valido(punto, n):
    if len(punto) != CANTIDAD_EJES:
        return False
    for i in range(0, CANTIDAD_EJES):
        if punto[i] < PRIMER_VALOR or punto[i] > n:
            return False
    return True


def validar_punto(punto, n):
    if not es_punto_valido(punto, n):
        raise PuntoInvalidoError("Punto invalido: " + str(punto))
    return punto


def convertir_a_indices(punto):
    return (punto[0] - 1, punto[1] - 1, punto[2] - 1)


def leer_celda(cubo, punto):
    validar_punto(punto, len(cubo))
    iz, ix, iy = convertir_a_indices(punto)
    return cubo[iz][ix][iy]


def escribir_celda(cubo, punto, estado):
    validar_punto(punto, len(cubo))
    iz, ix, iy = convertir_a_indices(punto)
    cubo[iz][ix][iy] = estado
    return cubo


def dibujar_capa(cubo, z, letras_por_punto):
    n = len(cubo)
    validar_punto((z, PRIMER_VALOR, PRIMER_VALOR), n)
    ancho = len(str(n)) + 1
    lineas = ["========= CAPA z = " + str(z) + " ========="]
    encabezado = " " * ancho
    for x in range(1, n + 1):
        encabezado = encabezado + " " + rellenar_texto("x" + str(x), ancho)
    lineas.append(encabezado.rstrip())
    for y in range(1, n + 1):
        fila = rellenar_texto("y" + str(y), ancho)
        for x in range(1, n + 1):
            simbolo = obtener_simbolo_celda(cubo, (z, x, y), letras_por_punto)
            fila = fila + " " + rellenar_texto(simbolo, ancho)
        lineas.append(fila.rstrip())
    lineas.append(
        "Referencias: " + SIMBOLOS[AGUA_SIN_EXPLORAR] + " sin explorar  "
        + SIMBOLOS[AGUA_MARCADA] + " agua  " + SIMBOLOS[IMPACTO] + " impacto  "
        + SIMBOLOS[HUNDIDO] + " hundido  " + SIMBOLOS[DETECTADO] + " detectado"
    )
    return "\n".join(lineas)


def rellenar_texto(texto, ancho):
    return texto + " " * (ancho - len(texto))


def obtener_simbolo_celda(cubo, punto, letras_por_punto):
    estado = leer_celda(cubo, punto)
    if estado == NAVE_OCULTA:
        if letras_por_punto is not None and punto in letras_por_punto:
            return letras_por_punto[punto]
        return SIMBOLOS[AGUA_SIN_EXPLORAR]
    return SIMBOLOS[estado]


def validar_matriz(matriz):
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
    filas, columnas = validar_matriz(a)
    resultado = []
    for j in range(0, columnas):
        fila = []
        for i in range(0, filas):
            fila.append(a[i][j])
        resultado.append(fila)
    return resultado
