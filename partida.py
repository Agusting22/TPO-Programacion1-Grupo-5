import random
import re

import armamento
import flota
import radar
import registro
import tablero

PATRON_OPCION_MENU = r"^[1-3]$"
PATRON_OPCION_UBICACION = r"^[12]$"
PATRON_OPCION_TURNO = r"^[1-4]$"
PATRON_OPCION_VISTA = r"^[1-3]$"
PATRON_PUNTO = r"^\d{1,2},\d{1,2},\d{1,2}$"
PATRON_TRAMO = r"^\d{1,2},\d{1,2},\d{1,2}-\d{1,2},\d{1,2},\d{1,2}$"
PATRON_LETRA_NAVE = r"^[FDSCPE]$"
PATRON_LETRA_ARMA = r"^[TRCSL]$"
PATRON_EJE_LASER = r"^[XY]$"
PATRON_EJE_SONAR = r"^[ZXY]$"
PATRON_NUMERO = r"^\d{1,2}$"
PATRON_CONFIRMACION = r"^[SN]$"

OPCION_SALIR = "3"
OPCION_TURNO_DISPARAR = "1"
OPCION_TURNO_VER_CUBO = "2"
OPCION_TURNO_RADAR = "3"
OPCION_TURNO_SALIR = "4"
OPCION_VISTA_CORTE_X = "2"
OPCION_VISTA_CORTE_Y = "3"

SEMILLA_MAXIMA = 1000000
MAX_INTENTOS_MAQUINA = 500
NOMBRE_JUGADOR_1 = "Jugador 1"
NOMBRE_JUGADOR_2 = "Jugador 2"
NOMBRE_MAQUINA = "Maquina"
MENSAJE_NO_UBICADA = "No se puede ubicar ahi. Intente de nuevo."
MENSAJE_INVALIDO = "Dato invalido. Intente de nuevo."

TEXTO_MENU_PRINCIPAL = "\n".join([
    "===== OPERACION CUBO =====",
    "1 - Partida uno contra uno",
    "2 - Partida uno contra la maquina",
    "3 - Salir",
])
TEXTO_MENU_UBICACION = "\n".join(["1 - Ubicacion manual", "2 - Ubicacion automatica"])
TEXTO_MENU_TURNO = "\n".join([
    "1 - Disparar",
    "2 - Ver el cubo",
    "3 - Reporte de radar (metricas)",
    "4 - Salir de la partida",
])
TEXTO_MENU_VISTA_CUBO = "\n".join([
    "1 - Capas en el eje z",
    "2 - Corte fijando x",
    "3 - Corte fijando y",
])

ETIQUETAS_EJE_CORTE = {OPCION_VISTA_CORTE_X: "x", OPCION_VISTA_CORTE_Y: "y"}


class ObjetivoYaDisparadoError(tablero.ErrorCubo):
    pass


def validar_opcion(texto, patron):
    return re.match(patron, texto) is not None


def parsear_punto(texto, n):
    texto = texto.strip()
    if not validar_opcion(texto, PATRON_PUNTO):
        raise tablero.PuntoInvalidoError("Formato de punto invalido: " + texto)
    partes = texto.split(",")
    punto = (int(partes[0]), int(partes[1]), int(partes[2]))
    return tablero.validar_punto(punto, n)


def parsear_tramo(texto, n):
    texto = texto.strip()
    if not validar_opcion(texto, PATRON_TRAMO):
        raise tablero.PuntoInvalidoError("Formato de tramo invalido: " + texto)
    partes = texto.split("-")
    return (parsear_punto(partes[0], n), parsear_punto(partes[1], n))


def formatear_punto(punto):
    return str(punto[0]) + "," + str(punto[1]) + "," + str(punto[2])


def formatear_pendientes(pendientes):
    partes = []
    for letra in pendientes:
        if pendientes[letra] > 0:
            partes.append(letra + " x" + str(pendientes[letra]))
    return "Pendientes:  " + "  ".join(partes)


def contar_pendientes_totales(pendientes):
    total = 0
    for letra in pendientes:
        total = total + pendientes[letra]
    return total


def dibujar_cubo_completo(cubo, flota_jugador):
    letras = flota.obtener_letras_por_punto(flota_jugador)
    capas = []
    for z in range(1, len(cubo) + 1):
        capas.append(tablero.dibujar_capa(cubo, z, letras))
    return "\n\n".join(capas)


def pedir_opcion(mensaje, patron):
    texto = input(mensaje).strip()
    while not validar_opcion(texto.upper(), patron):
        print(MENSAJE_INVALIDO)
        texto = input(mensaje).strip()
    return texto.upper()


def pedir_valor_eje(n, nombre_eje):
    texto = input("Valor de " + nombre_eje + " (1-" + str(n) + "): ").strip()
    while not validar_opcion(texto, PATRON_NUMERO) or int(texto) < 1 or int(texto) > n:
        print(MENSAJE_INVALIDO)
        texto = input("Valor de " + nombre_eje + " (1-" + str(n) + "): ").strip()
    return int(texto)


def intentar_ubicar_nave(cubo, flota_jugador, letra, texto_tramo):
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


def ubicar_flota_manual(cubo, flota_jugador):
    pendientes = flota.obtener_pendientes(flota_jugador, flota.CATALOGO_NAVES)
    while contar_pendientes_totales(pendientes) > 0:
        print()
        print(formatear_pendientes(pendientes))
        print()
        letra = pedir_opcion("Nave (F/D/S/C/P/E): ", PATRON_LETRA_NAVE)
        texto_tramo = input("Desde-hasta: ")
        intentar_ubicar_nave(cubo, flota_jugador, letra, texto_tramo)
        pendientes = flota.obtener_pendientes(flota_jugador, flota.CATALOGO_NAVES)
    return flota_jugador


def ubicar_flota_automatica(cubo, flota_jugador):
    semilla = random.randint(1, SEMILLA_MAXIMA)
    return flota.ubicacion_automatica(cubo, flota.CATALOGO_NAVES, semilla)


ACCIONES_UBICACION = {
    "1": ubicar_flota_manual,
    "2": ubicar_flota_automatica,
}


def ubicar_flota_jugador(nombre_jugador, n):
    cubo = tablero.crear_cubo(n)
    flota_jugador = flota.crear_flota()
    print()
    print("--- Flota de " + nombre_jugador + " ---")
    print(TEXTO_MENU_UBICACION)
    opcion = pedir_opcion("Opcion: ", PATRON_OPCION_UBICACION)
    flota_jugador = ACCIONES_UBICACION[opcion](cubo, flota_jugador)
    return (cubo, flota_jugador)


def mostrar_estado(cubo, flota_jugador):
    print()
    print(dibujar_cubo_completo(cubo, flota_jugador))


# ---------------------------------------------------------------------------
# Estado de la partida y turnos (Entrega 2)
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
        "ganador": None,
    }
    return estado


def nueva_partida_vs_maquina(configuracion, dificultad):
    """
    Objetivo: armar el estado inicial de una partida contra la maquina.
    Parametros: configuracion (ver nueva_partida_1v1), dificultad (se guarda
    para usarse en una proxima entrega; por ahora la maquina siempre dispara
    al azar).
    Retorna: diccionario de estado de la partida.
    """
    estado = nueva_partida_1v1(configuracion)
    estado["es_vs_maquina"] = True
    estado["dificultad"] = dificultad
    return estado


def obtener_defensor(estado, atacante):
    if atacante == estado["jugador_1"]:
        return estado["jugador_2"]
    return estado["jugador_1"]


def revelar_celda_atacante(estado, atacante):
    flota_atacante = estado["flotas"][atacante]
    cubo_atacante = estado["cubos"][atacante]
    punto = flota.elegir_celda_para_revelar(flota_atacante, cubo_atacante)
    if punto is not None:
        tablero.escribir_celda(cubo_atacante, punto, tablero.DETECTADO)


def otorgar_municion_extra(estado, jugador):
    municion = estado["municiones"][jugador]
    municion[armamento.LETRA_RACIMO] = municion[armamento.LETRA_RACIMO] + 1


def procesar_comportamientos_especiales(estado, atacante, defensor, resultado):
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
    Parametros: estado, jugada ({"arma", "punto", "eje", "valor"}).
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
    intentos = 0
    while intentos < MAX_INTENTOS_MAQUINA:
        punto = (random.randint(1, n), random.randint(1, n), random.randint(1, n))
        estado_celda = tablero.leer_celda(cubo, punto)
        if estado_celda not in (tablero.AGUA_MARCADA, tablero.IMPACTO, tablero.HUNDIDO):
            return punto
        intentos = intentos + 1
    return (1, 1, 1)


def turno_maquina(estado):
    """
    Objetivo: jugar el turno de la maquina disparando un torpedo al azar.
    Parametros: estado.
    Retorna: estado actualizado.
    """
    atacante = estado["turno_actual"]
    defensor = obtener_defensor(estado, atacante)
    n = estado["n"]
    punto = elegir_punto_aleatorio_no_disparado(estado["cubos"][defensor], n)
    jugada = {"arma": armamento.LETRA_TORPEDO, "punto": punto, "eje": None, "valor": None}
    return ejecutar_turno(estado, jugada)


def hay_ganador(estado):
    return estado["ganador"]


def formatear_mensaje_resultado(flota_defensor, resultado):
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


# ---------------------------------------------------------------------------
# Submenus de turno
# ---------------------------------------------------------------------------

def pedir_objetivo_punto(n):
    texto = input("Objetivo: ")
    punto = parsear_punto(texto, n)
    return {"punto": punto, "eje": None, "valor": None}


def pedir_objetivo_laser(n):
    texto = input("Objetivo: ")
    punto = parsear_punto(texto, n)
    eje = pedir_opcion("Eje (x/y): ", PATRON_EJE_LASER).lower()
    return {"punto": punto, "eje": eje, "valor": None}


def pedir_objetivo_sonar(n):
    eje = pedir_opcion("Eje (z/x/y): ", PATRON_EJE_SONAR).lower()
    valor = pedir_valor_eje(n, eje)
    return {"punto": None, "eje": eje, "valor": valor}


PEDIDOS_OBJETIVO = {
    armamento.LETRA_TORPEDO: pedir_objetivo_punto,
    armamento.LETRA_RACIMO: pedir_objetivo_punto,
    armamento.LETRA_CARGA_PROFUNDIDAD: pedir_objetivo_punto,
    armamento.LETRA_LASER: pedir_objetivo_laser,
    armamento.LETRA_SONAR: pedir_objetivo_sonar,
}


def realizar_disparo(estado, jugador_actual):
    n = estado["n"]
    defensor = obtener_defensor(estado, jugador_actual)
    letra_arma = pedir_opcion("Arma (T/R/C/S/L): ", PATRON_LETRA_ARMA)
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
        print(formatear_mensaje_resultado(estado["flotas"][defensor], jugada["resultado"]))
    finally:
        print()


def vista_capas_z(cubo, letras, n, valor):
    capas = []
    for z in range(1, n + 1):
        capas.append(tablero.dibujar_capa(cubo, z, letras))
    return "\n\n".join(capas)


def vista_corte_x(cubo, letras, n, valor):
    return tablero.dibujar_corte_x(cubo, valor, letras)


def vista_corte_y(cubo, letras, n, valor):
    return tablero.dibujar_corte_y(cubo, valor, letras)


ACCIONES_VISTA_CUBO = {
    "1": vista_capas_z,
    OPCION_VISTA_CORTE_X: vista_corte_x,
    OPCION_VISTA_CORTE_Y: vista_corte_y,
}


def mostrar_cubo_propio_y_rival(estado, jugador_actual):
    rival = obtener_defensor(estado, jugador_actual)
    n = estado["n"]
    print()
    print("--- Ver el cubo ---")
    print(TEXTO_MENU_VISTA_CUBO)
    opcion = pedir_opcion("Opcion: ", PATRON_OPCION_VISTA)
    if opcion in ETIQUETAS_EJE_CORTE:
        valor = pedir_valor_eje(n, ETIQUETAS_EJE_CORTE[opcion])
    else:
        valor = None
    letras_propio = flota.obtener_letras_por_punto(estado["flotas"][jugador_actual])
    letras_rival = {}
    print()
    print("=== Tu cubo (" + jugador_actual + ") ===")
    print(ACCIONES_VISTA_CUBO[opcion](estado["cubos"][jugador_actual], letras_propio, n, valor))
    print()
    print("=== Cubo rival (" + rival + ") ===")
    print(ACCIONES_VISTA_CUBO[opcion](estado["cubos"][rival], letras_rival, n, valor))


def accion_disparar(estado, jugador_actual):
    realizar_disparo(estado, jugador_actual)
    return True


def accion_ver_cubo(estado, jugador_actual):
    mostrar_cubo_propio_y_rival(estado, jugador_actual)
    return True


def formatear_metricas_radar(nombre_busqueda, metricas, total_encontrados):
    lineas = [
        "[" + nombre_busqueda + "]",
        "- Celdas encontradas: " + str(total_encontrados),
        "- Comparaciones: " + str(metricas["comparaciones"]),
        "- Tiempo: " + f"{metricas['tiempo_ms']:.4f} ms",
        "- Profundidad max: " + str(metricas["profundidad_max"]),
    ]
    return "\n".join(lineas)


def mostrar_reporte_radar(estado, jugador_actual):
    cubo = estado["cubos"][jugador_actual]
    flota_jugador = estado["flotas"][jugador_actual]
    puntos_lin, met_lin = radar.buscar_naves_lineal(cubo)
    puntos_opt, met_opt = radar.buscar_naves_optimizada(cubo, flota_jugador)
    print()
    print("=== Reporte de Radar (" + jugador_actual + ") ===")
    print(formatear_metricas_radar("Busqueda lineal", met_lin, len(puntos_lin)))
    print()
    print(formatear_metricas_radar("Busqueda optimizada", met_opt, len(puntos_opt)))
    if len(puntos_opt) > 0:
        puntos_str = ", ".join(formatear_punto(p) for p in puntos_opt)
        print()
        print("Celdas activas: " + puntos_str)


def accion_radar(estado, jugador_actual):
    mostrar_reporte_radar(estado, jugador_actual)
    return True


def accion_salir_partida(estado, jugador_actual):
    return False


ACCIONES_TURNO = {
    OPCION_TURNO_DISPARAR: accion_disparar,
    OPCION_TURNO_VER_CUBO: accion_ver_cubo,
    OPCION_TURNO_RADAR: accion_radar,
    OPCION_TURNO_SALIR: accion_salir_partida,
}


def ejecutar_turno_humano(estado, jugador_actual):
    print()
    print("--- Turno de " + jugador_actual + " ---")
    print(TEXTO_MENU_TURNO)
    opcion = pedir_opcion("Opcion: ", PATRON_OPCION_TURNO)
    return ACCIONES_TURNO[opcion](estado, jugador_actual)


def ejecutar_turno_maquina(estado):
    atacante = estado["turno_actual"]
    defensor = obtener_defensor(estado, atacante)
    print()
    print("Turno de " + atacante + " (automatico)...")
    turno_maquina(estado)
    jugada = estado["ultima_jugada"]
    print("Objetivo: " + formatear_punto(jugada["punto"]))
    print(formatear_mensaje_resultado(estado["flotas"][defensor], jugada["resultado"]))


def ejecutar_bucle_turnos(estado):
    continuar = True
    while continuar and hay_ganador(estado) is None:
        jugador_actual = estado["turno_actual"]
        if estado["es_vs_maquina"] and jugador_actual == estado["jugador_2"]:
            ejecutar_turno_maquina(estado)
        else:
            continuar = ejecutar_turno_humano(estado, jugador_actual)
    if hay_ganador(estado) is not None:
        print()
        print("Gano " + hay_ganador(estado) + "!")
        print(registro.formatear_resumen(estado["estadisticas"]))
    return estado


def confirmar_inicio():
    respuesta = pedir_opcion("Ambas flotas ubicadas. Iniciar partida (s/n): ", PATRON_CONFIRMACION)
    return respuesta == "S"


def iniciar_partida_1v1():
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


def iniciar_partida_vs_maquina():
    n = tablero.TAMANO_CUBO_POR_DEFECTO
    cubo1, flota1 = ubicar_flota_jugador(NOMBRE_JUGADOR_1, n)
    mostrar_estado(cubo1, flota1)
    cubo2 = tablero.crear_cubo(n)
    flota2 = ubicar_flota_automatica(cubo2, flota.crear_flota())
    print()
    print("La maquina ubico su flota.")
    if not confirmar_inicio():
        return
    configuracion = {
        "n": n,
        "nombre_jugador_1": NOMBRE_JUGADOR_1, "cubo_jugador_1": cubo1, "flota_jugador_1": flota1,
        "nombre_jugador_2": NOMBRE_MAQUINA, "cubo_jugador_2": cubo2, "flota_jugador_2": flota2,
    }
    estado = nueva_partida_vs_maquina(configuracion, "normal")
    ejecutar_bucle_turnos(estado)


def salir():
    return None


ACCIONES_MENU_PRINCIPAL = {
    "1": iniciar_partida_1v1,
    "2": iniciar_partida_vs_maquina,
    "3": salir,
}


def ejecutar_menu_principal():
    opcion = ""
    try:
        while opcion != OPCION_SALIR:
            print()
            print(TEXTO_MENU_PRINCIPAL)
            opcion = pedir_opcion("Opcion: ", PATRON_OPCION_MENU)
            ACCIONES_MENU_PRINCIPAL[opcion]()
    except EOFError:
        print()
