import tablero
import flota

LETRA_TORPEDO = "T"
LETRA_RACIMO = "R"
LETRA_CARGA_PROFUNDIDAD = "C"
LETRA_SONAR = "S"
LETRA_LASER = "L"


class ArmaInvalidaError(tablero.ErrorCubo):
    pass


class MunicionAgotadaError(tablero.ErrorCubo):
    pass


def obtener_celdas_torpedo(punto, n, eje):
    """
    Objetivo: calcular las celdas afectadas por el torpedo.
    Parametros: punto apuntado, n tamano del cubo, eje (no se usa).
    Retorna: lista con la unica celda apuntada.
    """
    tablero.validar_punto(punto, n)
    return [punto]


def obtener_celdas_racimo(punto, n, eje):
    """
    Objetivo: calcular las celdas del misil de racimo.
    Parametros: punto apuntado, n tamano del cubo, eje (no se usa).
    Retorna: la celda apuntada mas sus vecinas ortogonales.
    """
    tablero.validar_punto(punto, n)
    celdas = [punto]
    for vecino in tablero.vecinos_ortogonales(punto, n):
        celdas.append(vecino)
    return celdas


def obtener_celdas_carga_profundidad(punto, n, eje):
    """
    Objetivo: calcular las celdas de la carga de profundidad.
    Parametros: punto apuntado, n tamano del cubo, eje (no se usa).
    Retorna: toda la recta del eje z que pasa por el punto.
    """
    tablero.validar_punto(punto, n)
    celdas = []
    for z in range(1, n + 1):
        celdas.append((z, punto[1], punto[2]))
    return celdas


CONSTRUCTORES_LASER = {
    tablero.EJE_X: lambda punto, valor: (punto[0], valor, punto[2]),
    tablero.EJE_Y: lambda punto, valor: (punto[0], punto[1], valor),
}


def obtener_celdas_laser(punto, n, eje):
    """
    Objetivo: calcular las celdas del barrido laser sobre el eje x o el eje y.
    Parametros: punto apuntado, n tamano del cubo, eje ("x" o "y").
    Retorna: la recta completa sobre el eje elegido.
    Lanza: ArmaInvalidaError si el eje no es "x" ni "y".
    """
    tablero.validar_punto(punto, n)
    if eje not in CONSTRUCTORES_LASER:
        raise ArmaInvalidaError("El barrido laser va sobre el eje x o el eje y")
    constructor = CONSTRUCTORES_LASER[eje]
    celdas = []
    for valor in range(1, n + 1):
        celdas.append(constructor(punto, valor))
    return celdas


# Sonar no tiene funcion de celdas aca porque no hace dano: se resuelve en
# radar.aplicar_sonar, que revela un plano entero a partir de un eje y un valor.
CATALOGO_ARMAS = {
    LETRA_TORPEDO: {"nombre": "Torpedo", "municion_inicial": None, "celdas": obtener_celdas_torpedo},
    LETRA_RACIMO: {"nombre": "Misil de racimo", "municion_inicial": 3, "celdas": obtener_celdas_racimo},
    LETRA_CARGA_PROFUNDIDAD: {"nombre": "Carga de profundidad", "municion_inicial": 2, "celdas": obtener_celdas_carga_profundidad},
    LETRA_SONAR: {"nombre": "Sonar", "municion_inicial": 4, "celdas": None},
    LETRA_LASER: {"nombre": "Barrido laser", "municion_inicial": 2, "celdas": obtener_celdas_laser},
}


def crear_municion_inicial(catalogo):
    """
    Objetivo: armar la municion inicial de un jugador para todas las armas.
    Parametros: catalogo de armas.
    Retorna: diccionario letra de arma -> municion (None es ilimitada).
    """
    municion = {}
    for letra in catalogo:
        municion[letra] = catalogo[letra]["municion_inicial"]
    return municion


def hay_municion(municion, letra):
    cantidad = municion[letra]
    if cantidad is None:
        return True
    return cantidad > 0


def descontar_municion(municion, letra):
    """
    Objetivo: descontar una unidad de municion de un arma.
    Parametros: municion del jugador, letra del arma.
    Retorna: municion actualizada.
    Lanza: MunicionAgotadaError si no queda municion.
    """
    if not hay_municion(municion, letra):
        raise MunicionAgotadaError("Sin municion de " + letra)
    if municion[letra] is not None:
        municion[letra] = municion[letra] - 1
    return municion


def aplicar_disparo(cubo_rival, flota_rival, letra_arma, punto, eje, catalogo):
    """
    Objetivo: aplicar un disparo de un arma con dano sobre el cubo rival.
    Parametros: cubo_rival, flota_rival, letra_arma, punto apuntado, eje (para
    el laser), catalogo de armas.
    Retorna: diccionario con celdas_impactadas, celdas_agua y naves_hundidas.
    Lanza: ArmaInvalidaError si el arma no aplica dano directo (por ej. Sonar).
    """
    if letra_arma not in catalogo or catalogo[letra_arma]["celdas"] is None:
        raise ArmaInvalidaError("Arma invalida para disparo directo: " + str(letra_arma))
    n = len(cubo_rival)
    funcion_celdas = catalogo[letra_arma]["celdas"]
    celdas = funcion_celdas(punto, n, eje)
    resultado = {"celdas_impactadas": [], "celdas_agua": [], "naves_hundidas": []}
    for celda in celdas:
        if not tablero.es_punto_valido(celda, n):
            continue
        id_nave = flota.buscar_nave_en_punto(flota_rival, celda)
        if id_nave is None:
            if tablero.leer_celda(cubo_rival, celda) == tablero.AGUA_SIN_EXPLORAR:
                tablero.escribir_celda(cubo_rival, celda, tablero.AGUA_MARCADA)
                resultado["celdas_agua"].append(celda)
            continue
        nave = flota_rival[id_nave]
        if nave["tipo"] == flota.LETRA_SUBMARINO and letra_arma == LETRA_LASER:
            continue
        hundida_antes = nave["hundida"]
        flota.registrar_impacto(flota_rival, id_nave, celda)
        requeridos = flota.celdas_requeridas_por_impacto(nave["tipo"])
        if nave["impactos"][celda] >= requeridos:
            resultado["celdas_impactadas"].append((celda, id_nave, nave["tipo"]))
            if nave["hundida"]:
                tablero.escribir_celda(cubo_rival, celda, tablero.HUNDIDO)
            else:
                tablero.escribir_celda(cubo_rival, celda, tablero.IMPACTO)
        if nave["hundida"] and not hundida_antes:
            resultado["naves_hundidas"].append(id_nave)
            for punto_nave in nave["puntos"]:
                tablero.escribir_celda(cubo_rival, punto_nave, tablero.HUNDIDO)
    return resultado
