# Operacion Cubo - Batalla Naval 3D

TPO de Programacion I (UADE). **Estado: ENTREGA 3 (Completo).**

En esta entrega el juego se encuentra 100% completo, integrado y probado:
- Modos de juego completos: **1 vs 1**, **1 vs la maquina** (con dos niveles de dificultad: Facil y Estratega) y **Maquina vs Maquina**.
- Guardado y reanudacion persistente de partidas en formato JSON (`registro.py`, `flota.py`).
- Sistema de ranking historico persistente con calculo de puntuacion (`ranking.json`).
- Busquedas de radar con comparador de metricas: lineal, optimizada y recursiva por capas (`radar.py`).
- Recorridos alternativos del cubo en 3D: capas Z, cortes axiales X e Y, octantes recursivo, espiral recursivo y propagacion esferica recursiva (`tablero.py`).
- Arsenal completo con 7 armas: Torpedo (T), Misil de racimo (R), Carga de profundidad (C), Sonar (S), Barrido laser (L), Onda expansiva (O, recursiva) y Torpedo guiado (G, recursivo) (`armamento.py`).
- Despacho 100% por diccionarios para armas, recorridos y opciones de menu (sin cadenas `if/elif`).
- Manejo robusto de excepciones propias heredadas de `ErrorCubo` mediante bloques `try/except/else/finally`.

---

## Instalacion y Requisitos

Requiere Python 3.10 o superior.

```bash
pip install -r requirements.txt
```

> **Nota:** `requirements.txt` solo incluye `pytest` para la ejecucion de la suite de pruebas automatizadas. Todo el codigo del juego funciona exclusivamente sobre la biblioteca estandar de Python (`json`, `os`, `random`, `re`, `time`).

---

## Ejecucion y Pruebas

Para iniciar el juego:

```bash
python main.py
```

Para correr las pruebas unitarias automatizadas (112 tests):

```bash
python -m pytest -v
```

---

## Menus del Juego

### 1. Menu Principal

```
===== OPERACION CUBO =====
1 - Partida uno contra uno
2 - Partida uno contra la maquina
3 - Partida maquina contra maquina
4 - Continuar partida guardada
5 - Salir
Opcion:
```

- **1 - Partida uno contra uno**: dos jugadores humanos ubican sus flotas y alternan turnos.
- **2 - Partida uno contra la maquina**: partida de un jugador humano contra la inteligencia artificial, pudiendo elegir su dificultad:
  ```
  Nivel de dificultad de la maquina:
  1 - Facil (disparos aleatorios)
  2 - Estratega (mapa de probabilidad y modo caza)
  ```
- **3 - Partida maquina contra maquina**: simulacion automatica entre dos IA. Permite configurar la dificultad de cada maquina (ej. Estratega vs Facil) y una pausa configurable entre turnos para seguir el desarrollo de la contienda.
- **4 - Continuar partida guardada**: escanea la carpeta `partidas/` y lista las partidas guardadas con fecha y jugadores, permitiendo retomar cualquier partida exactamente en el turno y estado en que fue guardada.
- **5 - Salir**: finaliza la aplicacion.

Todas las entradas de menu se validan; si se ingresa una opcion no valida (`abc`, `9`, etc.), el sistema informa el error y vuelve a solicitarla sin cortar el programa.

---

### 2. Ubicacion de Flotas

Antes de iniciar la batalla, los jugadores humanos configuran la disposicion de sus naves:

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

- **Manual**: las coordenadas se ingresan en formato `z,x,y-z,x,y` (para naves lineales) o indicando dos esquinas opuestas para la estacion orbital 2x2x2 (ej. `3,3,3-4,4,4`). El sistema valida que no salgan del cubo, que cumplan las restricciones de cota Z de cada nave y que mantengan una celda de separacion en las 26 direcciones con cualquier otra nave.
- **Automatica**: ubica de forma aleatoria y valida las 10 naves de la flota garantizando todas las restricciones de adyacencia. La flota de la maquina siempre se ubica automaticamente.

---

### 3. Menu de Turno

```
--- Turno de Jugador 1 ---
1 - Disparar
2 - Ver el cubo
3 - Reporte de radar (metricas)
4 - Guardar partida
5 - Salir de la partida
Opcion: 1
```

- **1 - Disparar**: permite elegir el arma deseada (si queda municion) y solicita el objetivo correspondiente segun el tipo de armamento.
- **2 - Ver el cubo**: abre el submenu de vistas y recorridos del cubo:
  - `1 - Ver todas las capas de z` (planos XY secuenciales).
  - `2 - Corte fijando x` (plano lateral).
  - `3 - Corte fijando y` (plano frontal).
  - `4 - Octantes (recursivo)` (particion tridimensional en 8 cuadrantes espaciales).
  - `5 - Espiral (recursivo)` (recorrido por anillos concentricos borde-centro).
  - `6 - Propagacion desde centro (recursivo)` (ondas esfericas desde el centro del cubo).
- **3 - Reporte de radar (metricas)**: ejecuta en paralelo las busquedas lineal, optimizada y recursiva sobre la flota propia, informando celdas activas encontradas, cantidad de comparaciones, tiempo de ejecucion en milisegundos y profundidad maxima de recursion.
- **4 - Guardar partida**: serializa el estado completo en un archivo JSON en la carpeta `partidas/` para continuar mas adelante.
- **5 - Salir de la partida**: interrumpe la partida en curso y regresa al menu principal.

---

## Inteligencia Artificial y Niveles de Dificultad

El juego cuenta con dos niveles de inteligencia artificial para la maquina, implementados en `partida.py` y apoyados en los algoritmos de `radar.py` y `armamento.py`:

### Nivel 1: Facil
- **Comportamiento**: la maquina dispara sobre celdas validas que no hayan sido disparadas previamente, seleccionadas al azar.
- **Armas**: selecciona aleatoriamente entre las armas que cuenten con municion disponible, priorizando el Torpedo convencional.
- **Uso ideal**: partidas introductorias y jugadores principiantes.

### Nivel 2: Estratega (Dificil)
Implementa un modelo tactico dividido en dos fases:

1. **Fase de Caza (Modo Persecucion / Targeting)**:
   - Se activa cuando hay al menos una nave enemiga **averiada pero no hundida** (impacto positivo previo).
   - **Uso de Torpedo Guiado (`G`)**: si la maquina dispone de esta arma, la utiliza inmediatamente, aprovechando el algoritmo de busqueda contigua recursiva (`armamento._buscar_contiguo_recursivo`) para impactar las secciones intactas de la nave averiada.
   - **Rastreo ortogonal**: si no cuenta con Torpedo Guiado, evalua las celdas vecinas ortogonales directas a los impactos previos que aun no hayan recibido disparos.

2. **Fase de Busqueda (Mapa de Probabilidad 3D / Heatmap)**:
   - Se activa cuando no hay naves averiadas pendientes de destruccion.
   - Utiliza la funcion `radar.mapa_probabilidad(dimension, celdas_libres, naves_restantes)` para calcular una matriz 3D con la densidad de probabilidad de presencia de las naves vivas del rival.
   - Dispara sobre la celda con la mayor probabilidad acumulada.
   - **Seleccion estrategica de armas**: si detecta zonas de alta densidad o celdas concentradas, prioriza armas de impacto zonal (Misil de racimo `R`, Carga de profundidad `C` u Onda expansiva `O`) para maximizar el dano esperado.

---

## Persistencia y Sistema de Ranking

El modulo `registro.py` se encarga de la persistencia de datos mediante formato JSON:

### 1. Guardado y Carga de Partidas
- Los archivos se guardan en el directorio `partidas/` (por ejemplo `partida_20261126_201500.json`).
- Estructura persistida:
  - `dimension_cubo`: tamano N del tablero.
  - `jugadores` y `turno_actual`: nombre de los jugadores y a quien le corresponde el turno.
  - `flotas`: serializacion completa de las 10 naves de cada jugador (clave, tipo, tramo de celdas, impactos por celda, estado sana/averiada/hundida).
  - `impactos`: conjunto de celdas ya disparadas por cada jugador.
  - `municiones`: inventario de cada arma para cada jugador.
  - `historial`: lista cronologica de todos los eventos y disparos realizados.
  - `estadisticas`: disparos totales, impactos acertados, fallos al agua y naves hundidas.
  - `modo` y `dificultad`: modalidad de juego (`1v1`, `vs_maquina`, `maquina_vs_maquina`) y dificultad de la IA.

### 2. Ranking Historico
- Se almacena en `ranking.json`.
- Al finalizar una partida, se calcula la puntuacion del ganador en base a:
  $$\text{Puntaje} = (\text{Naves hundidas} \times 100) + (\text{Efectividad de disparo} \times 50) - (\text{Turnos empleados} \times 2)$$
- Registra: nombre del ganador, puntuacion final, turnos empleados, naves destruidas, dificultad y fecha/hora.
- Incluye formateo para visualizar la tabla de posiciones desde la consola.

---

## Reglas del Juego

Cubo de $N \times N \times N$ (por defecto $N = 8$). Las coordenadas $z, x, y$ van de $1$ a $N$.

### Catalogo de la Flota

| Nave | Letra | Celdas | Cantidad | Restriccion de Ubicacion | Comportamiento Especial |
|------|:-----:|:------:|:--------:|--------------------------|--------------------------|
| **Fragata** | F | 2 | 3 | Ninguna | Estandar |
| **Destructor** | D | 3 | 2 | Ninguna | Al ser impactado, contraataca revelando una celda de la flota atacante |
| **Submarino** | S | 3 | 2 | Solo mitad inferior de Z ($z \le N/2$) | Inmune al Barrido laser |
| **Crucero** | C | 4 | 1 | No puede tocar extremos ($z \ne 1$ y $z \ne N$) | Estandar |
| **Portaaviones** | P | 5 | 1 | Solo mitad superior de Z ($z > N/2$) | Cada celda requiere **2 impactos** para considerarse danada |
| **Estacion orbital** | E | Bloque 2x2x2 | 1 | No toca ninguna cara exterior del cubo | Al ser destruida, otorga una municion extra de Misil de racimo |

Entre cualquier par de naves debe existir como minimo **1 celda libre en las 26 direcciones** (adyacencias ortogonales y diagonales).

---

### Catalogo del Arsenal

| Arma | Letra | Municion | Patron de Dano / Efecto |
|------|:-----:|:--------:|-------------------------|
| **Torpedo** | T | Ilimitada | Impacta una celda puntual $(z, x, y)$. |
| **Misil de racimo** | R | 3 | Impacta la celda apuntada y sus 6 celdas vecinas ortogonales. |
| **Carga de profundidad** | C | 2 | Afecta toda la columna vertical del eje Z que pasa por $(x, y)$. |
| **Sonar** | S | 4 | No causa dano; revela el contenido de un plano completo (fijando $Z$, $X$ o $Y$). |
| **Barrido laser** | L | 2 | Barre una fila completa en el eje X o en el eje Y a eleccion (los Submarinos son inmunes). |
| **Onda expansiva** | O | 1 | Se propaga recursivamente en volumen con radio decreciente desde el impacto. |
| **Torpedo guiado** | G | 1 | Si hay un impacto previo sobre una nave no hundida, rastrea recursivamente una celda contigua sana de esa misma nave. |

---

## Modulo de Radar y Comparacion de Algoritmos

El modulo `radar.py` permite monitorear y comparar tres tecnicas algoritmicas de busqueda sobre la flota:

- **Busqueda Lineal (`buscar_naves_lineal`)**: recorre de forma exhaustiva las $N^3$ celdas del espacio cubico mediante tres ciclos `for` anidados ($O(N^3)$ comparaciones).
- **Busqueda Optimizada (`buscar_naves_optimizada`)**: aprovecha el indice de posiciones ocupadas por las naves vivas, realizando consultas directas ($O(K)$ con $K \ll N^3$).
- **Busqueda Recursiva (`buscar_naves_recursiva`)**: divide el cubo por capas Z de manera recursiva (divide y conquista con wrapper `aux(z)`), acumulando las comparaciones y midiendo la profundidad maxima en la pila de llamadas (*call stack*).
- **Reporte comparativo**: la opcion 3 del turno contrasta las tres busquedas mostrando comparaciones realizadas, tiempo en milisegundos y profundidad de recursion.

---

## Estructura de Modulos y Arquitectura

```
main.py           Punto de entrada: inicializa y gestiona el menu principal.
partida.py        Integrador del juego: flujo de turnos, menus, IA (Facil y Estratega),
                  simulacion maquina vs maquina, validacion regex y despacho por diccionarios.
tablero.py        Representacion del cubo 3D, validaciones de coordenadas, algebra de matrices,
                  vistas de corte y recorridos alternativos (capas, octantes, espiral, propagacion).
flota.py          Catalogo de naves, reglas de colocacion manual y automatica, gestion de
                  impactos, estados de salud y serializacion/restauracion de flotas.
radar.py          Busquedas lineal, optimizada y recursiva, sonar y mapa de probabilidad 3D.
armamento.py      Catalogo de armas, aplicacion de impactos, onda expansiva recursiva,
                  torpedo guiado recursivo y administracion de municiones.
registro.py       Persistencia JSON (guardado y carga), historial de turnos,
                  calculo de estadisticas y ranking historico.
tests/            Suite de 112 pruebas unitarias automatizadas con pytest.
docs/bitacora.md  Registro de tareas y responsabilidades del equipo por cada entrega.
```

### Principios de Diseno Aplicados:
1. **Despacho por Diccionario**: ni en los menus, ni en la seleccion de armas, ni en los recorridos del cubo se utilizan cadenas `if/elif`. Se emplean diccionarios que asocian claves a funciones.
2. **Aislamiento de Entrada/Salida**: las funciones `print()` e `input()` se encuentran estrictamente confinadas en `partida.py` y `main.py`. Los demas modulos son puramente funcionales (reciben datos y devuelven datos).
3. **Jerarquia de Excepciones Propias**: todas las excepciones del juego heredan de `tablero.ErrorCubo` (derivada de `Exception`), y son capturadas con bloques `try/except/else/finally` en el ciclo de juego para evitar cortes abruptos.
