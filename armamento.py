import tablero
import flota

LETRA_TORPEDO = "T"
LETRA_RACIMO = "R"
LETRA_CARGA_PROFUNDIDAD = "C"
LETRA_SONAR = "S"
LETRA_LASER = "L"
LETRA_ONDA_EXPANSIVA = "O"
LETRA_TORPEDO_GUIADO = "G"

RADIO_ONDA_EXPANSIVA = 2


class ArmaInvalidaError(tablero.ErrorCubo):
    """Se lanza cuando el arma o su eje no sirven para el disparo."""
    pass


class MunicionAgotadaError(tablero.ErrorCubo):
    """Se lanza cuando no queda municion del arma elegida."""
    pass


def obtener_celdas_torpedo(punto, n, eje):
    """
    Objetivo: calcular las celdas afectadas por el torpedo.
    Parametros: punto apuntado, n tamano del cubo, eje (no se usa).
    Retorna: lista con la unica celda apuntada.
    Lanza: PuntoInvalidoError si el punto esta fuera del cubo.
    """
    tablero.validar_punto(punto, n)
    return [punto]


def obtener_celdas_racimo(punto, n, eje):
    """
    Objetivo: calcular las celdas del misil de racimo.
    Parametros: punto apuntado, n tamano del cubo, eje (no se usa).
    Retorna: la celda apuntada mas sus vecinas ortogonales.
    Lanza: PuntoInvalidoError si el punto esta fuera del cubo.
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
    Lanza: PuntoInvalidoError si el punto esta fuera del cubo.
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
    Lanza: ArmaInvalidaError si el eje no es "x" ni "y", PuntoInvalidoError si el
    punto esta fuera del cubo.
    """
    tablero.validar_punto(punto, n)
    if eje not in CONSTRUCTORES_LASER:
        raise ArmaInvalidaError("El barrido laser va sobre el eje x o el eje y")
    constructor = CONSTRUCTORES_LASER[eje]
    celdas = []
    for valor in range(1, n + 1):
        celdas.append(constructor(punto, valor))
    return celdas


# ---------------------------------------------------------------------------
# Armas avanzadas con efectos y busqueda recursiva (Entrega 3)
# ---------------------------------------------------------------------------

def propagar_onda_recursiva(punto, radio, n, visitados):
    """
    Objetivo: propagar la onda expansiva en forma recursiva con radio decreciente.
    Parametros: punto actual (z, x, y), radio restante (int >= 0), tamano n del cubo,
    diccionario visitados (punto -> radio alcanzado).
    Retorna: diccionario visitados actualizado.
    """
    if radio < 0 or not tablero.es_punto_valido(punto, n):
        return visitados
    if punto in visitados and visitados[punto] >= radio:
        return visitados
    visitados[punto] = radio
    if radio == 0:
        return visitados
    for vecino in tablero.vecinos_ortogonales(punto, n):
        propagar_onda_recursiva(vecino, radio - 1, n, visitados)
    return visitados


def obtener_celdas_onda_expansiva(punto, n, eje, radio=RADIO_ONDA_EXPANSIVA):
    """
    Objetivo: calcular las celdas afectadas por la onda expansiva mediante propagacion
    recursiva con radio decreciente.
    Parametros: punto apuntado (z, x, y), tamano n del cubo, eje (no se usa), radio inicial.
    Retorna: lista de celdas alcanzadas.
    Lanza: PuntoInvalidoError si el punto esta fuera del cubo.
    """
    tablero.validar_punto(punto, n)
    visitados = {}
    propagar_onda_recursiva(punto, radio, n, visitados)
    return list(visitados.keys())


def buscar_celda_contigua_nave_recursiva(celda_actual, celda_inicio, puntos_nave, impactos, requeridos, visitados, n):
    """
    Objetivo: buscar en forma recursiva una celda contigua de la nave que aun no este
    completamente impactada.
    Parametros: celda actual (z, x, y), celda donde se inicio la busqueda, conjunto puntos_nave,
    diccionario impactos, impactos requeridos por celda, conjunto visitados, tamano n del cubo.
    Retorna: celda encontrada (z, x, y) o None.
    """
    visitados.add(celda_actual)
    if celda_actual != celda_inicio and celda_actual in puntos_nave and impactos.get(celda_actual, 0) < requeridos:
        return celda_actual
    for vecino in tablero.vecinos_ortogonales(celda_actual, n):
        if vecino in puntos_nave and vecino not in visitados:
            encontrada = buscar_celda_contigua_nave_recursiva(
                vecino, celda_inicio, puntos_nave, impactos, requeridos, visitados, n
            )
            if encontrada is not None:
                return encontrada
    return None


def buscar_objetivo_torpedo_guiado(flota_rival, n, punto_apuntado=None):
    """
    Objetivo: buscar un objetivo para el torpedo guiado. Si hay un impacto previo sobre
    una nave no hundida, busca en forma recursiva una celda contigua de esa nave.
    Parametros: flota_rival (diccionario), tamano n del cubo, punto_apuntado opcional.
    Retorna: celda (z, x, y) guiada o None si no hay naves averiadas no hundidas.
    """
    orden_naves = []
    if punto_apuntado is not None:
        id_prioritaria = flota.buscar_nave_en_punto(flota_rival, punto_apuntado)
        if id_prioritaria is not None:
            orden_naves.append(id_prioritaria)
    for id_nave in sorted(flota_rival.keys()):
        if id_nave not in orden_naves:
            orden_naves.append(id_nave)

    for id_nave in orden_naves:
        nave = flota_rival[id_nave]
        if nave["hundida"]:
            continue
        requeridos = flota.celdas_requeridas_por_impacto(nave["tipo"])
        celdas_con_impacto = [
            p for p in nave["puntos"] if nave["impactos"].get(p, 0) > 0
        ]
        if not celdas_con_impacto:
            continue
        for celda_inicio in celdas_con_impacto:
            visitados = set()
            encontrada = buscar_celda_contigua_nave_recursiva(
                celda_inicio, celda_inicio, nave["puntos"], nave["impactos"], requeridos, visitados, n
            )
            if encontrada is not None:
                return encontrada
        for celda_inicio in celdas_con_impacto:
            if nave["impactos"].get(celda_inicio, 0) < requeridos:
                return celda_inicio
    return None


def obtener_celdas_torpedo_guiado(punto, n, eje, flota_rival=None, cubo_rival=None):
    """
    Objetivo: calcular las celdas afectadas por el torpedo guiado.
    Si hay un impacto previo sobre una nave no hundida, busca en forma recursiva una
    celda contigua de esa nave. Si no, afecta la celda apuntada.
    Parametros: punto apuntado (z, x, y), tamano n del cubo, eje (no se usa),
    flota_rival (opcional), cubo_rival (opcional).
    Retorna: lista con la celda objetivo.
    Lanza: PuntoInvalidoError si el punto esta fuera del cubo.
    """
    if punto is not None:
        tablero.validar_punto(punto, n)
    if flota_rival is not None:
        celda_guiada = buscar_objetivo_torpedo_guiado(flota_rival, n, punto)
        if celda_guiada is not None:
            return [celda_guiada]
    if punto is not None:
        return [punto]
    return []


# Sonar no tiene funcion de celdas aca porque no hace dano: se resuelve en
# radar.aplicar_sonar, que revela un plano entero a partir de un eje y un valor.
CATALOGO_ARMAS = {
    LETRA_TORPEDO: {"nombre": "Torpedo", "municion_inicial": None, "celdas": obtener_celdas_torpedo},
    LETRA_RACIMO: {"nombre": "Misil de racimo", "municion_inicial": 3, "celdas": obtener_celdas_racimo},
    LETRA_CARGA_PROFUNDIDAD: {"nombre": "Carga de profundidad", "municion_inicial": 2, "celdas": obtener_celdas_carga_profundidad},
    LETRA_SONAR: {"nombre": "Sonar", "municion_inicial": 4, "celdas": None},
    LETRA_LASER: {"nombre": "Barrido laser", "municion_inicial": 2, "celdas": obtener_celdas_laser},
    LETRA_ONDA_EXPANSIVA: {"nombre": "Onda expansiva", "municion_inicial": 1, "celdas": obtener_celdas_onda_expansiva},
    LETRA_TORPEDO_GUIADO: {"nombre": "Torpedo guiado", "municion_inicial": 1, "celdas": obtener_celdas_torpedo_guiado},
}

CALCULADORES_CELDAS = {
    LETRA_TORPEDO: lambda punto, n, eje, flota_rival, cubo_rival: obtener_celdas_torpedo(punto, n, eje),
    LETRA_RACIMO: lambda punto, n, eje, flota_rival, cubo_rival: obtener_celdas_racimo(punto, n, eje),
    LETRA_CARGA_PROFUNDIDAD: lambda punto, n, eje, flota_rival, cubo_rival: obtener_celdas_carga_profundidad(punto, n, eje),
    LETRA_LASER: lambda punto, n, eje, flota_rival, cubo_rival: obtener_celdas_laser(punto, n, eje),
    LETRA_ONDA_EXPANSIVA: lambda punto, n, eje, flota_rival, cubo_rival: obtener_celdas_onda_expansiva(punto, n, eje),
    LETRA_TORPEDO_GUIADO: lambda punto, n, eje, flota_rival, cubo_rival: obtener_celdas_torpedo_guiado(punto, n, eje, flota_rival, cubo_rival),
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
    """
    Objetivo: verificar si queda municion de un arma.
    Parametros: municion del jugador, letra del arma.
    Retorna: True si el arma se puede usar (None es municion ilimitada).
    """
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
    Lanza: ArmaInvalidaError si el arma no aplica dano directo (por ej. Sonar) o el
    eje del laser no sirve, PuntoInvalidoError si el punto esta fuera del cubo.
    """
    if letra_arma not in catalogo or catalogo[letra_arma]["celdas"] is None:
        raise ArmaInvalidaError("Arma invalida para disparo directo: " + str(letra_arma))
    n = len(cubo_rival)
    despachador = CALCULADORES_CELDAS.get(
        letra_arma,
        lambda pt, dim, ax, fl, cb: catalogo[letra_arma]["celdas"](pt, dim, ax)
    )
    celdas = despachador(punto, n, eje, flota_rival, cubo_rival)
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
        requeridos = flota.celdas_requeridas_por_impacto(nave["tipo"])
        if tablero.leer_celda(cubo_rival, celda) in (tablero.IMPACTO, tablero.HUNDIDO) or nave["impactos"].get(celda, 0) >= requeridos:
            continue
        hundida_antes = nave["hundida"]
        flota.registrar_impacto(flota_rival, id_nave, celda)
        resultado["celdas_impactadas"].append((celda, id_nave, nave["tipo"]))
        if nave["impactos"][celda] >= requeridos:
            if nave["hundida"]:
                tablero.escribir_celda(cubo_rival, celda, tablero.HUNDIDO)
            else:
                tablero.escribir_celda(cubo_rival, celda, tablero.IMPACTO)
        if nave["hundida"] and not hundida_antes:
            resultado["naves_hundidas"].append(id_nave)
            for punto_nave in nave["puntos"]:
                tablero.escribir_celda(cubo_rival, punto_nave, tablero.HUNDIDO)
    return resultado
