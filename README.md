# Operacion Cubo - Batalla Naval 3D

TPO de Programacion I (UADE). **Entrega final.**

Batalla naval por consola dentro de un cubo de 8 x 8 x 8. Incluye:

- Tres modos: uno contra uno, uno contra la maquina y maquina contra maquina.
- Dos niveles para la maquina: Facil y Dificil.
- Siete armas, entre ellas dos con algoritmos recursivos.
- Tres busquedas de radar con metricas y seis vistas del cubo.
- Guardado y carga de partidas en JSON, ranking de partidas terminadas y exportacion de reportes.

---

## Instalacion

Requiere Python 3.10 o superior.

```bash
pip install -r requirements.txt
```

`requirements.txt` solo incluye `pytest`, que se usa para las pruebas. El juego usa unicamente la biblioteca estandar de Python.

---

## Ejecucion

Desde la **raiz del repositorio** (la carpeta donde esta `main.py`):

```bash
python main.py
```

Las rutas de `partidas/`, `exportaciones/` y `ranking.json` son relativas a la carpeta desde la que se ejecuta el programa. Si se ejecuta desde otra carpeta, no se van a encontrar las partidas guardadas.

## Pruebas

Tambien desde la raiz del repositorio (154 pruebas):

```bash
python -m pytest -v
```

---

## Menus

Las opciones se validan: ante un dato no valido se muestra `Dato invalido. Intente de nuevo.` y se vuelve a pedir. Con `Ctrl+C` o fin de la entrada, el programa sale con un mensaje (lo no guardado se pierde).

### Menu principal

```
===== OPERACION CUBO =====
1 - Partida uno contra uno
2 - Partida uno contra la maquina
3 - Partida maquina contra maquina
4 - Continuar una partida guardada
5 - Salir
```

### Ubicacion de flotas

```
1 - Ubicacion manual
2 - Ubicacion automatica
```

- **Manual**: se pide la nave (`Nave (F/D/S/C/P/E):`) y sus extremos (`Desde-hasta:`) con el formato `z,x,y-z,x,y`, por ejemplo `3,5,4-3,5,5`. Las naves son rectas sobre un solo eje. Para la estacion orbital se indican dos esquinas opuestas del bloque, por ejemplo `3,3,3-4,4,4`. Si alguna nave pendiente se queda sin ninguna posicion valida, la flota se reinicia.
- **Automatica**: ubica al azar las 10 naves respetando las reglas.

La flota de la maquina siempre se ubica de forma automatica. Antes de empezar se pide confirmacion: `Ambas flotas ubicadas. Iniciar partida (s/n):`.

### Dificultad de la maquina

```
Dificultad de la maquina:
1 - Facil (disparos aleatorios)
2 - Dificil (estratega: caza naves averiadas y mapa de probabilidad)
```

### Menu de turno

```
--- Turno de Jugador 1 ---
1 - Disparar
2 - Ver el cubo
3 - Reporte de radar (metricas)
4 - Guardar y salir
5 - Salir de la partida
```

- **1 - Disparar**: pide el arma (`Arma (T/R/C/S/L/O/G):`) y el objetivo. Si la jugada es valida, el turno pasa al rival. Si no (sin municion, celda ya disparada o dato invalido), el turno no cambia.
- **2 - Ver el cubo**: abre el submenu de vistas. No consume el turno.
- **3 - Reporte de radar (metricas)**: compara las tres busquedas sobre la flota propia. No consume el turno.
- **4 - Guardar y salir**: guarda la partida y vuelve al menu principal.
- **5 - Salir de la partida**: vuelve al menu principal **sin guardar**.

### Ver el cubo

```
--- Ver el cubo ---
1 - Capas en el eje z
2 - Corte fijando x
3 - Corte fijando y
4 - Recorrido por octantes
5 - Recorrido en espiral
6 - Recorrido por propagacion (desde el centro)
```

La vista elegida se muestra para el cubo propio y para el del rival (sin revelar sus naves ocultas).

| Opcion | Que muestra |
|--------|-------------|
| 1 | Las 8 capas, con `y` en las filas y `x` en las columnas |
| 2 | El plano de un `x` elegido, con `z` en las filas e `y` en las columnas |
| 3 | El plano de un `y` elegido, con `z` en las filas y `x` en las columnas |
| 4 | Lista de celdas en el orden de una subdivision recursiva en octantes |
| 5 | Lista de celdas capa por capa, en espiral recursiva del borde al centro |
| 6 | Lista de celdas por distancia ortogonal creciente (recursivo) desde un origen. El programa pide `Origen (z,x,y):`; con Enter usa el centro |

Simbolos: `~` sin explorar, `o` agua, `X` impacto, `#` hundido, `?` detectado. En el cubo propio, las celdas de nave sin dano ni deteccion se muestran con la letra de la nave.

---

## Reglas

Las coordenadas se escriben como `z,x,y`, con valores de 1 a 8. Hay dos jugadores y cada uno realiza una jugada por turno. Gana quien hunde toda la flota rival.

### Flota (10 naves por jugador)

| Nave | Letra | Celdas | Cantidad | Restriccion | Comportamiento especial |
|------|:-----:|:------:|:--------:|-------------|-------------------------|
| Fragata | F | 2 | 3 | Ninguna | - |
| Destructor | D | 3 | 2 | Ninguna | Por cada celda suya impactada se marca como detectada una celda oculta de la flota atacante |
| Submarino | S | 3 | 2 | Solo en la mitad inferior (z de 1 a 4) | Inmune al barrido laser |
| Crucero | C | 4 | 1 | No ocupa z = 1 ni z = 8 | - |
| Portaaviones | P | 5 | 1 | Solo en la mitad superior (z de 5 a 8) | Cada celda necesita 2 impactos para quedar danada |
| Estacion orbital | E | 8 (bloque 2x2x2) | 1 | No toca ninguna cara exterior del cubo | Al hundirla, el atacante suma 1 misil de racimo |

Entre dos naves tiene que quedar al menos una celda libre en las 26 direcciones (incluidas las diagonales).

El primer impacto sobre una celda del Portaaviones informa la nave como averiada, pero esa celda todavia no se marca como impactada y se puede volver a disparar.

### Armas

| Arma | Letra | Municion inicial | Datos que pide | Efecto |
|------|:-----:|:----------------:|----------------|--------|
| Torpedo | T | Ilimitada | Objetivo | Una celda |
| Misil de racimo | R | 3 | Objetivo | La celda y sus vecinas ortogonales (hasta 6) |
| Carga de profundidad | C | 2 | Objetivo | Toda la recta en el eje z que pasa por ese (x, y) |
| Sonar | S | 4 | Eje (z/x/y) y valor | No hace dano; marca como detectadas las naves ocultas de un plano completo. Consume el turno |
| Barrido laser | L | 2 | Objetivo y eje (x/y) | Toda la recta sobre el eje elegido; no afecta a los submarinos |
| Onda expansiva | O | 1 | Objetivo | Propagacion recursiva hasta 2 pasos ortogonales desde el objetivo |
| Torpedo guiado | G | 1 | Objetivo | Si hay una nave rival impactada y no hundida, busca recursivamente una celda contigua de esa nave que falte danar. Si no hay, afecta la celda apuntada |

En las armas que piden objetivo, la celda apuntada no puede ser una que ya figure como agua, impacto o hundida.

---

## Modos de juego y niveles de la maquina

| Modo | Jugadores |
|------|-----------|
| Uno contra uno | `Jugador 1` y `Jugador 2`, ambos humanos, en la misma consola |
| Uno contra la maquina | `Jugador 1` contra `Maquina` |
| Maquina contra maquina | `Maquina` contra `Maquina 2`, cada una con su dificultad |

### Nivel Facil

Dispara siempre con torpedo a una celda al azar que todavia no haya sido disparada.

### Nivel Dificil

Usa solamente el torpedo y el torpedo guiado. En cada turno aplica, en orden:

1. Si le queda el torpedo guiado y hay una nave rival averiada, lo usa.
2. Si hay una nave averiada con una celda marcada como impacto, dispara un torpedo a una celda vecina ortogonal sin disparar.
3. En otro caso, calcula el mapa de probabilidad y dispara un torpedo a la celda de mayor valor (si hay empate, elige al azar entre ellas).

El mapa de probabilidad (`radar.mapa_probabilidad(cubo, largos)`) cuenta, para cada celda, en cuantas posiciones rectas de las naves lineales a flote podria estar incluida, descartando las rectas que pasan por agua marcada o celdas hundidas. Las naves ocultas se tratan como celdas sin explorar y la estacion orbital no se cuenta.

### Maquina contra maquina

La partida se muestra turno a turno. Aparece un menu de pausa antes del primer turno (tambien al retomar una partida guardada) y luego segun la opcion elegida:

```
--- Pausa (turnos jugados: N) ---
1 - Continuar (proxima pausa en 50 turnos)
2 - Avanzar un solo turno
3 - Guardar y salir
4 - Salir de la partida
```

Las pausas son fijas: cada 50 turnos con la opcion 1. Si se llega al limite de turnos, que depende del tamano N del cubo (2 x (N^3 + 5) + 66, es decir 1100 con N = 8), la partida termina sin ganador.

---

## Busquedas de radar

La opcion 3 del menu de turno ejecuta, una despues de otra, tres busquedas de las celdas propias que tienen nave sin dano (ocultas o detectadas):

| Busqueda | Funcion | Como trabaja |
|----------|---------|--------------|
| Lineal | `buscar_naves_lineal` | Tres ciclos anidados sobre las 512 celdas |
| Optimizada | `buscar_naves_optimizada` | Consulta solo las celdas registradas en la flota (35 en una flota completa) |
| Recursiva | `buscar_naves_recursiva` | Revisa una capa z y se llama a si misma con la siguiente (profundidad 8) |

De cada una informa celdas encontradas, comparaciones, tiempo en milisegundos y profundidad maxima de recursion. Al final lista las celdas activas.

---

## Partidas guardadas

### Como guardar

- **Uno contra uno y contra la maquina**: en el menu de turno, opcion `4 - Guardar y salir`.
- **Maquina contra maquina**: en el menu de pausa, opcion `3 - Guardar y salir`.

En ambos casos se pide `Nombre de la partida:`. Si se guarda correctamente, se vuelve al menu principal. Si el archivo no se puede escribir, se informa el error y la partida sigue abierta.

- **Nombres validos**: de 1 a 30 caracteres entre letras, numeros, guion (`-`) y guion bajo (`_`). Sin espacios ni extension.
- **Sobrescritura**: guardar con un nombre que ya existe **reemplaza el archivo sin pedir confirmacion**.

### Como retomar

1. En el menu principal, elegir `4 - Continuar una partida guardada`.
2. El programa lista los nombres disponibles en orden alfabetico.
3. Escribir el nombre (sin `.json`). La partida continua con el turno, los cubos, las flotas y las municiones guardados.

Si no hay archivos, se informa `No hay partidas guardadas.`. Si el nombre no existe, `No se encontro la partida`. Si el archivo esta danado o le faltan datos, se muestra `Error al cargar la partida:` seguido del detalle y se vuelve al menu principal; el archivo no se modifica.

### Donde queda y que contiene

Cada partida es un archivo `partidas/<nombre>.json`.

| Clave | Contenido |
|-------|-----------|
| `n` | Tamano del cubo |
| `jugador_1`, `jugador_2` | Nombres de los jugadores |
| `turno_actual` | A quien le toca jugar |
| `ganador` | Nombre del ganador o `null` |
| `es_vs_maquina`, `es_maquina_vs_maquina` | Indican el modo |
| `dificultad` | `"facil"`, `"dificil"` o `null` en uno contra uno |
| `dificultades` | Dificultad de cada maquina en maquina contra maquina; `null` en los otros modos |
| `cubos` | Por jugador, matriz `[z][x][y]`: 0 sin explorar, 1 nave oculta, 2 agua, 3 impacto, 4 hundido, 5 detectado |
| `flotas` | Por jugador y nave: `tipo`, `puntos`, `impactos` (cantidad por celda `"z,x,y"`) y `hundida` |
| `municiones` | Por jugador y letra de arma; `null` significa ilimitada |
| `estadisticas` | Por jugador: `disparos`, `aciertos`, `fallos`, `naves_hundidas` |
| `historial` | Lista de jugadas: `numero`, `jugador` y `detalle` (`arma`, `punto`, `eje`, `valor`, `resultado`) |

### Partidas de demostracion incluidas

Partidas a mitad de juego, sin ganador. Los turnos se cuentan sumando las jugadas de ambos jugadores.

| Nombre | Modo | Estado al cargarla |
|--------|------|--------------------|
| `demo_1v1` | Uno contra uno | 34 turnos, juega Jugador 1. Cada jugador tiene 10 aciertos y hundio una fragata y un destructor. Ambos usaron 2 sonares y 1 misil de racimo |
| `demo_facil` | Contra la maquina (Facil) | 34 turnos, juega Jugador 1. Jugador 1 tiene 10 aciertos, hundio una fragata y un destructor y uso 2 sonares y 1 misil de racimo. La maquina logro 1 acierto, sobre la estacion orbital |
| `demo_dificil` | Contra la maquina (Dificil) | 34 turnos, juega Jugador 1. Jugador 1 tiene 10 aciertos y hundio una fragata y un destructor. La maquina hundio un submarino y ya uso su torpedo guiado |
| `demo_maquinas` | Maquina (Dificil) contra Maquina 2 (Facil) | 150 turnos, juega Maquina. Maquina hundio 4 naves (dos destructores, un submarino y la estacion orbital) y tiene 17 aciertos; Maquina 2 tiene 7 y no hundio naves. Abre en el menu de pausa |

Para conservar una demostracion en su estado original, al guardar despues de jugarla conviene usar otro nombre.

---

## Fin de la partida, ranking y exportaciones

Cuando hay un ganador se muestran las estadisticas, se agrega la partida al ranking, se muestra el ranking y se pregunta `Exportar reporte de la partida (s/n):`.

- **`ranking.json`**: lista de partidas ganadas, en el orden en que terminaron. Cada entrada tiene `ganador`, `partida` (`sin_nombre` si nunca se guardo ni se cargo), `turnos`, `es_vs_maquina` y `timestamp`. Las partidas entre maquinas figuran como `vs maquina`. Si el archivo esta danado, se avisa, no se modifica y ese resultado no se registra.
- **`exportaciones/<nombre>.txt`**: reporte con fecha, modo, jugadores, ganador, turnos, estadisticas e historial. Usa el nombre de la partida o lo pide si no tiene. Reemplaza un reporte anterior con el mismo nombre.

Una partida entre maquinas que llega al limite de turnos no entra al ranking, pero se puede exportar.

`ranking.json` y `exportaciones/` se crean al usarlos y estan excluidos del control de versiones.

---

## Estructura del proyecto

```
main.py       Punto de entrada.
partida.py    Menus, turnos, entrada y salida por consola y jugadas de la maquina.
tablero.py    Cubo 3D, coordenadas, dibujo de capas y cortes, recorridos y operaciones de matrices.
flota.py      Catalogo de naves, ubicacion, impactos y datos de la flota para guardar.
radar.py      Busquedas, sonar y mapa de probabilidad.
armamento.py  Catalogo de armas, municion y aplicacion de disparos.
registro.py   Historial, estadisticas, guardado y carga, ranking y exportacion.
partidas/     Partidas guardadas.
tests/        Pruebas con pytest.
docs/         Bitacora del equipo.
```

Criterios de diseno:

- La seleccion de acciones de los menus, armas, vistas y niveles de la maquina se despacha con diccionarios.
- `input()` y `print()` se usan solo en `partida.py`.
- Las excepciones propias del juego heredan de `tablero.ErrorCubo`.
