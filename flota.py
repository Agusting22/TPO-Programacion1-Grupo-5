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
    """Se lanza cuando el tipo de nave no existe o se supera su cantidad permitida."""
    pass


class UbicacionInvalidaError(tablero.ErrorCubo):
    """Se lanza cuando las coordenadas o reglas de posicionamiento de una nave son invalidas."""
    pass


class UbicacionAutomaticaError(tablero.ErrorCubo):
    """Se lanza cuando no se logra ubicar toda la flota de forma aleatoria tras varios intentos."""
    pass


def es_mitad_inferior(z, n):
    """
    Objetivo: verificar si una capa z pertenece a la mitad inferior del cubo.
    Parametros: z (int) coordenada vertical, n (int) tamano del cubo.
    Retorna: bool True si z esta en la mitad inferior, False en caso contrario.
    """
    return z >= 1 and z <= n // 2


def es_mitad_superior(z, n):
    """
    Objetivo: verificar si una capa z pertenece a la mitad superior del cubo.
    Parametros: z (int) coordenada vertical, n (int) tamano del cubo.
    Retorna: bool True si z esta en la mitad superior, False en caso contrario.
    """
    return z > n - n // 2 and z <= n


def regla_sin_restriccion(puntos, n):
    """
    Objetivo: validar una nave sin restricciones de zona dentro del cubo.
    Parametros: puntos (list) lista de coordenadas (z, x, y), n (int) tamano del cubo.
    Retorna: bool siempre True.
    """
    return True


def regla_mitad_inferior(puntos, n):
    """
    Objetivo: verificar que todos los puntos de la nave esten en la mitad inferior en z.
    Parametros: puntos (list) lista de coordenadas (z, x, y), n (int) tamano del cubo.
    Retorna: bool True si todos los puntos cumplen la regla, False en caso contrario.
    """
    for i in range(0, len(puntos)):
        if not es_mitad_inferior(puntos[i][0], n):
            return False
    return True


def regla_mitad_superior(puntos, n):
    """
    Objetivo: verificar que todos los puntos de la nave esten en la mitad superior en z.
    Parametros: puntos (list) lista de coordenadas (z, x, y), n (int) tamano del cubo.
    Retorna: bool True si todos los puntos cumplen la regla, False en caso contrario.
    """
    for i in range(0, len(puntos)):
        if not es_mitad_superior(puntos[i][0], n):
            return False
    return True


def regla_no_ocupar_extremos_z(puntos, n):
    """
    Objetivo: verificar que la nave no ocupe las capas z = 1 ni z = n.
    Parametros: puntos (list) lista de coordenadas (z, x, y), n (int) tamano del cubo.
    Retorna: bool True si ningun punto esta en los extremos de z, False en caso contrario.
    """
    for i in range(0, len(puntos)):
        if puntos[i][0] == 1 or puntos[i][0] == n:
            return False
    return True


def regla_sin_caras_exteriores(puntos, n):
    """
    Objetivo: verificar que la nave este completamente en el interior del cubo sin tocar caras externas.
    Parametros: puntos (list) lista de coordenadas (z, x, y), n (int) tamano del cubo.
    Retorna: bool True si todas las coordenadas estan entre 2 y n - 1, False en caso contrario.
    """
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
    """
    Objetivo: inicializar una estructura vacia para almacenar las naves de un jugador.
    Parametros: ninguno.
    Retorna: dict diccionario vacio de flota.
    """
    return {}


def contar_naves_tipo(flota, letra):
    """
    Objetivo: contar cuantas naves de un tipo especifico ya fueron ubicadas en la flota.
    Parametros: flota (dict) diccionario de naves del jugador, letra (str) codigo del tipo de nave.
    Retorna: int cantidad de naves ubicadas de ese tipo.
    """
    cantidad = 0
    for id_nave in flota:
        if flota[id_nave]["tipo"] == letra:
            cantidad = cantidad + 1
    return cantidad


def obtener_pendientes(flota, catalogo):
    """
    Objetivo: calcular cuantas naves faltan ubicar por cada tipo segun el catalogo.
    Parametros: flota (dict) naves ubicadas, catalogo (dict) configuracion total de naves.
    Retorna: dict mapa de letra de nave a cantidad pendiente por ubicar.
    """
    pendientes = {}
    for letra in catalogo:
        pendientes[letra] = catalogo[letra]["cantidad"] - contar_naves_tipo(flota, letra)
    return pendientes


def obtener_letras_por_punto(flota):
    """
    Objetivo: mapear cada coordenada ocupada de la flota a la letra del tipo de nave correspondiente.
    Parametros: flota (dict) diccionario de naves del jugador.
    Retorna: dict mapa de tupla (z, x, y) a str con la letra de la nave.
    """
    letras = {}
    for id_nave in flota:
        for punto in flota[id_nave]["puntos"]:
            letras[punto] = flota[id_nave]["tipo"]
    return letras


def calcular_diferencia(a, b):
    """
    Objetivo: obtener la distancia absoluta entre dos valores enteros.
    Parametros: a (int) primer valor, b (int) segundo valor.
    Retorna: int diferencia no negativa entre a y b.
    """
    if a > b:
        return a - b
    return b - a


def ordenar_extremos(a, b):
    """
    Objetivo: devolver dos enteros ordenados de menor a mayor.
    Parametros: a (int) primer extremo, b (int) segundo extremo.
    Retorna: tuple par ordenado (menor, mayor).
    """
    if a <= b:
        return (a, b)
    return (b, a)


def calcular_puntos_nave(letra, desde, hasta, catalogo):
    """
    Objetivo: generar todas las coordenadas que ocupa una nave entre dos extremos dados.
    Parametros: letra (str) tipo de nave, desde (tuple) punto inicial (z, x, y),
                hasta (tuple) punto final (z, x, y), catalogo (dict) definicion de naves.
    Retorna: list lista de tuplas (z, x, y) que conforman la nave.
    """
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
    """
    Objetivo: comprobar si existe alguna celda ocupada en el vecindario 3D (26 alrededores o centro) de un punto.
    Parametros: cubo (list) tablero 3D, punto (tuple) coordenada (z, x, y) a evaluar.
    Retorna: bool True si hay una nave en el punto o adyacente, False si esta despejado.
    """
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
    """
    Objetivo: verificar si un conjunto de puntos cumple limites, regla de zona y distancia minima.
    Parametros: cubo (list) tablero 3D, letra (str) tipo de nave, puntos (list) celdas propuestas,
                catalogo (dict) reglas y tamanos de cada nave.
    Retorna: bool True si la ubicacion es valida, False en caso contrario.
    """
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
    """
    Objetivo: registrar una nave en el diccionario de flota y marcar sus celdas en el cubo.
    Parametros: cubo (list) tablero 3D, flota (dict) flota del jugador, letra (str) tipo de nave,
                puntos (list) coordenadas ocupadas por la nave.
    Retorna: tuple par (cubo, flota) actualizados.
    """
    id_nave = f"{letra}{contar_naves_tipo(flota, letra) + 1}"
    flota[id_nave] = {"tipo": letra, "puntos": set(puntos), "impactos": {}, "hundida": False}
    for punto in puntos:
        tablero.escribir_celda(cubo, punto, tablero.NAVE_OCULTA)
    return (cubo, flota)


def ubicar_nave(cubo, flota, nave, punto_desde, punto_hasta):
    """
    Objetivo: validar y colocar manualmente una nave en el tablero y la flota del jugador.
    Parametros: cubo (list) tablero 3D, flota (dict) flota del jugador, nave (str) letra de la nave,
                punto_desde (tuple) coordenada inicial, punto_hasta (tuple) coordenada final.
    Retorna: tuple par (cubo, flota) actualizados tras ubicar la nave.
    """
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
    """
    Objetivo: generar una posicion candidata aleatoria dentro del cubo para un tipo de nave.
    Parametros: letra (str) tipo de nave, n (int) tamano del cubo, catalogo (dict) definicion de naves.
    Retorna: list lista de puntos candidatos o lista vacia si excede el borde del cubo.
    """
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
    """
    Objetivo: limpiar del cubo todas las celdas ocupadas por las naves de una flota.
    Parametros: cubo (list) tablero 3D, flota (dict) diccionario de naves a remover.
    Retorna: list el cubo con las celdas restauradas a agua sin explorar.
    """
    for id_nave in flota:
        for punto in flota[id_nave]["puntos"]:
            tablero.escribir_celda(cubo, punto, tablero.AGUA_SIN_EXPLORAR)
    return cubo


def intentar_ubicar_flota(cubo, flota, catalogo):
    """
    Objetivo: intentar colocar al azar todas las naves del catalogo respetando las reglas.
    Parametros: cubo (list) tablero 3D, flota (dict) diccionario donde se cargan las naves,
                catalogo (dict) cantidades y reglas de cada tipo de nave.
    Retorna: bool True si se ubicaron todas las naves, False si alguna agoto los intentos.
    """
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
    """
    Objetivo: generar una flota completa ubicada aleatoriamente usando una semilla reproducible.
    Parametros: cubo (list) tablero 3D vacio, catalogo (dict) configuracion de flota,
                semilla (int o None) semilla para el generador aleatorio.
    Retorna: dict flota completa ubicada en el cubo.
    """
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
    """
    Objetivo: obtener cuantos impactos necesita una misma celda para considerarse danada segun la nave.
    Parametros: tipo (str) letra identificadora del tipo de nave.
    Retorna: int cantidad de impactos requeridos por celda.
    """
    return CELDAS_REQUERIDAS_POR_IMPACTO.get(tipo, CELDAS_REQUERIDAS_POR_DEFECTO)


def buscar_nave_en_punto(flota_jugador, punto):
    """
    Objetivo: localizar el identificador de la nave que ocupa una coordenada dada.
    Parametros: flota_jugador (dict) flota donde buscar, punto (tuple) coordenada (z, x, y).
    Retorna: str identificador de la nave (ej. 'F1') o None si no hay nave en ese punto.
    """
    for id_nave in flota_jugador:
        if punto in flota_jugador[id_nave]["puntos"]:
            return id_nave
    return None


def contar_celdas_impactadas(nave):
    """
    Objetivo: contar cuantas celdas de una nave alcanzaron los impactos necesarios para quedar inutilizadas.
    Parametros: nave (dict) diccionario con los datos e impactos de una nave.
    Retorna: int cantidad de celdas completamente impactadas.
    """
    requeridos = celdas_requeridas_por_impacto(nave["tipo"])
    cantidad = 0
    for punto in nave["puntos"]:
        if nave["impactos"].get(punto, 0) >= requeridos:
            cantidad = cantidad + 1
    return cantidad


def calcular_hundida(nave):
    """
    Objetivo: determinar si todas las celdas de una nave fueron impactadas y por lo tanto esta hundida.
    Parametros: nave (dict) diccionario con los datos de la nave.
    Retorna: bool True si la nave esta hundida, False en caso contrario.
    """
    return contar_celdas_impactadas(nave) == len(nave["puntos"])


def registrar_impacto(flota_jugador, id_nave, punto):
    """
    Objetivo: sumar un impacto en un punto de una nave y actualizar su estado de hundimiento.
    Parametros: flota_jugador (dict) flota del jugador, id_nave (str) identificador de la nave,
                punto (tuple) coordenada impactada (z, x, y).
    Retorna: dict diccionario actualizado de la nave impactada.
    """
    nave = flota_jugador[id_nave]
    nave["impactos"][punto] = nave["impactos"].get(punto, 0) + 1
    nave["hundida"] = calcular_hundida(nave)
    return nave


def obtener_estado_nave(nave):
    """
    Objetivo: devolver el estado general de una nave (sana, averiada o hundida).
    Parametros: nave (dict) diccionario con los datos de la nave.
    Retorna: str constante de estado de la nave.
    """
    if nave["hundida"]:
        return ESTADO_HUNDIDA
    if any(cantidad > 0 for cantidad in nave["impactos"].values()):
        return ESTADO_AVERIADA
    return ESTADO_SANA


def pertenece_a_submarino(flota_jugador, punto):
    """
    Objetivo: comprobar si en una coordenada especifica se encuentra un submarino.
    Parametros: flota_jugador (dict) flota del jugador, punto (tuple) coordenada (z, x, y).
    Retorna: bool True si hay un submarino en ese punto, False en caso contrario.
    """
    id_nave = buscar_nave_en_punto(flota_jugador, punto)
    if id_nave is None:
        return False
    return flota_jugador[id_nave]["tipo"] == LETRA_SUBMARINO


def flota_hundida_completa(flota_jugador):
    """
    Objetivo: verificar si todas las naves de la flota de un jugador fueron hundidas.
    Parametros: flota_jugador (dict) flota del jugador a evaluar.
    Retorna: bool True si toda la flota esta hundida, False si queda alguna nave a flote.
    """
    if len(flota_jugador) == 0:
        return False
    for id_nave in flota_jugador:
        if not flota_jugador[id_nave]["hundida"]:
            return False
    return True


def elegir_celda_para_revelar(flota_jugador, cubo_jugador):
    """
    Objetivo: seleccionar al azar una celda con nave oculta que aun no fue revelada ni impactada.
    Parametros: flota_jugador (dict) flota del jugador, cubo_jugador (list) tablero 3D del jugador.
    Retorna: tuple coordenada (z, x, y) seleccionada al azar o None si no quedan celdas ocultas.
    """
    candidatos = []
    for id_nave in flota_jugador:
        for punto in flota_jugador[id_nave]["puntos"]:
            if tablero.leer_celda(cubo_jugador, punto) == tablero.NAVE_OCULTA:
                candidatos.append(punto)
    if len(candidatos) == 0:
        return None
    return random.choice(candidatos)