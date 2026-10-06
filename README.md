# Operacion Cubo - Batalla Naval 3D

TPO de Programacion I (UADE). **Estado: ENTREGA 1.**

En esta entrega se puede ubicar la flota (manual o automatica) y ver el cubo
dibujado por capas. **Todavia no hay turnos, disparos, victoria, guardado de
partidas ni partida maquina contra maquina**: eso corresponde a las Entregas 2 y 3.

## Instalacion

Requiere Python 3.10 o superior.

```
pip install -r requirements.txt
```

`requirements.txt` solo contiene `pytest` (se usa unicamente para las pruebas).

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
3 - Partida maquina contra maquina
4 - Continuar una partida guardada
5 - Salir
Opcion:
```

| Opcion | Que hace en la Entrega 1 |
|--------|--------------------------|
| 1 | Pasa al submenu de ubicacion de flota del Jugador 1 y dibuja el cubo |
| 2 | Igual que la 1 y, ademas, ubica automaticamente la flota de la maquina |
| 3 | Muestra "Disponible en una proxima entrega" |
| 4 | Muestra "Disponible en una proxima entrega" |
| 5 | Sale del programa |

El menu se vuelve a mostrar despues de cada accion. Si se tipea algo que no es
una opcion valida (por ejemplo `abc` o `9`) se avisa y se vuelve a preguntar.

### Submenu de ubicacion de flota

```
--- Flota de Jugador 1 ---
1 - Ubicacion manual
2 - Ubicacion automatica
Opcion:
```

- **1 - Ubicacion manual**: muestra las naves pendientes
  (`Pendientes:  F x3  D x2  S x2  C x1  P x1  E x1`), pide `Nave (F/D/S/C/P/E):`
  y `Desde-hasta:`. El tramo se escribe `z,x,y-z,x,y`, por ejemplo `3,5,4-3,5,5`.
  La estacion orbital (E) se escribe con dos esquinas opuestas del bloque,
  por ejemplo `3,3,3-4,4,4`. Si se ubica bien, muestra `Ubicada.`; si no,
  `No se puede ubicar ahi. Intente de nuevo.`. Se repite hasta ubicar las 10 naves.
- **2 - Ubicacion automatica**: coloca la flota completa respetando las mismas reglas.

Al terminar se dibujan todas las capas de z, con la letra de cada nave.

## Reglas del juego implementadas

Cubo de N x N x N (por defecto N = 8). Los ejes z, x, y van de 1 a N.

| Nave | Letra | Celdas | Cantidad | Restriccion |
|------|-------|--------|----------|-------------|
| Fragata | F | 2 | 3 | ninguna |
| Destructor | D | 3 | 2 | ninguna |
| Submarino | S | 3 | 2 | solo mitad inferior de z |
| Crucero | C | 4 | 1 | no puede ocupar z = 1 ni z = N |
| Portaaviones | P | 5 | 1 | solo mitad superior de z |
| Estacion orbital | E | bloque 2x2x2 | 1 | no toca ninguna cara exterior |

Cada nave es una recta contigua sobre un eje (la estacion es un bloque).
Ninguna sale del cubo y entre dos naves queda al menos una celda libre en las
26 direcciones (incluye diagonales).

## Estructura del proyecto

```
main.py           punto de entrada: llama al menu principal
partida.py        integrador: menus, entrada/salida, validacion con regex, dibujo del estado
tablero.py        cubo, validacion de puntos, dibujo de capas, operaciones de matrices
                  y las excepciones propias de la validacion de puntos y matrices
flota.py          catalogo de naves, reglas, ubicacion manual y automatica
                  (y sus excepciones propias)
radar.py          busqueda lineal con metricas
armamento.py      catalogo de armas y torpedo
registro.py       historial de la partida en memoria
tests/            pruebas con pytest (una por modulo)
docs/bitacora.md  bitacora del equipo
```

Solo `partida.py` y `main.py` usan `print` e `input`; los demas modulos reciben
datos y devuelven datos.

## API de los modulos (Entrega 1)

Las funciones no tienen parametros por defecto: se pasan todos los argumentos.
Un punto es una tupla `(z, x, y)` con valores desde 1.

**tablero.py**
- Excepciones propias: `ErrorCubo` (base de toda la aplicacion), `PuntoInvalidoError` y
  `MatrizInvalidaError`
- `crear_cubo(n)`
- `es_punto_valido(punto, n)`, `validar_punto(punto, n)`, `convertir_a_indices(punto)`
- `leer_celda(cubo, punto)`, `escribir_celda(cubo, punto, estado)`
- `dibujar_capa(cubo, z, letras_por_punto)` (con `None` es la vista del rival)
- `validar_matriz(m)`, `sumar_matrices(a, b)`, `restar_matrices(a, b)`,
  `multiplicar_matrices(a, b)`, `transponer_matriz(a)`

**flota.py**
- Excepciones propias (heredan de `ErrorCubo`): `NaveInvalidaError`,
  `UbicacionInvalidaError`, `UbicacionAutomaticaError`
- `ubicar_nave(cubo, flota, nave, punto_desde, punto_hasta)` y
  `ubicacion_automatica(cubo, catalogo, semilla)`
- `CATALOGO_NAVES`, `crear_flota()`, `contar_naves_tipo(flota, letra)`,
  `obtener_pendientes(flota, catalogo)`, `obtener_letras_por_punto(flota)`
- `calcular_puntos_nave(letra, desde, hasta, catalogo)`,
  `puede_ubicar_nave(cubo, letra, puntos, catalogo)`, `hay_nave_cerca(cubo, punto)`
- `es_mitad_inferior(z, n)`, `es_mitad_superior(z, n)` y las reglas por nave

**radar.py**
- `buscar_naves_lineal(cubo)` devuelve `(puntos, metricas)` con las claves
  `comparaciones`, `tiempo_ms` y `profundidad_max`.

**armamento.py**
- `CATALOGO_ARMAS` (las 7 armas) y `obtener_celdas_torpedo(punto, n)`. Solo el torpedo
  tiene logica; las demas armas figuran en el catalogo y se implementan despues.

**registro.py**
- `crear_historial()`, `registrar_evento(historial, jugador, detalle)`,
  `obtener_eventos(historial)`.

## Que queda para las proximas entregas

- Entrega 2: impactos y naves averiadas/hundidas, cortes por x e y, vecinos de una celda,
  armas restantes, municion, estadisticas, turnos y victoria, busqueda optimizada.
- Entrega 3: guardado y carga en JSON, partida maquina contra maquina, continuar partida,
  recorridos y busqueda recursivos, ranking.
