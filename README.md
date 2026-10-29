# Operacion Cubo - Batalla Naval 3D

TPO de Programacion I (UADE). **Estado: ENTREGA 2.**

En esta entrega ya se puede jugar una partida completa: ubicar las dos
flotas, alternar turnos, disparar con cinco armas distintas, ver el cubo
propio y el rival (por capas o por cortes), y terminar la partida cuando
se hunde toda la flota rival. **Todavia no hay guardado de partidas,
partida maquina contra maquina ni busqueda/recorridos recursivos**: eso
queda para la Entrega 3.

## Instalacion

Requiere Python 3.10 o superior.

```
pip install -r requirements.txt
```

`requirements.txt` solo contiene `pytest` (se usa unicamente para las pruebas).
Todo lo demas del proyecto usa solamente la biblioteca estandar (`re`,
`random`, `time`).

## Ejecucion

```
python main.py
```

## Pruebas

Desde la raiz del proyecto:

```
python -m pytest
```

## Menus

### Menu principal

```
===== OPERACION CUBO =====
1 - Partida uno contra uno
2 - Partida uno contra la maquina
3 - Salir
Opcion:
```

Si se tipea algo que no es una opcion valida (por ejemplo `abc` o `9`) se
avisa y se vuelve a preguntar; el programa nunca se corta por un dato mal
escrito.

### Submenu de ubicacion de flota

Antes de empezar, cada jugador ubica su flota (la de la maquina siempre se
ubica en forma automatica):

```
--- Flota de Jugador 1 ---
1 - Ubicacion manual
2 - Ubicacion automatica
Opcion: 1

Pendientes:  F x3  D x2  S x2  C x1  P x1  E x1

Nave (F/D/S/C/P/E): F
Desde-hasta: 3,5,4-3,5,5
Ubicada.
```

El tramo se escribe `z,x,y-z,x,y`. La estacion orbital (E) se escribe con
dos esquinas opuestas del bloque, por ejemplo `3,3,3-4,4,4`. Si el tramo no
se puede ubicar (sale del cubo, pisa otra nave o no respeta la separacion
minima) se avisa con `No se puede ubicar ahi. Intente de nuevo.` y se repite
hasta ubicar las 10 naves.

Ubicadas las dos flotas, el sistema pide confirmacion (`s`/`n`) para arrancar
la partida.

### Turno de juego

```
--- Turno de Jugador 1 ---
1 - Disparar
2 - Ver el cubo
3 - Reporte de radar (metricas)
4 - Salir de la partida
Opcion: 1

Arma (T/R/C/S/L): T
Objetivo: 4,2,7
Impacto. Destructor averiado (1 de 3).
```

- **Disparar**: pide el arma por su letra y, segun el arma, el objetivo:
  - Torpedo (T), Misil de racimo (R) y Carga de profundidad (C) piden un
    unico punto `z,x,y`.
  - Barrido laser (L) pide el punto y, ademas, el eje de la recta (`x` o `y`).
  - Sonar (S) no hace dano: pide el eje (`z`, `x` o `y`) y el valor fijo de
    ese eje, y revela todo ese plano.
  - Si no queda municion de esa arma, o si el punto ya habia sido disparado,
    se avisa y no se pierde el turno.
- **Ver el cubo**: deja elegir entre ver todas las capas de z, un corte
  fijando x o un corte fijando y, y muestra el cubo propio (con las naves) y
  el cubo rival (sin revelar lo que todavia no fue descubierto).
- **Reporte de radar (metricas)**: ejecuta y compara la busqueda lineal
  (`radar.buscar_naves_lineal`) con la optimizada (`radar.buscar_naves_optimizada`)
  sobre la flota propia, mostrando las celdas activas encontradas, cantidad de
  comparaciones y tiempo de ejecucion en milisegundos.
- **Salir de la partida**: corta la partida en curso y vuelve al menu
  principal.

Cuando un jugador hunde toda la flota rival se declara el ganador y se
muestra un resumen de estadisticas (disparos, aciertos, fallos y naves
hundidas de cada jugador).

## Reglas del juego

Cubo de N x N x N (por defecto N = 8). Los ejes z, x, y van de 1 a N.

### Flota

| Nave | Letra | Celdas | Cantidad | Restriccion | Comportamiento propio |
|------|-------|--------|----------|-------------|------------------------|
| Fragata | F | 2 | 3 | ninguna | - |
| Destructor | D | 3 | 2 | ninguna | al ser impactado revela una celda de la flota rival (del atacante) |
| Submarino | S | 3 | 2 | solo mitad inferior de z | no es alcanzado por el barrido laser |
| Crucero | C | 4 | 1 | no puede ocupar z = 1 ni z = N | - |
| Portaaviones | P | 5 | 1 | solo mitad superior de z | cada celda necesita dos impactos para contar como impactada |
| Estacion orbital | E | bloque 2x2x2 | 1 | no toca ninguna cara exterior | al hundirse otorga una municion extra de Misil de racimo |

Cada nave es una recta contigua sobre un eje (la estacion es un bloque).
Ninguna sale del cubo y entre dos naves queda al menos una celda libre en las
26 direcciones (incluye diagonales).

### Arsenal

| Arma | Letra | Municion | Celdas que afecta |
|------|-------|----------|--------------------|
| Torpedo | T | ilimitada | la celda apuntada |
| Misil de racimo | R | 3 | la celda apuntada y sus 6 vecinas ortogonales |
| Carga de profundidad | C | 2 | toda la recta del eje z que pasa por el punto |
| Sonar | S | 4 | no hace dano: revela un plano completo (eje + valor) |
| Barrido laser | L | 2 | una recta completa sobre el eje x o el eje y, a eleccion |

La seleccion de que funcion aplica cada arma (y tambien la de que
recorrido/corte del cubo mostrar, y la de que accion del menu ejecutar) se
resuelve siempre con un diccionario que asocia la letra u opcion con su
funcion; en ningun lado se usa una cadena de if/elif para elegir entre
varias opciones.

## Busqueda de naves

- **Busqueda lineal** (`radar.buscar_naves_lineal`): recorre las N^3 celdas
  del cubo con tres ciclos `for` anidados.
- **Busqueda optimizada** (`radar.buscar_naves_optimizada`): en vez de
  recorrer todo el cubo, usa el indice de celdas que ya mantiene la flota
  (cada nave sabe que puntos ocupa) y solo consulta esas celdas puntuales.
  Con una flota de 20 celdas ocupadas sobre un cubo de 8x8x8 (512 celdas)
  hace muchas menos comparaciones que la busqueda lineal.

Ambas devuelven una tupla `(puntos_encontrados, metricas)`, donde
`metricas` es un diccionario con `comparaciones`, `tiempo_ms` y
`profundidad_max` (esta ultima queda en 0 hasta que haya busqueda
recursiva, en la Entrega 3).

## Estructura del proyecto

```
main.py           punto de entrada: llama al menu principal
partida.py        integrador: menus, turnos, estado de la partida, entrada/salida,
                  validacion con regex, excepciones propias del flujo de juego
tablero.py        cubo, validacion de puntos, vecinos, capas y cortes, dibujo,
                  operaciones de matrices y las excepciones de esa parte
flota.py          catalogo de naves, reglas de ubicacion, ubicacion manual y
                  automatica, impactos y estado de cada nave (sana/averiada/hundida)
radar.py          busqueda lineal, busqueda optimizada y sonar por planos
armamento.py      catalogo de armas, celdas que afecta cada una, aplicacion
                  del disparo y manejo de municion
registro.py       historial de la partida, estadisticas y resumen final
                  (el guardado/carga en JSON queda para la Entrega 3)
tests/            pruebas con pytest, una por modulo
docs/bitacora.md  bitacora del equipo
```

Solo `partida.py` y `main.py` usan `print` e `input`; los demas modulos
reciben datos y devuelven datos.

## Excepciones propias

Toda excepcion propia hereda, directa o indirectamente, de
`tablero.ErrorCubo`:

- `tablero.py`: `ErrorCubo` (base), `PuntoInvalidoError`, `MatrizInvalidaError`
- `flota.py`: `NaveInvalidaError`, `UbicacionInvalidaError`, `UbicacionAutomaticaError`
- `armamento.py`: `ArmaInvalidaError`, `MunicionAgotadaError`
- `radar.py`: `EjeInvalidoError`
- `partida.py`: `ObjetivoYaDisparadoError`

El integrador (`partida.py`) atrapa todas estas excepciones con
try/except/else/finally para que un dato invalido nunca corte el programa.

## Que queda para la Entrega 3

Guardado y carga de partidas en JSON, partida maquina contra maquina,
busqueda recursiva, recorridos alternativos del cubo (espiral, octantes),
Onda expansiva y Torpedo guiado, y ranking de partidas.
