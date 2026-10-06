import tablero


def obtener_celdas_torpedo(punto, n):
    tablero.validar_punto(punto, n)
    return [punto]


CATALOGO_ARMAS = {
    "T": {"nombre": "Torpedo", "municion_inicial": None, "celdas": obtener_celdas_torpedo},
    "R": {"nombre": "Misil de racimo", "municion_inicial": 3, "celdas": None},
    "C": {"nombre": "Carga de profundidad", "municion_inicial": 2, "celdas": None},
    "S": {"nombre": "Sonar", "municion_inicial": 4, "celdas": None},
    "L": {"nombre": "Barrido laser", "municion_inicial": 2, "celdas": None},
    "O": {"nombre": "Onda expansiva", "municion_inicial": 1, "celdas": None},
    "G": {"nombre": "Torpedo guiado", "municion_inicial": 1, "celdas": None},
}
