import pytest

import tablero


def test_crear_cubo_tamano():
    cubo = tablero.crear_cubo(4)
    assert len(cubo) == 4
    assert len(cubo[0]) == 4
    assert len(cubo[0][0]) == 4
    assert cubo[0][0][0] == tablero.AGUA_SIN_EXPLORAR


def test_es_punto_valido():
    assert tablero.es_punto_valido((1, 1, 1), 8)
    assert tablero.es_punto_valido((8, 8, 8), 8)
    assert not tablero.es_punto_valido((0, 1, 1), 8)
    assert not tablero.es_punto_valido((9, 1, 1), 8)


def test_validar_punto_invalido_lanza_excepcion():
    with pytest.raises(tablero.PuntoInvalidoError):
        tablero.validar_punto((9, 9, 9), 8)


def test_escribir_y_leer_celda():
    cubo = tablero.crear_cubo(8)
    tablero.escribir_celda(cubo, (3, 5, 4), tablero.IMPACTO)
    assert tablero.leer_celda(cubo, (3, 5, 4)) == tablero.IMPACTO


def test_vecinos_ortogonales_celda_interior():
    vecinos = tablero.vecinos_ortogonales((4, 4, 4), 8)
    assert len(vecinos) == 6
    assert (3, 4, 4) in vecinos
    assert (5, 4, 4) in vecinos


def test_vecinos_ortogonales_esquina():
    vecinos = tablero.vecinos_ortogonales((1, 1, 1), 8)
    assert len(vecinos) == 3


def test_dibujar_capa_tiene_encabezado_y_referencias():
    cubo = tablero.crear_cubo(4)
    texto = tablero.dibujar_capa(cubo, 1, {})
    assert "CAPA z = 1" in texto
    assert "x1" in texto
    assert "y1" in texto


def test_dibujar_corte_x_e_y():
    cubo = tablero.crear_cubo(4)
    corte_x = tablero.dibujar_corte_x(cubo, 2, {})
    corte_y = tablero.dibujar_corte_y(cubo, 2, {})
    assert "CORTE x = 2" in corte_x
    assert "CORTE y = 2" in corte_y
    assert "y1" in corte_x
    assert "x1" in corte_y


def test_sumar_matrices():
    a = [[1, 2], [3, 4]]
    b = [[1, 1], [1, 1]]
    assert tablero.sumar_matrices(a, b) == [[2, 3], [4, 5]]


def test_restar_matrices():
    a = [[5, 5], [5, 5]]
    b = [[1, 2], [3, 4]]
    assert tablero.restar_matrices(a, b) == [[4, 3], [2, 1]]


def test_multiplicar_matrices():
    a = [[1, 2], [3, 4]]
    b = [[2, 0], [1, 2]]
    assert tablero.multiplicar_matrices(a, b) == [[4, 4], [10, 8]]


def test_transponer_matriz():
    a = [[1, 2, 3], [4, 5, 6]]
    assert tablero.transponer_matriz(a) == [[1, 4], [2, 5], [3, 6]]


def test_sumar_matrices_distinto_tamano_lanza_excepcion():
    with pytest.raises(tablero.MatrizInvalidaError):
        tablero.sumar_matrices([[1, 2]], [[1, 2, 3]])
