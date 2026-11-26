# Operacion Cubo - Batalla Naval 3D

TPO de Programacion I (UADE). **Estado: ENTREGA 3 (Completo).**

En esta entrega el juego se encuentra 100% completo, integrado y testeado:
- Partidas 1 vs 1, 1 vs la maquina (con dos niveles de dificultad: Facil y Estratega), y simulacion Maquina vs Maquina.
- Guardado y reanudacion persistente de partidas en formato JSON (`registro.py`, `flota.py`).
- Ranking persistente de victorias y puntuaciones en JSON.
- Busquedas de radar: lineal, optimizada y recursiva por capas (`radar.py`), con comparador de metricas (comparaciones, tiempo en ms y profundidad de recursion).
- Recorridos alternativos del cubo en 3D: capas Z, corte X, corte Y, octantes recursivo, espiral recursivo y propagacion esferica recursiva (`tablero.py`).
- Arsenal completo con las 7 armas: Torpedo (T), Misil de racimo (R), Carga de profundidad (C), Sonar (S), Barrido laser (L), Onda expansiva (O, propagacion recursiva) y Torpedo guiado (G, busqueda contigua recursiva) (`armamento.py`).
- Despacho 100% por diccionarios para armas, recorridos y opciones de menu (sin cadenas `if/elif`).
- Manejo robusto de excepciones propias heredadas de `ErrorCubo` con `try/except/else/finally`.

## Instalacion

Requiere Python 3.10 o superior.

```
pip install -r requirements.txt
```

`requirements.txt` solo contiene `pytest` (se usa unicamente para la ejecucion de pruebas unitarias).
Todo el resto del proyecto utiliza exclusivamente la biblioteca estandar de Python (`json`, `os`, `random`, `re`, `time`).

## Ejecucion

```
python main.py
```

## Pruebas

Desde la raiz del proyecto:

```
python -m pytest
```

(Actualmente cuenta con 112 pruebas unitarias automatizadas cubriendo todos los modulos).

## Menus

### Menu principal

```
===== OPERACION CUBO =====
1 - Partida uno contra uno
2 - Partida uno contra la maquina
3 - Partida maquina contra maquina
4 - Continuar partida guardada
5 - Salir
Opcion:
```

- **Partida uno contra uno**: dos jugadores humanos ubican sus flotas y alternan turnos.
- **Partida uno contra la maquina**: permite elegir la dificultad de la IA:
  - `1 - Facil`: disparos y armas elegidas de forma aleatoria sobre casilleros no impactados.
  - `2 - Estratega`: combina un modo de caza (analiza impactos previos para perseguir naves) y un mapa de probabilidades 3D (`radar.mapa_probabilidad`) para maximizar la eficacia de cada disparo y seleccion de armamento.
- **Partida maquina contra maquina**: simulacion automatica entre dos inteligencias artificiales con pausa configurable entre turnos.
- **Continuar partida guardada**: lista las partidas guardadas en `partidas/` para reanudar cualquier partida previa en el turno exacto donde se dejo.
- **Salir**: finaliza el programa.

Si se tipea algo que no es una opcion valida (por ejemplo `abc` o `9`) se avisa y se vuelve a solicitar; el programa nunca se interrumpe por entradas no validas.

### Submenu de ubicacion de flota

Antes de empezar, cada jugador humano ubica su flota (la flota de la maquina siempre se ubica de forma automatica):

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

El tramo se ingresa en formato `z,x,y-z,x,y`. La estacion orbital (E) se ingresa con dos esquinas opuestas del bloque 2x2x2 (ej. `3,3,3-4,4,4`).
Si el tramo no se puede ubicar (fuera del cubo, solapamiento o violacion de la distancia de seguridad de 1 celda en las 26 direcciones) se avisa con `No se puede ubicar ahi. Intente de nuevo.` y se repite la solicitud.

### Turno de juego

```
--- Turno de Jugador 1 ---
1 - Disparar
2 - Ver el cubo
3 - Reporte de radar (metricas)
4 - Guardar partida
5 - Salir de la partida
Opcion: 1

Arma (T/R/C/S/L/O/G): T
Objetivo: 4,2,7
Impacto. Destructor averiado (1 de 3).
```

- **Disparar**: solicita la letra del arma y sus coordenadas correspondientes:
  - Torpedo (T), Misil de racimo (R), Carga de profundidad (C) y Onda expansiva (O): solicitan un punto `z,x,y`.
  - Barrido laser (L): solicita el punto y el eje de barrido (`x` o `y`).
  - Sonar (S): no causa dano, revela un plano completo solicitando eje (`z`, `x` o `y`) y su valor.
  - Torpedo guiado (G): solicita un punto inicial; si impacta una nave ya averiada, rastrea recursivamente sus secciones contiguas intactas.
- **Ver el cubo**: despliega el menu de vistas y recorridos:
  - `1 - Ver todas las capas de z`
  - `2 - Corte fijando x`
  - `3 - Corte fijando y`
  - `4 - Octantes (recursivo)`: divide el cubo en 8 octantes de forma recursiva.
  - `5 - Espiral (recursivo)`: recorre las capas en espiral concentrica desde el borde al centro.
  - `6 - Propagacion desde centro (recursivo)`: recorre las celdas en ondas esfericas desde el centro `(N//2, N//2, N//2)`.
- **Reporte de radar (metricas)**: ejecuta y compara la busqueda lineal (`buscar_naves_lineal`), la optimizada (`buscar_naves_optimizada`) y la recursiva (`buscar_naves_recursiva`) sobre la flota propia, informando celdas activas, comparaciones realizadas, tiempo en milisegundos y profundidad maxima alcanzada en la recursion.
- **Guardar partida**: serializa el estado completo a formato JSON en la carpeta `partidas/` para reanudarla mas tarde.
- **Salir de la partida**: interrumpe la partida en curso y regresa al menu principal.

Al finalizar una partida por destruccion total de la flota rival, se proclama al ganador, se presentan las estadisticas completas de disparos, aciertos y fallos, y se guarda la victoria en el ranking general.

## Reglas del juego

Cubo de N x N x N (por defecto N = 8). Las coordenadas z, x, y van de 1 a N.

### Flota

| Nave | Letra | Celdas | Cantidad | Restriccion | Comportamiento propio |
|------|-------|--------|----------|-------------|------------------------|
| Fragata | F | 2 | 3 | ninguna | - |
| Destructor | D | 3 | 2 | ninguna | al ser impactado revela una celda de la flota rival (del atacante) |
| Submarino | S | 3 | 2 | solo mitad inferior de z | no es alcanzado por el barrido laser |
| Crucero | C | 4 | 1 | no puede ocupar z = 1 ni z = N | - |
| Portaaviones | P | 5 | 1 | solo mitad superior de z | cada celda necesita dos impactos para contar como destruida |
| Estacion orbital | E | bloque 2x2x2 | 1 | no toca ninguna cara exterior | al hundirse otorga una municion extra de Misil de racimo |

Cada nave ocupa una recta contigua ortogonal (salvo la estacion orbital que ocupa un bloque cubico de 2x2x2).
Ninguna nave sale de los limites del cubo y entre naves existe una distancia minima de 1 celda libre en las 26 direcciones (incluyendo diagonales).

### Arsenal

| Arma | Letra | Municion | Celdas que afecta |
|------|-------|----------|--------------------|
| Torpedo | T | ilimitada | la celda apuntada |
| Misil de racimo | R | 3 | la celda apuntada y sus 6 vecinas ortogonales |
| Carga de profundidad | C | 2 | toda la recta del eje z que pasa por el punto |
| Sonar | S | 4 | no hace dano: revela un plano completo (eje + valor) |
| Barrido laser | L | 2 | una recta completa sobre el eje x o el eje y, a eleccion |
| Onda expansiva | O | 1 | se propaga en forma recursiva desde el punto de impacto |
| Torpedo guiado | G | 1 | rastrea en forma recursiva una celda contigua danada no hundida |

La seleccion de cada accion, tipo de arma y recorrido se resuelve estrictamente mediante despacho por diccionario, prescindiendo de estructuras `if/elif`.

## Modulo de Radar y Busquedas

- **Busqueda lineal** (`radar.buscar_naves_lineal`): recorre sistematicamente las N^3 celdas del cubo con bucles anidados.
- **Busqueda optimizada** (`radar.buscar_naves_optimizada`): consulta directamente las celdas registradas en los indices de las naves vivas, reduciendo significativamente las comparaciones.
- **Busqueda recursiva** (`radar.buscar_naves_recursiva`): recorre el cubo dividiendo el espacio capa por capa (`z`) de manera recursiva, registrando comparaciones y la profundidad maxima de recursion.
- **Mapa de probabilidad** (`radar.mapa_probabilidad`): genera una matriz tridimensional de densidades probabilísticas a partir de las naves rivales aun a flote y las celdas disponibles, empleada por la maquina en dificultad Estratega.

## Estructura del proyecto

```
main.py           punto de entrada: inicializa el menu principal
partida.py        integrador: menus, turnos, IA (facil/estratega), maquina vs maquina,
                  flujo de juego, validacion regex y despacho por diccionario
tablero.py        representacion del cubo 3D, validaciones, matrices, vistas de corte,
                  y recorridos alternativos (capas, octantes, espiral, propagacion)
flota.py          catalogo y reglas de naves, ubicacion manual y automatica,
                  impactos, estados y persistencia/restauracion de flotas
radar.py          busquedas lineal, optimizada y recursiva, sonar y mapa de probabilidad
armamento.py      catalogo de armas, efectos de impacto, onda expansiva recursiva,
                  torpedo guiado recursivo y administracion de municion
registro.py       persistencia JSON (guardar/cargar partida), historial de turnos,
                  calculo de estadisticas y ranking historico
tests/            suite de pruebas unitarias automatizadas con pytest (112 tests)
docs/bitacora.md  bitacora del equipo con asignacion de tareas de cada entrega
```

Solo `partida.py` y `main.py` interactuan con el usuario mediante `print` e `input`. Todos los demas modulos son puramente funcionales (reciben parametros y retornan estructuras de datos).

## Excepciones propias

Todas las excepciones del sistema heredan, directa o indirectamente, de `tablero.ErrorCubo`:

- `tablero.py`: `ErrorCubo` (clase base), `PuntoInvalidoError`, `MatrizInvalidaError`, `RecorridoInvalidoError`
- `flota.py`: `NaveInvalidaError`, `UbicacionInvalidaError`, `UbicacionAutomaticaError`
- `armamento.py`: `ArmaInvalidaError`, `MunicionAgotadaError`
- `radar.py`: `EjeInvalidoError`
- `partida.py`: `ObjetivoYaDisparadoError`

Todas son capturadas en el ciclo del juego mediante bloques `try/except/else/finally`, impidiendo caidas inesperadas ante ingresos invalidos.
