import random
import re

import armamento
import flota
import radar
import registro
import tablero

PATRON_OPCION_MENU = r"^[1-5]$"
PATRON_OPCION_UBICACION = r"^[12]$"
PATRON_OPCION_TURNO = r"^[1-5]$"
PATRON_OPCION_VISTA = r"^[1-6]$"
PATRON_OPCION_PAUSA = r"^[1-4]$"
PATRON_PUNTO = r"^\d{1,2},\d{1,2},\d{1,2}$"
PATRON_TRAMO = r"^\d{1,2},\d{1,2},\d{1,2}-\d{1,2},\d{1,2},\d{1,2}$"
PATRON_LETRA_NAVE = r"^[FDSCPE]$"
PATRON_LETRA_ARMA = r"^[TRCSLOG]$"
PATRON_EJE_LASER = r"^[XY]$"
PATRON_EJE_SONAR = r"^[ZXY]$"
PATRON_NUMERO = r"^\d{1,2}$"
PATRON_CONFIRMACION = r"^[SN]$"
PATRON_NOMBRE_PARTIDA = r"^[\w\-]{1,30}$"
PATRON_OPCION_DIFICULTAD = r"^[12]$"

DIFICULTAD_FACIL = "facil"
DIFICULTAD_DIFICIL = "dificil"

OPCIONES_DIFICULTAD = {
    "1": DIFICULTAD_FACIL,
    "2": DIFICULTAD_DIFICIL,
}

OPCION_SALIR = "5"
OPCION_TURNO_DISPARAR = "1"
OPCION_TURNO_VER_CUBO = "2"
OPCION_TURNO_RADAR = "3"
OPCION_TURNO_GUARDAR = "4"
OPCION_TURNO_SALIR = "5"
OPCION_VISTA_CAPAS = "1"
OPCION_VISTA_CORTE_X = "2"
OPCION_VISTA_CORTE_Y = "3"
OPCION_VISTA_OCTANTES = "4"
OPCION_VISTA_ESPIRAL = "5"
OPCION_VISTA_PROPAGACION = "6"
OPCION_PAUSA_CONTINUAR = "1"
OPCION_PAUSA_UN_TURNO = "2"
OPCION_PAUSA_GUARDAR = "3"
OPCION_PAUSA_SALIR = "4"

SEMILLA_MAXIMA = 1000000
MAX_INTENTOS_MAQUINA = 500
MAX_TURNOS_MAQUINA_VS_MAQUINA = 1100
TURNOS_ENTRE_PAUSAS = 50
NOMBRE_JUGADOR_1 = "Jugador 1"
NOMBRE_JUGADOR_2 = "Jugador 2"
NOMBRE_MAQUINA = "Maquina"
NOMBRE_MAQUINA_2 = "Maquina 2"
NOMBRE_PARTIDA_SIN_GUARDAR = "sin_nombre"
MENSAJE_NO_UBICADA = "No se puede ubicar ahi. Intente de nuevo."
MENSAJE_INVALIDO = "Dato invalido. Intente de nuevo."
MENSAJE_ENTRADA_FINALIZADA = "Entrada finalizada. Saliendo del juego."
MENSAJE_INTERRUMPIDO = "Programa interrumpido. Saliendo del juego."
MENSAJE_RANKING_DANADO = (
    "No se pudo leer el ranking: el archivo ranking.json esta danado. "
    "Se conserva sin cambios y este resultado no se registro."
)

TEXTO_MENU_PRINCIPAL = "\n".join([
    "===== OPERACION CUBO =====",
    "1 - Partida uno contra uno",
    "2 - Partida uno contra la maquina",
    "3 - Partida maquina contra maquina",
    "4 - Continuar una partida guardada",
    "5 - Salir",
])
TEXTO_MENU_DIFICULTAD = "\n".join([
    "Dificultad de la maquina:",
    "1 - Facil (disparos aleatorios)",
    "2 - Dificil (estratega: caza naves averiadas y mapa de probabilidad)",
])
TEXTO_MENU_UBICACION = "\n".join(["1 - Ubicacion manual", "2 - Ubicacion automatica"])
TEXTO_MENU_TURNO = "\n".join([
    "1 - Disparar",
    "2 - Ver el cubo",
    "3 - Reporte de radar (metricas)",
    "4 - Guardar y salir",
    "5 - Salir de la partida",
])
TEXTO_MENU_VISTA_CUBO = "\n".join([
    "1 - Capas en el eje z",
    "2 - Corte fijando x",
    "3 - Corte fijando y",
    "4 - Recorrido por octantes",
    "5 - Recorrido en espiral",
    "6 - Recorrido por propagacion (desde el centro)",
])
TEXTO_MENU_PAUSA = "\n".join([
    "1 - Continuar (proxima pausa en " + str(TURNOS_ENTRE_PAUSAS) + " turnos)",
    "2 - Avanzar un solo turno",
    "3 - Guardar y salir",
    "4 - Salir de la partida",
])


class ObjetivoYaDisparadoError(tablero.ErrorCubo):
    """Se lanza cuando se apunta a una celda que ya fue disparada."""
    pass


def validar_opcion(texto, patron):
    """
    Objetivo: verificar que un texto cumpla con una expresion regular.
    Parametros: texto (str) dato tipeado, patron (str) expresion regular.
    Retorna: bool True si el texto cumple el patron, False en caso contrario.
    """
    return re.match(patron, texto) is not None


def parsear_punto(texto, n):
    """
    Objetivo: convertir un texto "z,x,y" en un punto del cubo.
    Parametros: texto (str) dato tipeado, n (int) tamano del cubo.
    Retorna: tuple punto (z, x, y).
    Lanza: PuntoInvalidoError si el formato es invalido o el punto esta fuera del cubo.
    """
    texto = texto.strip()
    if not validar_opcion(texto, PATRON_PUNTO):
        raise tablero.PuntoInvalidoError("Formato de punto invalido: " + texto)
    partes = texto.split(",")
    punto = (int(partes[0]), int(partes[1]), int(partes[2]))
    return tablero.validar_punto(punto, n)


def parsear_tramo(texto, n):
    """
    Objetivo: convertir un texto "z,x,y-z,x,y" en los dos extremos de un tramo.
    Parametros: texto (str) dato tipeado, n (int) tamano del cubo.
    Retorna: tuple (punto desde, punto hasta).
    Lanza: PuntoInvalidoError si el formato es invalido o algun punto esta fuera del cubo.
    """
    texto = texto.strip()
    if not validar_opcion(texto, PATRON_TRAMO):
        raise tablero.PuntoInvalidoError("Formato de tramo invalido: " + texto)
    partes = texto.split("-")
    return (parsear_punto(partes[0], n), parsear_punto(partes[1], n))


def formatear_punto(punto):
    """
    Objetivo: representar un punto del cubo como texto.
    Parametros: punto (tuple) coordenada (z, x, y).
    Retorna: str con el formato "z,x,y".
    """
    return str(punto[0]) + "," + str(punto[1]) + "," + str(punto[2])


def formatear_pendientes(pendientes):
    """
    Objetivo: armar el texto con las naves que faltan ubicar.
    Parametros: pendientes (dict) letra de nave -> cantidad pendiente.
    Retorna: str con las naves pendientes.
    """
    partes = []
    for letra in pendientes:
        if pendientes[letra] > 0:
            partes.append(letra + " x" + str(pendientes[letra]))
    return "Pendientes:  " + "  ".join(partes)


def contar_pendientes_totales(pendientes):
    """
    Objetivo: sumar la cantidad total de naves que faltan ubicar.
    Parametros: pendientes (dict) letra de nave -> cantidad pendiente.
    Retorna: int cantidad total pendiente.
    """
    total = 0
    for letra in pendientes:
        total = total + pendientes[letra]
    return total


def dibujar_cubo_completo(cubo, flota_jugador):
    """
    Objetivo: dibujar todas las capas en z del cubo mostrando las naves propias.
    Parametros: cubo (list) tablero 3D, flota_jugador (dict) naves del jugador.
    Retorna: str con todas las capas.
    """
    letras = flota.obtener_letras_por_punto(flota_jugador)
    capas = []
    for z in range(1, len(cubo) + 1):
        capas.append(tablero.dibujar_capa(cubo, z, letras))
    return "\n\n".join(capas)


def pedir_opcion(mensaje, patron):
    """
    Objetivo: pedir un dato por teclado hasta que cumpla con el patron.
    Parametros: mensaje (str) texto a mostrar, patron (str) expresion regular.
    Retorna: str dato validado en mayusculas.
    Lanza: EOFError si se termina la entrada de datos.
    """
    texto = input(mensaje).strip()
    while not validar_opcion(texto.upper(), patron):
        print(MENSAJE_INVALIDO)
        texto = input(mensaje).strip()
    return texto.upper()


def pedir_valor_eje(n, nombre_eje):
    """
    Objetivo: pedir el valor de un eje hasta que este entre 1 y n.
    Parametros: n (int) tamano del cubo, nombre_eje (str) eje a mostrar.
    Retorna: int valor del eje.
    Lanza: EOFError si se termina la entrada de datos.
    """
    texto = input("Valor de " + nombre_eje + " (1-" + str(n) + "): ").strip()
    while not validar_opcion(texto, PATRON_NUMERO) or int(texto) < 1 or int(texto) > n:
        print(MENSAJE_INVALIDO)
        texto = input("Valor de " + nombre_eje + " (1-" + str(n) + "): ").strip()
    return int(texto)


def intentar_ubicar_nave(cubo, flota_jugador, letra, texto_tramo):
    """
    Objetivo: intentar ubicar una nave a partir del tramo tipeado, informando el resultado.
    Parametros: cubo (list), flota_jugador (dict), letra (str) tipo de nave,
    texto_tramo (str) extremos de la nave.
    Retorna: bool True si la nave quedo ubicada.
    """
    ubicada = False
    try:
        desde, hasta = parsear_tramo(texto_tramo, len(cubo))
        flota.ubicar_nave(cubo, flota_jugador, letra, desde, hasta)
    except tablero.PuntoInvalidoError:
        print(MENSAJE_INVALIDO)
    except tablero.ErrorCubo:
        print(MENSAJE_NO_UBICADA)
    else:
        print("Ubicada.")
        ubicada = True
    return ubicada


def obtener_nave_sin_lugar(cubo, pendientes):
    """
    Objetivo: detectar una nave pendiente que ya no entra en ninguna posicion del cubo.
    Parametros: cubo (list) tablero 3D, pendientes (dict) letra de nave -> cantidad.
    Retorna: str letra de la nave sin lugar o None si todas pueden ubicarse.
    """
    for letra in pendientes:
        if pendientes[letra] > 0 and not flota.hay_posicion_valida(cubo, letra, flota.CATALOGO_NAVES):
            return letra
    return None


def ubicar_flota_manual(cubo, flota_jugador):
    """
    Objetivo: ubicar la flota pidiendo cada nave por teclado. Si alguna nave pendiente
    se queda sin posiciones validas, la flota se reinicia.
    Parametros: cubo (list) tablero 3D, flota_jugador (dict) flota a completar.
    Retorna: dict flota completa.
    Lanza: EOFError si se termina la entrada de datos.
    """
    pendientes = flota.obtener_pendientes(flota_jugador, flota.CATALOGO_NAVES)
    while contar_pendientes_totales(pendientes) > 0:
        letra_sin_lugar = obtener_nave_sin_lugar(cubo, pendientes)
        if letra_sin_lugar is not None and len(flota_jugador) > 0:
            print()
            print("No queda ninguna posicion valida para la nave " + letra_sin_lugar + ". Se reinicia la flota.")
            flota.quitar_flota_del_cubo(cubo, flota_jugador)
            flota_jugador.clear()
        else:
            print()
            print(formatear_pendientes(pendientes))
            print()
            letra = pedir_opcion("Nave (F/D/S/C/P/E): ", PATRON_LETRA_NAVE)
            texto_tramo = input("Desde-hasta: ")
            intentar_ubicar_nave(cubo, flota_jugador, letra, texto_tramo)
        pendientes = flota.obtener_pendientes(flota_jugador, flota.CATALOGO_NAVES)
    return flota_jugador


def ubicar_flota_automatica(cubo, flota_jugador):
    """
    Objetivo: ubicar la flota completa al azar.
    Parametros: cubo (list) tablero 3D vacio, flota_jugador (dict) no se usa.
    Retorna: dict flota completa.
    Lanza: UbicacionAutomaticaError si no se logra ubicar la flota.
    """
    semilla = random.randint(1, SEMILLA_MAXIMA)
    return flota.ubicacion_automatica(cubo, flota.CATALOGO_NAVES, semilla)


ACCIONES_UBICACION = {
    "1": ubicar_flota_manual,
    "2": ubicar_flota_automatica,
}


def ubicar_flota_jugador(nombre_jugador, n):
    """
    Objetivo: crear el cubo de un jugador y ubicar su flota segun el metodo elegido.
    Parametros: nombre_jugador (str), n (int) tamano del cubo.
    Retorna: tuple (cubo, flota).
    Lanza: EOFError si se termina la entrada de datos.
    """
    cubo = tablero.crear_cubo(n)
    flota_jugador = flota.crear_flota()
    print()
    print("--- Flota de " + nombre_jugador + " ---")
    print(TEXTO_MENU_UBICACION)
    opcion = pedir_opcion("Opcion: ", PATRON_OPCION_UBICACION)
    flota_jugador = ACCIONES_UBICACION[opcion](cubo, flota_jugador)
    return (cubo, flota_jugador)


def mostrar_estado(cubo, flota_jugador):
    """
    Objetivo: mostrar por pantalla el cubo completo de un jugador.
    Parametros: cubo (list) tablero 3D, flota_jugador (dict) naves del jugador.
    Retorna: None.
    """
    print()
    print(dibujar_cubo_completo(cubo, flota_jugador))


# ---------------------------------------------------------------------------
# Estado de la partida y turnos
# ---------------------------------------------------------------------------

def nueva_partida_1v1(configuracion):
    """
    Objetivo: armar el estado inicial de una partida de dos jugadores.
    Parametros: configuracion con n y, para cada jugador, nombre/cubo/flota ya
    ubicados.
    Retorna: diccionario de estado de la partida.
    """
    n = configuracion["n"]
    nombre1 = configuracion["nombre_jugador_1"]
    nombre2 = configuracion["nombre_jugador_2"]
    estado = {
        "n": n,
        "jugador_1": nombre1,
        "jugador_2": nombre2,
        "cubos": {
            nombre1: configuracion["cubo_jugador_1"],
            nombre2: configuracion["cubo_jugador_2"],
        },
        "flotas": {
            nombre1: configuracion["flota_jugador_1"],
            nombre2: configuracion["flota_jugador_2"],
        },
        "municiones": {
            nombre1: armamento.crear_municion_inicial(armamento.CATALOGO_ARMAS),
            nombre2: armamento.crear_municion_inicial(armamento.CATALOGO_ARMAS),
        },
        "turno_actual": nombre1,
        "historial": registro.crear_historial(),
        "estadisticas": registro.crear_estadisticas([nombre1, nombre2]),
        "es_vs_maquina": False,
        "es_maquina_vs_maquina": False,
        "ganador": None,
    }
    return estado


def nueva_partida_vs_maquina(configuracion, dificultad):
    """
    Objetivo: armar el estado inicial de una partida contra la maquina.
    Parametros: configuracion (ver nueva_partida_1v1), dificultad.
    Retorna: diccionario de estado de la partida.
    """
    estado = nueva_partida_1v1(configuracion)
    estado["es_vs_maquina"] = True
    estado["dificultad"] = dificultad
    return estado


def nueva_partida_maquina_vs_maquina(configuracion, dificultades=None):
    """
    Objetivo: armar el estado inicial de una partida maquina contra maquina.
    Parametros: configuracion (ver nueva_partida_1v1), dificultades (opcional:
    tupla/lista de dificultades para cada maquina, diccionario por nombre, o str).
    Retorna: diccionario de estado de la partida.
    """
    estado = nueva_partida_1v1(configuracion)
    estado["es_vs_maquina"] = True
    estado["es_maquina_vs_maquina"] = True
    nombre1 = estado["jugador_1"]
    nombre2 = estado["jugador_2"]
    es_secuencia = isinstance(dificultades, list) or isinstance(dificultades, tuple)
    if es_secuencia and len(dificultades) >= 2:
        estado["dificultades"] = {nombre1: dificultades[0], nombre2: dificultades[1]}
    elif isinstance(dificultades, dict):
        estado["dificultades"] = dificultades
    elif isinstance(dificultades, str):
        estado["dificultades"] = {nombre1: dificultades, nombre2: dificultades}
    else:
        estado["dificultades"] = {nombre1: DIFICULTAD_FACIL, nombre2: DIFICULTAD_DIFICIL}
    estado["dificultad"] = estado["dificultades"].get(nombre2, DIFICULTAD_FACIL)
    return estado


def obtener_defensor(estado, atacante):
    """
    Objetivo: obtener el rival del jugador que ataca.
    Parametros: estado (dict), atacante (str) nombre del jugador.
    Retorna: str nombre del defensor.
    """
    if atacante == estado["jugador_1"]:
        return estado["jugador_2"]
    return estado["jugador_1"]


def revelar_celda_atacante(estado, atacante):
    """
    Objetivo: marcar como detectada una celda oculta del atacante.
    Parametros: estado (dict), atacante (str) nombre del jugador.
    Retorna: None.
    """
    flota_atacante = estado["flotas"][atacante]
    cubo_atacante = estado["cubos"][atacante]
    punto = flota.elegir_celda_para_revelar(flota_atacante, cubo_atacante)
    if punto is not None:
        tablero.escribir_celda(cubo_atacante, punto, tablero.DETECTADO)


def otorgar_municion_extra(estado, jugador):
    """
    Objetivo: sumar un misil de racimo a la municion de un jugador.
    Parametros: estado (dict), jugador (str) nombre del jugador.
    Retorna: None.
    """
    municion = estado["municiones"][jugador]
    municion[armamento.LETRA_RACIMO] = municion[armamento.LETRA_RACIMO] + 1


def procesar_comportamientos_especiales(estado, atacante, defensor, resultado):
    """
    Objetivo: aplicar los efectos propios de las naves alcanzadas por un disparo.
    Parametros: estado (dict), atacante (str), defensor (str), resultado (dict) del disparo.
    Retorna: None.
    """
    flota_defensor = estado["flotas"][defensor]
    for celda, id_nave, tipo in resultado["celdas_impactadas"]:
        if tipo == flota.LETRA_DESTRUCTOR:
            revelar_celda_atacante(estado, atacante)
    for id_nave in resultado["naves_hundidas"]:
        if flota_defensor[id_nave]["tipo"] == flota.LETRA_ESTACION:
            otorgar_municion_extra(estado, atacante)


def ejecutar_turno(estado, jugada):
    """
    Objetivo: aplicar la jugada del jugador en turno y actualizar la partida.
    Parametros: estado, jugada ({\"arma\", \"punto\", \"eje\", \"valor\"}).
    Retorna: estado actualizado.
    Lanza: MunicionAgotadaError, ObjetivoYaDisparadoError y las excepciones
    propias de armamento/flota/tablero si la jugada no es valida.
    """
    atacante = estado["turno_actual"]
    defensor = obtener_defensor(estado, atacante)
    letra_arma = jugada["arma"]
    municion_atacante = estado["municiones"][atacante]
    cubo_defensor = estado["cubos"][defensor]
    flota_defensor = estado["flotas"][defensor]
    if not armamento.hay_municion(municion_atacante, letra_arma):
        raise armamento.MunicionAgotadaError("Sin municion de " + letra_arma)
    if letra_arma == armamento.LETRA_SONAR:
        reveladas = radar.aplicar_sonar(cubo_defensor, jugada["eje"], jugada["valor"])
        armamento.descontar_municion(municion_atacante, letra_arma)
        jugada["resultado"] = {"tipo": "sonar", "reveladas": reveladas}
    else:
        punto = jugada["punto"]
        estado_actual = tablero.leer_celda(cubo_defensor, punto)
        if estado_actual in (tablero.AGUA_MARCADA, tablero.IMPACTO, tablero.HUNDIDO):
            raise ObjetivoYaDisparadoError("Ese punto ya fue disparado")
        armamento.descontar_municion(municion_atacante, letra_arma)
        resultado = armamento.aplicar_disparo(
            cubo_defensor, flota_defensor, letra_arma, punto, jugada.get("eje"), armamento.CATALOGO_ARMAS
        )
        jugada["resultado"] = resultado
        hubo_impacto = len(resultado["celdas_impactadas"]) > 0
        registro.registrar_disparo(estado["estadisticas"], atacante, hubo_impacto)
        for id_nave in resultado["naves_hundidas"]:
            registro.registrar_nave_hundida(estado["estadisticas"], atacante)
        procesar_comportamientos_especiales(estado, atacante, defensor, resultado)
    registro.registrar_evento(estado["historial"], atacante, jugada)
    estado["ultima_jugada"] = jugada
    if flota.flota_hundida_completa(flota_defensor):
        estado["ganador"] = atacante
    else:
        estado["turno_actual"] = defensor
    return estado


def elegir_punto_aleatorio_no_disparado(cubo, n):
    """
    Objetivo: elegir al azar una celda que todavia no fue disparada.
    Parametros: cubo (list) tablero rival, n (int) tamano del cubo.
    Retorna: tuple punto (z, x, y).
    """
    intentos = 0
    while intentos < MAX_INTENTOS_MAQUINA:
        punto = (random.randint(1, n), random.randint(1, n), random.randint(1, n))
        estado_celda = tablero.leer_celda(cubo, punto)
        if estado_celda not in (tablero.AGUA_MARCADA, tablero.IMPACTO, tablero.HUNDIDO):
            return punto
        intentos = intentos + 1
    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                punto = (z, x, y)
                if tablero.leer_celda(cubo, punto) not in (tablero.AGUA_MARCADA, tablero.IMPACTO, tablero.HUNDIDO):
                    return punto
    return (1, 1, 1)


def celdas_vecinas_no_disparadas(cubo, n, punto):
    """
    Objetivo: obtener las celdas vecinas de un punto que todavia no fueron disparadas.
    Parametros: cubo (list) tablero rival, n (int) tamano del cubo, punto (tuple).
    Retorna: list de puntos.
    """
    validos = []
    for vecino in tablero.vecinos_ortogonales(punto, n):
        estado_celda = tablero.leer_celda(cubo, vecino)
        if estado_celda not in (tablero.AGUA_MARCADA, tablero.IMPACTO, tablero.HUNDIDO):
            validos.append(vecino)
    return validos


def buscar_objetivo_caza_impacto(cubo, flota_defensor, n):
    """
    Objetivo: elegir una celda vecina a un impacto sobre una nave averiada.
    Parametros: cubo (list) tablero rival, flota_defensor (dict), n (int) tamano del cubo.
    Retorna: tuple punto elegido o None si no hay candidatos.
    """
    for id_nave, nave in flota_defensor.items():
        if flota.obtener_estado_nave(nave) == flota.ESTADO_AVERIADA:
            for punto in nave["puntos"]:
                if tablero.leer_celda(cubo, punto) == tablero.IMPACTO:
                    vecinos = celdas_vecinas_no_disparadas(cubo, n, punto)
                    if vecinos:
                        return vecinos[random.randint(0, len(vecinos) - 1)]
    return None


def obtener_largos_naves_restantes(flota_defensor):
    """
    Objetivo: obtener el largo de cada nave en linea que sigue a flote.
    Parametros: flota_defensor (dict).
    Retorna: list de largos (int).
    """
    largos = []
    for id_nave, nave in flota_defensor.items():
        if not nave.get("hundida", False) and nave["tipo"] != flota.LETRA_ESTACION:
            largos.append(flota.CATALOGO_NAVES[nave["tipo"]]["celdas"])
    if not largos:
        largos = [2]
    return largos


def elegir_punto_maxima_probabilidad(cubo, flota_defensor, n):
    """
    Objetivo: elegir la celda no disparada con mayor valor en el mapa de probabilidad.
    Parametros: cubo (list) tablero rival, flota_defensor (dict), n (int) tamano del cubo.
    Retorna: tuple punto (z, x, y).
    """
    largos = obtener_largos_naves_restantes(flota_defensor)
    mapa = radar.mapa_probabilidad(cubo, largos)
    mejor_valor = -1
    candidatos = []
    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                punto = (z, x, y)
                estado_celda = tablero.leer_celda(cubo, punto)
                if estado_celda not in (tablero.AGUA_MARCADA, tablero.IMPACTO, tablero.HUNDIDO):
                    valor = tablero.leer_celda(mapa, punto)
                    if valor > mejor_valor:
                        mejor_valor = valor
                        candidatos = [punto]
                    elif valor == mejor_valor:
                        candidatos.append(punto)
    if candidatos:
        return candidatos[random.randint(0, len(candidatos) - 1)]
    return elegir_punto_aleatorio_no_disparado(cubo, n)


def elegir_jugada_maquina_facil(estado, atacante):
    """
    Objetivo: armar la jugada de la maquina en nivel facil (disparo al azar).
    Parametros: estado (dict), atacante (str).
    Retorna: diccionario de jugada.
    """
    defensor = obtener_defensor(estado, atacante)
    n = estado["n"]
    punto = elegir_punto_aleatorio_no_disparado(estado["cubos"][defensor], n)
    return {"arma": armamento.LETRA_TORPEDO, "punto": punto, "eje": None, "valor": None}


def elegir_jugada_maquina_dificil(estado, atacante):
    """
    Objetivo: armar la jugada de la maquina en nivel dificil (estratega).
    Parametros: estado (dict), atacante (str).
    Retorna: diccionario de jugada.
    """
    defensor = obtener_defensor(estado, atacante)
    cubo_defensor = estado["cubos"][defensor]
    flota_defensor = estado["flotas"][defensor]
    municion_atacante = estado["municiones"][atacante]
    n = estado["n"]

    if armamento.hay_municion(municion_atacante, armamento.LETRA_TORPEDO_GUIADO):
        for id_nave, nave in flota_defensor.items():
            if flota.obtener_estado_nave(nave) == flota.ESTADO_AVERIADA:
                punto_no_disp = elegir_punto_aleatorio_no_disparado(cubo_defensor, n)
                return {"arma": armamento.LETRA_TORPEDO_GUIADO, "punto": punto_no_disp, "eje": None, "valor": None}

    punto_caza = buscar_objetivo_caza_impacto(cubo_defensor, flota_defensor, n)
    if punto_caza is not None:
        return {"arma": armamento.LETRA_TORPEDO, "punto": punto_caza, "eje": None, "valor": None}

    punto_prob = elegir_punto_maxima_probabilidad(cubo_defensor, flota_defensor, n)
    return {"arma": armamento.LETRA_TORPEDO, "punto": punto_prob, "eje": None, "valor": None}


ESTRATEGIAS_MAQUINA = {
    DIFICULTAD_FACIL: elegir_jugada_maquina_facil,
    "normal": elegir_jugada_maquina_facil,
    DIFICULTAD_DIFICIL: elegir_jugada_maquina_dificil,
}


def obtener_dificultad_turno(estado, atacante):
    """
    Objetivo: obtener la dificultad con la que juega la maquina en turno.
    Parametros: estado (dict), atacante (str).
    Retorna: str dificultad.
    """
    dificultades = estado.get("dificultades")
    if isinstance(dificultades, dict) and atacante in dificultades:
        return dificultades[atacante]
    return estado.get("dificultad", DIFICULTAD_FACIL)


def turno_maquina(estado):
    """
    Objetivo: jugar el turno de la maquina segun el nivel de dificultad configurado.
    Parametros: estado.
    Retorna: estado actualizado.
    Lanza: las mismas excepciones que ejecutar_turno.
    """
    atacante = estado["turno_actual"]
    dificultad = obtener_dificultad_turno(estado, atacante)
    estrategia = ESTRATEGIAS_MAQUINA.get(dificultad, elegir_jugada_maquina_facil)
    jugada = estrategia(estado, atacante)
    return ejecutar_turno(estado, jugada)


def hay_ganador(estado):
    """
    Objetivo: informar el ganador de la partida.
    Parametros: estado (dict).
    Retorna: str nombre del ganador o None.
    """
    return estado["ganador"]


def formatear_mensaje_resultado(flota_defensor, resultado):
    """
    Objetivo: armar el mensaje con el resultado de un disparo o del sonar.
    Parametros: flota_defensor (dict), resultado (dict) de la jugada.
    Retorna: str mensaje.
    """
    if resultado.get("tipo") == "sonar":
        return "Sonar activado. Se revelaron " + str(len(resultado["reveladas"])) + " celdas."
    if len(resultado["celdas_impactadas"]) == 0:
        return "Agua."
    mensajes = []
    naves_mencionadas = set()
    for celda, id_nave, tipo in resultado["celdas_impactadas"]:
        if id_nave in naves_mencionadas:
            continue
        naves_mencionadas.add(id_nave)
        nave = flota_defensor[id_nave]
        nombre_nave = flota.CATALOGO_NAVES[tipo]["nombre"]
        estado_nave = flota.obtener_estado_nave(nave)
        impactadas = flota.contar_celdas_impactadas(nave)
        total = len(nave["puntos"])
        mensajes.append(
            "Impacto. " + nombre_nave + " " + estado_nave + " (" + str(impactadas) + " de " + str(total) + ")."
        )
    return " ".join(mensajes)


def obtener_celda_alcanzada(jugada):
    """
    Objetivo: obtener la celda que realmente alcanzo una jugada, ya que el torpedo
    guiado puede desviarse del punto apuntado.
    Parametros: jugada (dict) ya ejecutada.
    Retorna: tuple punto (z, x, y) o None si la jugada no tiene punto.
    """
    if jugada["arma"] == armamento.LETRA_TORPEDO_GUIADO:
        impactadas = jugada["resultado"]["celdas_impactadas"]
        if len(impactadas) > 0:
            return impactadas[0][0]
    return jugada["punto"]


def formatear_mensaje_jugada(flota_defensor, jugada):
    """
    Objetivo: armar el mensaje de una jugada, indicando la celda alcanzada por el
    torpedo guiado.
    Parametros: flota_defensor (dict), jugada (dict) ya ejecutada.
    Retorna: str mensaje.
    """
    mensaje = formatear_mensaje_resultado(flota_defensor, jugada["resultado"])
    es_guiado = jugada["arma"] == armamento.LETRA_TORPEDO_GUIADO
    if es_guiado and len(jugada["resultado"]["celdas_impactadas"]) > 0:
        celda = obtener_celda_alcanzada(jugada)
        mensaje = "Torpedo guiado sobre la celda " + formatear_punto(celda) + ". " + mensaje
    return mensaje


# ---------------------------------------------------------------------------
# Submenus de turno
# ---------------------------------------------------------------------------

def pedir_objetivo_punto(n):
    """
    Objetivo: pedir el objetivo de un arma que apunta a una celda.
    Parametros: n (int) tamano del cubo.
    Retorna: diccionario con punto, eje y valor.
    Lanza: PuntoInvalidoError si el punto tipeado es invalido.
    """
    texto = input("Objetivo: ")
    punto = parsear_punto(texto, n)
    return {"punto": punto, "eje": None, "valor": None}


def pedir_objetivo_laser(n):
    """
    Objetivo: pedir el objetivo y el eje del barrido laser.
    Parametros: n (int) tamano del cubo.
    Retorna: diccionario con punto, eje y valor.
    Lanza: PuntoInvalidoError si el punto tipeado es invalido.
    """
    texto = input("Objetivo: ")
    punto = parsear_punto(texto, n)
    eje = pedir_opcion("Eje (x/y): ", PATRON_EJE_LASER).lower()
    return {"punto": punto, "eje": eje, "valor": None}


def pedir_objetivo_sonar(n):
    """
    Objetivo: pedir el eje y el valor del plano a revelar con el sonar.
    Parametros: n (int) tamano del cubo.
    Retorna: diccionario con punto, eje y valor.
    Lanza: EOFError si se termina la entrada de datos.
    """
    eje = pedir_opcion("Eje (z/x/y): ", PATRON_EJE_SONAR).lower()
    valor = pedir_valor_eje(n, eje)
    return {"punto": None, "eje": eje, "valor": valor}


PEDIDOS_OBJETIVO = {
    armamento.LETRA_TORPEDO: pedir_objetivo_punto,
    armamento.LETRA_RACIMO: pedir_objetivo_punto,
    armamento.LETRA_CARGA_PROFUNDIDAD: pedir_objetivo_punto,
    armamento.LETRA_LASER: pedir_objetivo_laser,
    armamento.LETRA_SONAR: pedir_objetivo_sonar,
    armamento.LETRA_ONDA_EXPANSIVA: pedir_objetivo_punto,
    armamento.LETRA_TORPEDO_GUIADO: pedir_objetivo_punto,
}


def realizar_disparo(estado, jugador_actual):
    """
    Objetivo: pedir el arma y el objetivo, ejecutar el disparo e informar el resultado.
    Parametros: estado (dict), jugador_actual (str).
    Retorna: None.
    Lanza: EOFError si se termina la entrada de datos.
    """
    n = estado["n"]
    defensor = obtener_defensor(estado, jugador_actual)
    letra_arma = pedir_opcion("Arma (T/R/C/S/L/O/G): ", PATRON_LETRA_ARMA)
    try:
        datos = PEDIDOS_OBJETIVO[letra_arma](n)
        jugada = {"arma": letra_arma, "punto": datos["punto"], "eje": datos["eje"], "valor": datos["valor"]}
        ejecutar_turno(estado, jugada)
    except armamento.MunicionAgotadaError:
        print("Sin municion de esa arma.")
    except ObjetivoYaDisparadoError:
        print("Ese punto ya fue disparado.")
    except tablero.PuntoInvalidoError:
        print(MENSAJE_INVALIDO)
    except tablero.ErrorCubo as error:
        print("No se pudo disparar: " + str(error))
    else:
        print(formatear_mensaje_jugada(estado["flotas"][defensor], jugada))
    finally:
        print()


def vista_capas_z(cubo, letras, n, valor):
    """
    Objetivo: dibujar todas las capas en z del cubo.
    Parametros: cubo (list), letras (dict) naves visibles, n (int), valor (no se usa).
    Retorna: str con la vista.
    """
    capas = []
    for z in range(1, n + 1):
        capas.append(tablero.dibujar_capa(cubo, z, letras))
    return "\n\n".join(capas)


def formatear_recorrido(cubo, puntos, letras_por_punto, titulo):
    """
    Objetivo: representar en texto una lista de puntos en orden de recorrido,
    mostrando el simbolo de cada celda.
    Parametros: cubo (list) tablero 3D, puntos (list) secuencia de tuplas (z, x, y),
                letras_por_punto (dict o None) mapa de letras de naves propias,
                titulo (str) encabezado de la vista.
    Retorna: str con el recorrido formateado.
    """
    lineas = ["========= " + titulo + " ========="]
    for punto in puntos:
        simbolo = tablero.obtener_simbolo_celda(cubo, punto, letras_por_punto)
        lineas.append(
            "(" + str(punto[0]) + "," + str(punto[1]) + "," + str(punto[2]) + ") " + simbolo
        )
    return "\n".join(lineas)


def vista_corte_x(cubo, letras, n, valor):
    """
    Objetivo: dibujar el corte del cubo fijando x.
    Parametros: cubo (list), letras (dict) naves visibles, n (int), valor (int) de x.
    Retorna: str con la vista.
    """
    return tablero.dibujar_corte_x(cubo, valor, letras)


def vista_corte_y(cubo, letras, n, valor):
    """
    Objetivo: dibujar el corte del cubo fijando y.
    Parametros: cubo (list), letras (dict) naves visibles, n (int), valor (int) de y.
    Retorna: str con la vista.
    """
    return tablero.dibujar_corte_y(cubo, valor, letras)


def vista_octantes(cubo, letras, n, valor):
    """
    Objetivo: mostrar el cubo con el recorrido por octantes.
    Parametros: cubo (list), letras (dict) naves visibles, n (int), valor (no se usa).
    Retorna: str con la vista.
    """
    puntos = tablero.recorrido_octantes(n)
    return formatear_recorrido(cubo, puntos, letras, "Recorrido por octantes")


def vista_espiral(cubo, letras, n, valor):
    """
    Objetivo: mostrar el cubo con el recorrido en espiral.
    Parametros: cubo (list), letras (dict) naves visibles, n (int), valor (no se usa).
    Retorna: str con la vista.
    """
    puntos = tablero.recorrido_espiral(n)
    return formatear_recorrido(cubo, puntos, letras, "Recorrido en espiral")


def vista_propagacion(cubo, letras, n, valor):
    """
    Objetivo: mostrar el cubo con el recorrido por propagacion.
    Parametros: cubo (list), letras (dict) naves visibles, n (int),
    valor (tuple o None) punto de origen, None es el centro.
    Retorna: str con la vista.
    Lanza: PuntoInvalidoError si el origen esta fuera del cubo.
    """
    puntos = tablero.recorrido_propagacion(n, valor)
    return formatear_recorrido(cubo, puntos, letras, "Recorrido por propagacion")


ACCIONES_VISTA_CUBO = {
    OPCION_VISTA_CAPAS: vista_capas_z,
    OPCION_VISTA_CORTE_X: vista_corte_x,
    OPCION_VISTA_CORTE_Y: vista_corte_y,
    OPCION_VISTA_OCTANTES: vista_octantes,
    OPCION_VISTA_ESPIRAL: vista_espiral,
    OPCION_VISTA_PROPAGACION: vista_propagacion,
}


def pedir_valor_corte_x(n):
    """
    Objetivo: pedir el valor de x para el corte.
    Parametros: n (int) tamano del cubo.
    Retorna: int valor de x.
    Lanza: EOFError si se termina la entrada de datos.
    """
    return pedir_valor_eje(n, tablero.EJE_X)


def pedir_valor_corte_y(n):
    """
    Objetivo: pedir el valor de y para el corte.
    Parametros: n (int) tamano del cubo.
    Retorna: int valor de y.
    Lanza: EOFError si se termina la entrada de datos.
    """
    return pedir_valor_eje(n, tablero.EJE_Y)


def pedir_origen_propagacion(n):
    """
    Objetivo: pedir el punto de origen del recorrido por propagacion.
    Parametros: n (int) tamano del cubo.
    Retorna: tuple punto elegido o None para usar el centro.
    Lanza: EOFError si se termina la entrada de datos.
    """
    print("Punto de origen para la propagacion (Enter = centro del cubo):")
    texto = input("Origen (z,x,y): ").strip()
    origen = None
    if texto != "":
        try:
            origen = parsear_punto(texto, n)
        except tablero.PuntoInvalidoError:
            print(MENSAJE_INVALIDO + " Usando el centro del cubo.")
    return origen


def pedir_sin_valor(n):
    """
    Objetivo: resolver las vistas que no necesitan datos adicionales.
    Parametros: n (int) tamano del cubo (no se usa).
    Retorna: None.
    """
    return None


PEDIDOS_VALOR_VISTA = {
    OPCION_VISTA_CAPAS: pedir_sin_valor,
    OPCION_VISTA_CORTE_X: pedir_valor_corte_x,
    OPCION_VISTA_CORTE_Y: pedir_valor_corte_y,
    OPCION_VISTA_OCTANTES: pedir_sin_valor,
    OPCION_VISTA_ESPIRAL: pedir_sin_valor,
    OPCION_VISTA_PROPAGACION: pedir_origen_propagacion,
}


def mostrar_cubo_propio_y_rival(estado, jugador_actual):
    """
    Objetivo: mostrar el cubo propio y el rival con la vista elegida.
    Parametros: estado (dict), jugador_actual (str).
    Retorna: None.
    Lanza: EOFError si se termina la entrada de datos.
    """
    rival = obtener_defensor(estado, jugador_actual)
    n = estado["n"]
    print()
    print("--- Ver el cubo ---")
    print(TEXTO_MENU_VISTA_CUBO)
    opcion = pedir_opcion("Opcion: ", PATRON_OPCION_VISTA)
    valor = PEDIDOS_VALOR_VISTA[opcion](n)
    letras_propio = flota.obtener_letras_por_punto(estado["flotas"][jugador_actual])
    letras_rival = {}
    print()
    print("=== Tu cubo (" + jugador_actual + ") ===")
    print(ACCIONES_VISTA_CUBO[opcion](estado["cubos"][jugador_actual], letras_propio, n, valor))
    print()
    print("=== Cubo rival (" + rival + ") ===")
    print(ACCIONES_VISTA_CUBO[opcion](estado["cubos"][rival], letras_rival, n, valor))


def accion_disparar(estado, jugador_actual):
    """
    Objetivo: resolver la opcion de disparar del menu de turno.
    Parametros: estado (dict), jugador_actual (str).
    Retorna: True para continuar la partida.
    """
    realizar_disparo(estado, jugador_actual)
    return True


def accion_ver_cubo(estado, jugador_actual):
    """
    Objetivo: resolver la opcion de ver el cubo del menu de turno.
    Parametros: estado (dict), jugador_actual (str).
    Retorna: True para continuar la partida.
    """
    mostrar_cubo_propio_y_rival(estado, jugador_actual)
    return True


def formatear_metricas_radar(nombre_busqueda, metricas, total_encontrados):
    """
    Objetivo: armar el texto con las metricas de un metodo de busqueda.
    Parametros: nombre_busqueda (str), metricas (dict), total_encontrados (int).
    Retorna: str con las metricas.
    """
    lineas = [
        "[" + nombre_busqueda + "]",
        "- Celdas encontradas: " + str(total_encontrados),
        "- Comparaciones: " + str(metricas["comparaciones"]),
        "- Tiempo: " + f"{metricas['tiempo_ms']:.4f} ms",
        "- Profundidad max: " + str(metricas["profundidad_max"]),
    ]
    return "\n".join(lineas)


def mostrar_reporte_radar(estado, jugador_actual):
    """
    Objetivo: mostrar las metricas de los tres metodos de busqueda sobre el cubo propio.
    Parametros: estado (dict), jugador_actual (str).
    Retorna: None.
    """
    cubo = estado["cubos"][jugador_actual]
    flota_jugador = estado["flotas"][jugador_actual]
    puntos_lin, met_lin = radar.buscar_naves_lineal(cubo)
    puntos_opt, met_opt = radar.buscar_naves_optimizada(cubo, flota_jugador)
    puntos_rec, met_rec = radar.buscar_naves_recursiva(cubo)
    print()
    print("=== Reporte de Radar (" + jugador_actual + ") ===")
    print(formatear_metricas_radar("Busqueda lineal", met_lin, len(puntos_lin)))
    print()
    print(formatear_metricas_radar("Busqueda optimizada", met_opt, len(puntos_opt)))
    print()
    print(formatear_metricas_radar("Busqueda recursiva", met_rec, len(puntos_rec)))
    if len(puntos_opt) > 0:
        puntos_str = ", ".join(formatear_punto(p) for p in puntos_opt)
        print()
        print("Celdas activas: " + puntos_str)


def accion_radar(estado, jugador_actual):
    """
    Objetivo: resolver la opcion de reporte de radar del menu de turno.
    Parametros: estado (dict), jugador_actual (str).
    Retorna: True para continuar la partida.
    """
    mostrar_reporte_radar(estado, jugador_actual)
    return True


def pedir_nombre_partida():
    """
    Objetivo: pedir al usuario un nombre valido para la partida a guardar/cargar.
    Parametros: ninguno.
    Retorna: nombre de partida validado (str).
    Lanza: EOFError si se termina la entrada de datos.
    """
    texto = input("Nombre de la partida: ").strip()
    while not validar_opcion(texto, PATRON_NOMBRE_PARTIDA):
        print("Nombre invalido. Use solo letras, numeros, guiones (1-30 caracteres).")
        texto = input("Nombre de la partida: ").strip()
    return texto


def guardar_partida_actual(estado):
    """
    Objetivo: pedir nombre al usuario y guardar el estado actual de la partida.
    Parametros: estado.
    Retorna: bool True si la partida se guardo, False si hubo un error.
    Lanza: EOFError si se termina la entrada de datos.
    """
    nombre = pedir_nombre_partida()
    guardada = False
    try:
        registro.guardar_partida(estado, nombre)
    except OSError as error:
        print("Error al guardar: " + str(error))
    else:
        estado["nombre_partida"] = nombre
        guardada = True
        print("Partida guardada como '" + nombre + "'.")
    return guardada


def accion_guardar_partida(estado, jugador_actual):
    """
    Objetivo: resolver la opcion de guardar y salir del menu de turno.
    Parametros: estado (dict), jugador_actual (str).
    Retorna: False para salir si se guardo, True para continuar si hubo un error.
    """
    return not guardar_partida_actual(estado)


def accion_salir_partida(estado, jugador_actual):
    """
    Objetivo: resolver la opcion de salir de la partida sin guardar.
    Parametros: estado (dict), jugador_actual (str).
    Retorna: False para terminar el bucle de turnos.
    """
    return False


ACCIONES_TURNO = {
    OPCION_TURNO_DISPARAR: accion_disparar,
    OPCION_TURNO_VER_CUBO: accion_ver_cubo,
    OPCION_TURNO_RADAR: accion_radar,
    OPCION_TURNO_GUARDAR: accion_guardar_partida,
    OPCION_TURNO_SALIR: accion_salir_partida,
}


def ejecutar_turno_humano(estado, jugador_actual):
    """
    Objetivo: mostrar el menu de turno y ejecutar la opcion elegida.
    Parametros: estado (dict), jugador_actual (str).
    Retorna: bool True si la partida continua, False si el jugador sale.
    Lanza: EOFError si se termina la entrada de datos.
    """
    print()
    print("--- Turno de " + jugador_actual + " ---")
    print(TEXTO_MENU_TURNO)
    opcion = pedir_opcion("Opcion: ", PATRON_OPCION_TURNO)
    return ACCIONES_TURNO[opcion](estado, jugador_actual)


def ejecutar_turno_maquina(estado):
    """
    Objetivo: jugar un turno automatico y mostrar su resultado.
    Parametros: estado (dict).
    Retorna: None.
    """
    atacante = estado["turno_actual"]
    defensor = obtener_defensor(estado, atacante)
    print()
    print("Turno de " + atacante + " (automatico)...")
    turno_maquina(estado)
    jugada = estado["ultima_jugada"]
    print("Objetivo: " + formatear_punto(obtener_celda_alcanzada(jugada)))
    print(formatear_mensaje_jugada(estado["flotas"][defensor], jugada))


def pausa_continuar(estado):
    """
    Objetivo: seguir la partida automatica hasta la proxima pausa.
    Parametros: estado (dict).
    Retorna: int cantidad de turnos a jugar.
    """
    return TURNOS_ENTRE_PAUSAS


def pausa_un_turno(estado):
    """
    Objetivo: jugar un unico turno y volver a pausar.
    Parametros: estado (dict).
    Retorna: int cantidad de turnos a jugar.
    """
    return 1


def pausa_guardar_y_salir(estado):
    """
    Objetivo: guardar la partida automatica y salir.
    Parametros: estado (dict).
    Retorna: 0 para salir si se guardo, None para volver a preguntar si hubo un error.
    """
    if guardar_partida_actual(estado):
        return 0
    return None


def pausa_salir(estado):
    """
    Objetivo: salir de la partida automatica sin guardar.
    Parametros: estado (dict).
    Retorna: 0, no quedan turnos por jugar.
    """
    return 0


ACCIONES_PAUSA = {
    OPCION_PAUSA_CONTINUAR: pausa_continuar,
    OPCION_PAUSA_UN_TURNO: pausa_un_turno,
    OPCION_PAUSA_GUARDAR: pausa_guardar_y_salir,
    OPCION_PAUSA_SALIR: pausa_salir,
}


def contar_turnos_jugados(estado):
    """
    Objetivo: contar los turnos jugados en la partida.
    Parametros: estado (dict).
    Retorna: int cantidad de turnos.
    """
    return len(estado["historial"])


def pedir_pausa_maquinas(estado):
    """
    Objetivo: mostrar el menu de pausa de la partida maquina contra maquina.
    Parametros: estado (dict).
    Retorna: int cantidad de turnos a jugar antes de la proxima pausa, 0 para salir.
    Lanza: EOFError si se termina la entrada de datos.
    """
    turnos = None
    while turnos is None:
        print()
        print("--- Pausa (turnos jugados: " + str(contar_turnos_jugados(estado)) + ") ---")
        print(TEXTO_MENU_PAUSA)
        opcion = pedir_opcion("Opcion: ", PATRON_OPCION_PAUSA)
        turnos = ACCIONES_PAUSA[opcion](estado)
    return turnos


def alcanzo_limite_turnos(estado):
    """
    Objetivo: verificar si una partida automatica llego al maximo de turnos.
    Parametros: estado (dict).
    Retorna: bool True si es maquina contra maquina y alcanzo el limite.
    """
    es_mvm = estado.get("es_maquina_vs_maquina", False)
    return es_mvm and contar_turnos_jugados(estado) >= MAX_TURNOS_MAQUINA_VS_MAQUINA


def es_turno_automatico(estado):
    """
    Objetivo: verificar si el turno actual lo juega la maquina.
    Parametros: estado (dict).
    Retorna: bool True si el turno es de la maquina.
    """
    if estado.get("es_maquina_vs_maquina", False):
        return True
    return estado["es_vs_maquina"] and estado["turno_actual"] == estado["jugador_2"]


def registrar_y_mostrar_ranking(estado):
    """
    Objetivo: agregar la partida terminada al ranking y mostrarlo.
    Parametros: estado (dict) con ganador.
    Retorna: None.
    """
    try:
        registro.guardar_ranking(
            hay_ganador(estado),
            estado.get("nombre_partida", NOMBRE_PARTIDA_SIN_GUARDAR),
            contar_turnos_jugados(estado),
            estado["es_vs_maquina"],
        )
        entradas = registro.listar_ranking()
    except registro.RankingInvalidoError:
        print()
        print(MENSAJE_RANKING_DANADO)
    except OSError as error:
        print()
        print("No se pudo guardar el ranking: " + str(error))
    else:
        print()
        print(registro.formatear_ranking(entradas))


def ofrecer_exportacion(estado):
    """
    Objetivo: preguntar si se quiere exportar el reporte de la partida y hacerlo.
    Parametros: estado (dict).
    Retorna: None.
    Lanza: EOFError si se termina la entrada de datos.
    """
    print()
    respuesta = pedir_opcion("Exportar reporte de la partida (s/n): ", PATRON_CONFIRMACION)
    if respuesta != "S":
        return
    nombre = estado.get("nombre_partida")
    if nombre is None:
        nombre = pedir_nombre_partida()
    try:
        ruta = registro.exportar_reporte(estado, nombre)
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as error:
        print("No se pudo exportar el reporte: " + str(error))
    else:
        print("Reporte exportado en " + ruta)


def ejecutar_bucle_turnos(estado):
    """
    Objetivo: ejecutar el bucle principal de turnos hasta que haya ganador, se
    alcance el limite de turnos automaticos o se decida salir.
    Parametros: estado.
    Retorna: estado final.
    Lanza: EOFError si se termina la entrada de datos.
    """
    continuar = True
    es_mvm = estado.get("es_maquina_vs_maquina", False)
    turnos_hasta_pausa = 0
    while continuar and hay_ganador(estado) is None and not alcanzo_limite_turnos(estado):
        if es_mvm and turnos_hasta_pausa == 0:
            turnos_hasta_pausa = pedir_pausa_maquinas(estado)
            continuar = turnos_hasta_pausa > 0
        elif es_turno_automatico(estado):
            ejecutar_turno_maquina(estado)
            turnos_hasta_pausa = turnos_hasta_pausa - 1
        else:
            continuar = ejecutar_turno_humano(estado, estado["turno_actual"])
    ganador = hay_ganador(estado)
    if ganador is not None:
        print()
        print("Gano " + ganador + "!")
        print(registro.formatear_resumen(estado["estadisticas"]))
        registrar_y_mostrar_ranking(estado)
        ofrecer_exportacion(estado)
    elif continuar and alcanzo_limite_turnos(estado):
        print()
        print("Se alcanzo el limite de turnos. La partida termina sin ganador.")
        print(registro.formatear_resumen(estado["estadisticas"]))
        ofrecer_exportacion(estado)
    return estado


def confirmar_inicio():
    """
    Objetivo: pedir confirmacion para iniciar la partida.
    Parametros: ninguno.
    Retorna: bool True si se confirma.
    Lanza: EOFError si se termina la entrada de datos.
    """
    respuesta = pedir_opcion("Ambas flotas ubicadas. Iniciar partida (s/n): ", PATRON_CONFIRMACION)
    return respuesta == "S"


def iniciar_partida_1v1():
    """
    Objetivo: preparar y jugar una partida uno contra uno.
    Parametros: ninguno.
    Retorna: None.
    Lanza: EOFError si se termina la entrada de datos.
    """
    n = tablero.TAMANO_CUBO_POR_DEFECTO
    cubo1, flota1 = ubicar_flota_jugador(NOMBRE_JUGADOR_1, n)
    mostrar_estado(cubo1, flota1)
    cubo2, flota2 = ubicar_flota_jugador(NOMBRE_JUGADOR_2, n)
    mostrar_estado(cubo2, flota2)
    if not confirmar_inicio():
        return
    configuracion = {
        "n": n,
        "nombre_jugador_1": NOMBRE_JUGADOR_1, "cubo_jugador_1": cubo1, "flota_jugador_1": flota1,
        "nombre_jugador_2": NOMBRE_JUGADOR_2, "cubo_jugador_2": cubo2, "flota_jugador_2": flota2,
    }
    estado = nueva_partida_1v1(configuracion)
    ejecutar_bucle_turnos(estado)


def pedir_dificultad_maquina(titulo=""):
    """
    Objetivo: pedir el nivel de dificultad de una maquina.
    Parametros: titulo (str, opcional) encabezado a mostrar.
    Retorna: str dificultad elegida.
    Lanza: EOFError si se termina la entrada de datos.
    """
    print()
    if titulo:
        print(titulo)
    print(TEXTO_MENU_DIFICULTAD)
    opcion = pedir_opcion("Opcion: ", PATRON_OPCION_DIFICULTAD)
    return OPCIONES_DIFICULTAD[opcion]


def iniciar_partida_vs_maquina():
    """
    Objetivo: preparar y jugar una partida contra la maquina.
    Parametros: ninguno.
    Retorna: None.
    Lanza: EOFError si se termina la entrada de datos.
    """
    n = tablero.TAMANO_CUBO_POR_DEFECTO
    cubo1, flota1 = ubicar_flota_jugador(NOMBRE_JUGADOR_1, n)
    mostrar_estado(cubo1, flota1)
    cubo2 = tablero.crear_cubo(n)
    flota2 = ubicar_flota_automatica(cubo2, flota.crear_flota())
    print()
    print("La maquina ubico su flota.")
    dificultad = pedir_dificultad_maquina()
    if not confirmar_inicio():
        return
    configuracion = {
        "n": n,
        "nombre_jugador_1": NOMBRE_JUGADOR_1, "cubo_jugador_1": cubo1, "flota_jugador_1": flota1,
        "nombre_jugador_2": NOMBRE_MAQUINA, "cubo_jugador_2": cubo2, "flota_jugador_2": flota2,
    }
    estado = nueva_partida_vs_maquina(configuracion, dificultad)
    ejecutar_bucle_turnos(estado)


def iniciar_partida_maquina_vs_maquina():
    """
    Objetivo: iniciar y ejecutar una partida en modo maquina contra maquina.
    Ambas flotas se ubican automaticamente y todos los turnos son automaticos,
    con pausas periodicas que permiten guardar y salir.
    Parametros: ninguno.
    Retorna: None.
    Lanza: EOFError si se termina la entrada de datos.
    """
    n = tablero.TAMANO_CUBO_POR_DEFECTO
    cubo1 = tablero.crear_cubo(n)
    flota1 = ubicar_flota_automatica(cubo1, flota.crear_flota())
    cubo2 = tablero.crear_cubo(n)
    flota2 = ubicar_flota_automatica(cubo2, flota.crear_flota())
    print()
    print("Ambas maquinas ubicaron su flota.")
    dif1 = pedir_dificultad_maquina("--- Dificultad de " + NOMBRE_MAQUINA + " ---")
    dif2 = pedir_dificultad_maquina("--- Dificultad de " + NOMBRE_MAQUINA_2 + " ---")
    if not confirmar_inicio():
        return
    print("Iniciando partida automatica...")
    configuracion = {
        "n": n,
        "nombre_jugador_1": NOMBRE_MAQUINA, "cubo_jugador_1": cubo1, "flota_jugador_1": flota1,
        "nombre_jugador_2": NOMBRE_MAQUINA_2, "cubo_jugador_2": cubo2, "flota_jugador_2": flota2,
    }
    estado = nueva_partida_maquina_vs_maquina(configuracion, (dif1, dif2))
    ejecutar_bucle_turnos(estado)


def mostrar_listado_partidas():
    """
    Objetivo: mostrar las partidas guardadas disponibles.
    Parametros: ninguno.
    Retorna: lista de nombres.
    """
    try:
        nombres = registro.listar_partidas()
    except OSError as error:
        print("Error de archivo: " + str(error))
        return []
    if not nombres:
        print("No hay partidas guardadas.")
    else:
        print()
        print("Partidas guardadas:")
        for nombre in nombres:
            print("  - " + nombre)
    return nombres


def continuar_partida_guardada():
    """
    Objetivo: listar las partidas guardadas, pedir al usuario que elija una y
    continuar el bucle de turnos desde donde se guardo.
    Parametros: ninguno.
    Retorna: None.
    Lanza: EOFError si se termina la entrada de datos.
    """
    nombres = mostrar_listado_partidas()
    if not nombres:
        return
    nombre = pedir_nombre_partida()
    try:
        estado = registro.cargar_partida(nombre)
    except FileNotFoundError:
        print("No se encontro la partida '" + nombre + "'.")
    except (
        ValueError, KeyError, TypeError, AttributeError, IndexError, RecursionError, tablero.ErrorCubo
    ) as error:
        print("Error al cargar la partida: " + str(error))
    except OSError as error:
        print("Error de archivo: " + str(error))
    else:
        estado["nombre_partida"] = nombre
        print("Partida '" + nombre + "' cargada. Continuando...")
        ejecutar_bucle_turnos(estado)


def salir():
    """
    Objetivo: resolver la opcion de salir del menu principal.
    Parametros: ninguno.
    Retorna: None.
    """
    return None


ACCIONES_MENU_PRINCIPAL = {
    "1": iniciar_partida_1v1,
    "2": iniciar_partida_vs_maquina,
    "3": iniciar_partida_maquina_vs_maquina,
    "4": continuar_partida_guardada,
    "5": salir,
}


def ejecutar_menu_principal():
    """
    Objetivo: mostrar el menu principal hasta que se elija salir. Si se interrumpe
    el programa o se termina la entrada, sale con un mensaje.
    Parametros: ninguno.
    Retorna: None.
    """
    opcion = ""
    try:
        try:
            while opcion != OPCION_SALIR:
                print()
                print(TEXTO_MENU_PRINCIPAL)
                opcion = pedir_opcion("Opcion: ", PATRON_OPCION_MENU)
                try:
                    ACCIONES_MENU_PRINCIPAL[opcion]()
                except tablero.ErrorCubo as error:
                    print("No se pudo completar la accion: " + str(error))
        except EOFError:
            print()
            print(MENSAJE_ENTRADA_FINALIZADA)
    except KeyboardInterrupt:
        print()
        print(MENSAJE_INTERRUMPIDO)
