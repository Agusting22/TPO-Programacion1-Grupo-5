import random
import re

import flota
import tablero

PATRON_OPCION_MENU = r"^[1-5]$"
PATRON_OPCION_UBICACION = r"^[12]$"
PATRON_PUNTO = r"^\d{1,2},\d{1,2},\d{1,2}$"
PATRON_TRAMO = r"^\d{1,2},\d{1,2},\d{1,2}-\d{1,2},\d{1,2},\d{1,2}$"
PATRON_LETRA_NAVE = r"^[FDSCPE]$"

OPCION_SALIR = "5"
SEMILLA_MAXIMA = 1000000
NOMBRE_JUGADOR_1 = "Jugador 1"
MENSAJE_NO_UBICADA = "No se puede ubicar ahi. Intente de nuevo."
MENSAJE_INVALIDO = "Dato invalido. Intente de nuevo."

TEXTO_MENU_PRINCIPAL = "\n".join([
    "===== OPERACION CUBO =====",
    "1 - Partida uno contra uno",
    "2 - Partida uno contra la maquina",
    "3 - Partida maquina contra maquina",
    "4 - Continuar una partida guardada",
    "5 - Salir",
])
TEXTO_MENU_UBICACION = "\n".join(["1 - Ubicacion manual", "2 - Ubicacion automatica"])


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


def iniciar_partida_1v1():
    cubo, flota_jugador = ubicar_flota_jugador(NOMBRE_JUGADOR_1, tablero.TAMANO_CUBO_POR_DEFECTO)
    mostrar_estado(cubo, flota_jugador)


def iniciar_partida_vs_maquina():
    n = tablero.TAMANO_CUBO_POR_DEFECTO
    cubo, flota_jugador = ubicar_flota_jugador(NOMBRE_JUGADOR_1, n)
    mostrar_estado(cubo, flota_jugador)
    cubo_maquina = tablero.crear_cubo(n)
    ubicar_flota_automatica(cubo_maquina, flota.crear_flota())


def mostrar_proxima_entrega():
    print("Disponible en una proxima entrega")


def salir():
    return None


ACCIONES_MENU_PRINCIPAL = {
    "1": iniciar_partida_1v1,
    "2": iniciar_partida_vs_maquina,
    "3": mostrar_proxima_entrega,
    "4": mostrar_proxima_entrega,
    "5": salir,
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
