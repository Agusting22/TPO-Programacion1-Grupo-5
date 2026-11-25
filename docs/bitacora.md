# Bitacora del equipo

## Entrega 1

| Modulo | Alcance de la Entrega 1 | Responsable |
|--------|-------------------------|-------------|
| tablero.py (Nucleo 3D) | Cubo, excepciones base (ErrorCubo, PuntoInvalidoError), coordenadas 3D y validacion | Agustin Cangiani |
| tablero.py (Algebra y Render) | Operaciones de matrices (suma, resta, multiplicacion, traspuesta) y dibujar_capa | Kevin Palma |
| flota.py (Reglas y Catalogo) | Catalogo de naves, adyacencias en 26 direcciones y restricciones por nave | Thiago Negri |
| flota.py (Algoritmos) | Algoritmo de ubicacion automatica con semilla y colocacion manual interactiva | Francisco Pavlicich |
| radar.py / armamento.py / registro.py | Busqueda lineal con metricas, catalogo de armas (torpedo) e historial en memoria | Angel Nogales |
| partida.py / main.py (integrador) | Menu principal, submenu de ubicacion, validacion con regex y flujo general | Agustin Gonzalez |

Integrador de esta entrega: Agustin Gonzalez

## Entrega 2

| Modulo | Alcance de la Entrega 2 | Responsable |
|--------|--------------------------|-------------|
| tablero.py (Cortes y vecinos) | Vecinos ortogonales, cortes fijando x y fijando y | Agustin Cangiani |
| flota.py (Impactos y estado) | Registro de impactos, estado sana/averiada/hundida, comportamientos de Destructor, Submarino y Portaaviones | Thiago Negri |
| flota.py (Estacion y revelado) | Municion extra al hundir la estacion orbital, eleccion de la celda a revelar | Francisco Pavlicich |
| radar.py (Busqueda optimizada y sonar) | Busqueda optimizada por indice de flota, sonar por planos | Angel Nogales |
| armamento.py (Arsenal nuevo) | Misil de racimo, carga de profundidad, barrido laser y manejo de municion por diccionario | Kevin Palma |
| registro.py (Estadisticas) | Estadisticas de la partida y resumen final | Angel Nogales |
| partida.py / main.py (Turnos y partida completa) | Estado de partida, turnos, partida 1v1 y contra la maquina, submenus de disparo y de vista del cubo | Agustin Gonzalez |

Nota: la municion extra de la Estacion orbital se otorga sobre el Misil de
racimo (no hay todavia un arma especifica para eso, ya que Onda expansiva es
de la Entrega 3). Lo dejamos documentado por si despues hay que ajustarlo.

Integrador de esta entrega: Agustin Gonzalez

## Entrega 3

| Modulo | Alcance de la Entrega 3 | Responsable |
|--------|--------------------------|-------------|
| tablero.py (Recorridos del cubo) | Recorridos alternativos del cubo (capas Z, octantes recursivo, espiral recursivo, propagacion recursiva), despacho por diccionario y excepcion RecorridoInvalidoError | Agustin Cangiani |
| flota.py (Persistencia) | Datos de la flota para guardar y reponer la partida (guardar_datos_flota, reponer_flota, reponer_flota_en_cubo, validar_datos_flota) | Francisco Pavlicich |
| armamento.py (Armas avanzadas) | Onda expansiva (propagacion recursiva) y Torpedo guiado (busqueda contigua recursiva) | Kevin Palma |
| radar.py (Busquedas recursivas) | Busqueda recursiva (capa por capa) | Agustin Gonzalez |
| registro.py (Persistencia JSON y ranking) | Guardado y carga en JSON, listado de partidas y ranking | A designar por el equipo |
| partida.py / main.py (Integrador E3) | Maquina vs maquina, continuar partida guardada, guardar y salir, maquina con dos niveles | Agustin Gonzalez |

Integrador de esta entrega: Agustin Gonzalez
