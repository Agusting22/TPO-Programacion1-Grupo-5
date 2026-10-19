# Bitacora del equipo

## Entrega 1

| Modulo | Alcance de la Entrega 1 | Responsable |
|--------|-------------------------|-------------|
| tablero.py (Nucleo 3D) | Cubo, excepciones base (`ErrorCubo`, `PuntoInvalidoError`), coordenadas 3D y validacion | Agustín Cangiani |
| tablero.py (Algebra y Render) | Operaciones de matrices (suma, resta, multiplicacion, traspuesta) y `dibujar_capa` | Kevin Palma |
| flota.py (Reglas y Catalogo) | Catalogo de naves, adyacencias en 26 direcciones y restricciones por nave | Thiago Negri |
| flota.py (Algoritmos) | Algoritmo de ubicacion automatica con semilla y colocacion manual interactiva | Francisco Pavlicich |
| radar.py / armamento.py / registro.py | Busqueda lineal con metricas, catalogo de armas (torpedo) e historial en memoria | Angel Nogales |
| partida.py / main.py (integrador) | Menu principal, submenu de ubicacion, validacion con regex y flujo general | Agustin Gonzalez |

Integrador de esta entrega: Agustin Gonzalez

## Entrega 2

| Modulo | Alcance de la Entrega 2 | Responsable |
|--------|--------------------------|-------------|
| tablero.py (Cortes y vecinos) | `vecinos_ortogonales`, cortes fijando x y fijando y | Agustín Cangiani |
| flota.py (Impactos y estado) | Registro de impactos, estado sana/averiada/hundida, comportamientos de Destructor, Submarino y Portaaviones | Thiago Negri |
| flota.py (Estacion y revelado) | Munición extra al hundir la estación orbital, elección de la celda a revelar | Francisco Pavlicich |
| radar.py (Busqueda optimizada y sonar) | Busqueda optimizada por indice de flota, sonar por planos | Angel Nogales |
| armamento.py (Arsenal nuevo) | Misil de racimo, carga de profundidad, barrido laser y manejo de municion por diccionario | Kevin Palma |
| registro.py (Estadisticas) | Estadisticas de la partida y resumen final | Angel Nogales |
| partida.py / main.py (Turnos y partida completa) | Estado de partida, turnos, partida 1v1 y contra la maquina, submenus de disparo y de vista del cubo | Agustin Gonzalez |

Nota: la munición extra de la Estación orbital se otorga sobre el Misil de
racimo (no hay todavía un arma específica para eso, ya que Onda expansiva es
de la Entrega 3). Lo dejamos documentado por si después hay que ajustarlo.

Integrador de esta entrega: Agustin Gonzalez
