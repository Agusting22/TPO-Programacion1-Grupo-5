import random

import tablero

LETRA_FRAGATA = "F"
LETRA_DESTRUCTOR = "D"
LETRA_SUBMARINO = "S"
LETRA_CRUCERO = "C"
LETRA_PORTAAVIONES = "P"
LETRA_ESTACION = "E"
LADO_ESTACION = 2

ESTADO_SANA = "sana"
ESTADO_AVERIADA = "averiada"
ESTADO_HUNDIDA = "hundida"

CELDAS_REQUERIDAS_POR_DEFECTO = 1
CELDAS_REQUERIDAS_POR_IMPACTO = {LETRA_PORTAAVIONES: 2}
EJES = (0, 1, 2)
ULTIMO_EJE = 2
DESPLAZAMIENTOS = (-1, 0, 1)
MAX_INTENTOS_POR_NAVE = 200
MAX_REINICIOS_FLOTA = 100


class NaveInvalidaError(tablero.ErrorCubo):
    pass


class UbicacionInvalidaError(tablero.ErrorCubo):
    pass


class UbicacionAutomaticaError(tablero.ErrorCubo):
    pass


def es_mitad_inferior(z, n):
    return z >= 1 and z <= n // 2


def es_mitad_superior(z, n):
    return z > n - n // 2 and z <= n


def regla_sin_restriccion(puntos, n):
    return True


def regla_mitad_inferior(puntos, n):
    for i in range(0, len(puntos)):
        if not es_mitad_inferior(puntos[i][0], n):
            return False
    return True


def regla_mitad_superior(puntos, n):
    for i in range(0, len(puntos)):
        if not es_mitad_superior(puntos[i][0], n):
            return False
    return True


def regla_no_ocupar_extremos_z(puntos, n):
    for i in range(0, len(puntos)):
        if puntos[i][0] == 1 or puntos[i][0] == n:
            return False
    return True


def regla_sin_caras_exteriores(puntos, n):
    for i in range(0, len(puntos)):
        for eje in EJES:
            if puntos[i][eje] < 2 or puntos[i][eje] > n - 1:
                return False
    return True


CATALOGO_NAVES = {
    "F": {"nombre": "Fragata", "celdas": 2, "cantidad": 3, "regla": regla_sin_restriccion},
    "D": {"nombre": "Destructor", "celdas": 3, "cantidad": 2, "regla": regla_sin_restriccion},
    "S": {"nombre": "Submarino", "celdas": 3, "cantidad": 2, "regla": regla_mitad_inferior},
    "C": {"nombre": "Crucero", "celdas": 4, "cantidad": 1, "regla": regla_no_ocupar_extremos_z},
    "P": {"nombre": "Portaaviones", "celdas": 5, "cantidad": 1, "regla": regla_mitad_superior},
    "E": {"nombre": "Estacion orbital", "celdas": 8, "cantidad": 1, "regla": regla_sin_caras_exteriores},
}


def crear_flota():
    return {}


def contar_naves_tipo(flota, letra):
    cantidad = 0
    for id_nave in flota:
        if flota[id_nave]["tipo"] == letra:
            cantidad = cantidad + 1
    return cantidad


def obtener_pendientes(flota, catalogo):
    pendientes = {}
    for letra in catalogo:
        pendientes[letra] = catalogo[letra]["cantidad"] - contar_naves_tipo(flota, letra)
    return pendientes


def obtener_letras_por_punto(flota):
    letras = {}
    for id_nave in flota:
        for punto in flota[id_nave]["puntos"]:
            letras[punto] = flota[id_nave]["tipo"]
    return letras


def calcular_diferencia(a, b):
    if a > b:
        return a - b
    return b - a


def ordenar_extremos(a, b):
    if a <= b:
        return (a, b)
    return (b, a)


def calcular_puntos_nave(letra, desde, hasta, catalogo):
    if letra not in catalogo:
        raise NaveInvalidaError("Nave inexistente: " + letra)
    puntos = []
    if letra == LETRA_ESTACION:
        for eje in EJES:
            if calcular_diferencia(desde[eje], hasta[eje]) != LADO_ESTACION - 1:
                raise UbicacionInvalidaError("La estacion debe ser un bloque 2x2x2")
        z_inicio, z_fin = ordenar_extremos(desde[0], hasta[0])
        x_inicio, x_fin = ordenar_extremos(desde[1], hasta[1])
        y_inicio, y_fin = ordenar_extremos(desde[2], hasta[2])
        for z in range(z_inicio, z_fin + 1):
            for x in range(x_inicio, x_fin + 1):
                for y in range(y_inicio, y_fin + 1):
                    puntos.append((z, x, y))
        return puntos
    ejes_distintos = []
    for eje in EJES:
        if desde[eje] != hasta[eje]:
            ejes_distintos.append(eje)
    if len(ejes_distintos) != 1:
        raise UbicacionInvalidaError("La nave debe ser una recta sobre un solo eje")
    eje = ejes_distintos[0]
    if calcular_diferencia(desde[eje], hasta[eje]) + 1 != catalogo[letra]["celdas"]:
        raise UbicacionInvalidaError("Longitud incorrecta para esa nave")
    inicio, fin = ordenar_extremos(desde[eje], hasta[eje])
    for valor in range(inicio, fin + 1):
        punto = list(desde)
        punto[eje] = valor
        puntos.append(tuple(punto))
    return puntos


def hay_nave_cerca(cubo, punto):
    n = len(cubo)
    for dz in DESPLAZAMIENTOS:
        for dx in DESPLAZAMIENTOS:
            for dy in DESPLAZAMIENTOS:
                vecino = (punto[0] + dz, punto[1] + dx, punto[2] + dy)
                if tablero.es_punto_valido(vecino, n):
                    if tablero.leer_celda(cubo, vecino) != tablero.AGUA_SIN_EXPLORAR:
                        return True
    return False


def puede_ubicar_nave(cubo, letra, puntos, catalogo):
    n = len(cubo)
    if len(puntos) == 0:
        return False
    for punto in puntos:
        if not tablero.es_punto_valido(punto, n):
            return False
    regla = catalogo[letra]["regla"]
    if not regla(puntos, n):
        return False
    for punto in puntos:
        if hay_nave_cerca(cubo, punto):
            return False
    return True


def agregar_nave_a_flota(cubo, flota, letra, puntos):
    id_nave = f"{letra}{contar_naves_tipo(flota, letra) + 1}"
    flota[id_nave] = {"tipo": letra, "puntos": set(puntos), "impactos": {}, "hundida": False}
    for punto in puntos:
        tablero.escribir_celda(cubo, punto, tablero.NAVE_OCULTA)
    return (cubo, flota)


def ubicar_nave(cubo, flota, nave, punto_desde, punto_hasta):
    n = len(cubo)
    tablero.validar_punto(punto_desde, n)
    tablero.validar_punto(punto_hasta, n)
    puntos = calcular_puntos_nave(nave, punto_desde, punto_hasta, CATALOGO_NAVES)
    if contar_naves_tipo(flota, nave) >= CATALOGO_NAVES[nave]["cantidad"]:
        raise NaveInvalidaError("Ya se ubicaron todas las naves " + nave)
    if not puede_ubicar_nave(cubo, nave, puntos, CATALOGO_NAVES):
        raise UbicacionInvalidaError("No se puede ubicar ahi")
    return agregar_nave_a_flota(cubo, flota, nave, puntos)


def generar_puntos_al_azar(letra, n, catalogo):
    if letra == LETRA_ESTACION:
        z = random.randint(2, n - LADO_ESTACION)
        x = random.randint(2, n - LADO_ESTACION)
        y = random.randint(2, n - LADO_ESTACION)
        return calcular_puntos_nave(letra, (z, x, y), (z + 1, x + 1, y + 1), catalogo)
    eje = random.randint(0, ULTIMO_EJE)
    desde = [random.randint(1, n), random.randint(1, n), random.randint(1, n)]
    hasta = list(desde)
    hasta[eje] = desde[eje] + catalogo[letra]["celdas"] - 1
    if hasta[eje] > n:
        return []
    return calcular_puntos_nave(letra, tuple(desde), tuple(hasta), catalogo)


def quitar_flota_del_cubo(cubo, flota):
    for id_nave in flota:
        for punto in flota[id_nave]["puntos"]:
            tablero.escribir_celda(cubo, punto, tablero.AGUA_SIN_EXPLORAR)
    return cubo


def intentar_ubicar_flota(cubo, flota, catalogo):
    n = len(cubo)
    for letra in catalogo:
        for numero in range(0, catalogo[letra]["cantidad"]):
            ubicada = False
            intentos = 0
            while not ubicada and intentos < MAX_INTENTOS_POR_NAVE:
                puntos = generar_puntos_al_azar(letra, n, catalogo)
                if puede_ubicar_nave(cubo, letra, puntos, catalogo):
                    agregar_nave_a_flota(cubo, flota, letra, puntos)
                    ubicada = True
                intentos = intentos + 1
            if not ubicada:
                return False
    return True


def ubicacion_automatica(cubo, catalogo, semilla):
    random.seed(semilla)
    flota = crear_flota()
    completa = False
    reinicios = 0
    while not completa and reinicios < MAX_REINICIOS_FLOTA:
        flota = crear_flota()
        completa = intentar_ubicar_flota(cubo, flota, catalogo)
        if not completa:
            quitar_flota_del_cubo(cubo, flota)
            reinicios = reinicios + 1
    if not completa:
        raise UbicacionAutomaticaError("No se pudo ubicar la flota")
    return flota


def celdas_requeridas_por_impacto(tipo):
    return CELDAS_REQUERIDAS_POR_IMPACTO.get(tipo, CELDAS_REQUERIDAS_POR_DEFECTO)


def buscar_nave_en_punto(flota_jugador, punto):
    for id_nave in flota_jugador:
        if punto in flota_jugador[id_nave]["puntos"]:
            return id_nave
    return None


def contar_celdas_impactadas(nave):
    requeridos = celdas_requeridas_por_impacto(nave["tipo"])
    cantidad = 0
    for punto in nave["puntos"]:
        if nave["impactos"].get(punto, 0) >= requeridos:
            cantidad = cantidad + 1
    return cantidad


def calcular_hundida(nave):
    return contar_celdas_impactadas(nave) == len(nave["puntos"])


def registrar_impacto(flota_jugador, id_nave, punto):
    nave = flota_jugador[id_nave]
    nave["impactos"][punto] = nave["impactos"].get(punto, 0) + 1
    nave["hundida"] = calcular_hundida(nave)
    return nave


def obtener_estado_nave(nave):
    if nave["hundida"]:
        return ESTADO_HUNDIDA
    if any(cantidad > 0 for cantidad in nave["impactos"].values()):
        return ESTADO_AVERIADA
    return ESTADO_SANA


def pertenece_a_submarino(flota_jugador, punto):
    id_nave = buscar_nave_en_punto(flota_jugador, punto)
    if id_nave is None:
        return False
    return flota_jugador[id_nave]["tipo"] == LETRA_SUBMARINO


def flota_hundida_completa(flota_jugador):
    if len(flota_jugador) == 0:
        return False
    for id_nave in flota_jugador:
        if not flota_jugador[id_nave]["hundida"]:
            return False
    return True


def elegir_celda_para_revelar(flota_jugador, cubo_jugador):
    candidatos = []
    for id_nave in flota_jugador:
        for punto in flota_jugador[id_nave]["puntos"]:
            if tablero.leer_celda(cubo_jugador, punto) == tablero.NAVE_OCULTA:
                candidatos.append(punto)
    if len(candidatos) == 0:
        return None
    return random.choice(candidatos)
