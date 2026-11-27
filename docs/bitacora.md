# Bitacora del equipo

## Entrega 1

| Modulo | Alcance de la Entrega 1 | Responsable |
|--------|-------------------------|-------------|
| tablero.py (Nucleo 3D) | Cubo, excepciones base (ErrorCubo, PuntoInvalidoError), coordenadas 3D y validacion | Agustin Cangiani |
| tablero.py (Algebra y Render) | Operaciones de matrices (suma, resta, multiplicacion, traspuesta) y dibujar_capa | Kevin Palma |
| flota.py (Reglas y Catalogo) | Catalogo de naves, adyacencias en 26 direcciones y restricciones por nave | Francisco Pavlicich |
| flota.py (Algoritmos) | Algoritmo de ubicacion automatica con semilla y colocacion manual interactiva | Francisco Pavlicich |
| radar.py / armamento.py / registro.py | Busqueda lineal con metricas, catalogo de armas (torpedo) e historial en memoria | Kevin Palma |
| partida.py / main.py (integrador) | Menu principal, submenu de ubicacion, validacion con regex y flujo general | Agustin Gonzalez |

Integrador de esta entrega: Agustin Gonzalez

## Entrega 2

| Modulo | Alcance de la Entrega 2 | Responsable |
|--------|--------------------------|-------------|
| tablero.py (Cortes y vecinos) | Vecinos ortogonales, cortes fijando x y fijando y | Agustin Cangiani |
| flota.py (Impactos y estado) | Registro de impactos, estado sana/averiada/hundida, comportamientos de Destructor, Submarino y Portaaviones | Agustin Cangiani |
| flota.py (Estacion y revelado) | Municion extra al hundir la estacion orbital, eleccion de la celda a revelar | Francisco Pavlicich |
| radar.py (Busqueda optimizada y sonar) | Busqueda optimizada por indice de flota, sonar por planos | Kevin Palma |
| armamento.py (Arsenal nuevo) | Misil de racimo, carga de profundidad, barrido laser y manejo de municion por diccionario | Kevin Palma |
| registro.py (Estadisticas) | Estadisticas de la partida y resumen final | Agustin Cangiani |
| partida.py / main.py (Turnos y partida completa) | Estado de partida, turnos, partida 1v1 y contra la maquina, submenus de disparo y de vista del cubo | Agustin Gonzalez |

Nota: la municion extra que otorga la Estacion orbital al ser hundida se suma
al Misil de racimo.

Integrador de esta entrega: Agustin Gonzalez

## Entrega 3

| Modulo | Alcance de la Entrega 3 | Responsable |
|--------|--------------------------|-------------|
| tablero.py / radar.py (Recorridos del cubo) | Recorridos alternativos del cubo: capas Z en tablero.py; octantes recursivo, espiral recursivo, propagacion recursiva, despacho por diccionario y excepcion RecorridoInvalidoError en radar.py | Agustin Cangiani |
| flota.py (Persistencia) | Datos de la flota para guardar y reponer la partida (guardar_datos_flota, reponer_flota, reponer_flota_en_cubo, validar_datos_flota) | Francisco Pavlicich |
| armamento.py (Armas avanzadas) | Onda expansiva (propagacion recursiva) y Torpedo guiado (busqueda contigua recursiva) | Kevin Palma |
| radar.py (Busquedas recursivas) | Busqueda recursiva (capa por capa) | Agustin Gonzalez |
| registro.py (Persistencia JSON y ranking) | Guardado y carga en JSON, listado de partidas y ranking | Francisco Pavlicich |
| partida.py / main.py (Integrador E3) | Maquina vs maquina, continuar partida guardada, guardar y salir, maquina con dos niveles | Agustin Gonzalez |

La entrega incluye ademas el mapa de probabilidad de radar.py, que utiliza la
maquina en el nivel dificil.

Integrador de esta entrega: Agustin Gonzalez

## Entrega final

Correcciones realizadas el 26/11/2026.

Responsable: Kevin Maximiliano Palma Romero

| Modulo | Correcciones |
|--------|--------------|
| partida.py | La opcion Guardar y salir cierra la partida solo si se pudo guardar. Menu de pausa en maquina vs maquina (cada 50 turnos, avance de a un turno, guardar o salir), confirmacion antes de iniciar y limite de turnos segun el tamano del cubo (1100 con N = 8) con estadisticas |
| partida.py | Manejo de partidas guardadas danadas al cargarlas, salida con mensaje ante Ctrl+C o fin de la entrada y captura de errores del juego en el menu principal |
| partida.py | Reinicio de la ubicacion manual cuando una nave queda sin lugar, informe de la celda alcanzada por el torpedo guiado y revision de las vistas del cubo (despacho por diccionario y propagacion desde el centro o un origen elegido) |
| partida.py | Al terminar una partida se muestra el ranking, se avisa si esta danado y se ofrece exportar el reporte |
| registro.py | Validacion de los datos de las partidas guardadas, proteccion del archivo de ranking danado, exportacion de reportes y eliminacion de una funcion sin uso |
| flota.py | La carga conserva las celdas detectadas y recalcula las naves hundidas segun sus impactos. Verificacion de posiciones disponibles, eliminacion de alias sin uso y docstrings |
| tablero.py | Ajuste del recorrido en espiral (ubicado en radar.py) y de la validacion de tipos, y docstrings |
| radar.py / armamento.py | Docstrings faltantes |
| tablero.py / radar.py | Recorridos recursivos y su despacho ubicados en radar.py; tamano del cubo configurable en un unico lugar, con validacion de 7 a 15 |
| partida.py | Menu de turno en el orden de la consigna (3 - Guardar y salir), mensajes de impacto, sonar y turno de la maquina segun las muestras, validacion del arma, descuento de municion solo si la jugada se aplica, entrada no decodificable y nombres reservados de Windows |
| registro.py | El guardado devuelve la ruta escrita y no dana archivos existentes ante textos que no se pueden codificar; carga de flotas vacias y del historial identico al guardado |
| partida.py / registro.py / flota.py / armamento.py / radar.py / tablero.py | Declaracion de excepciones en los docstrings |
| tablero.py / radar.py / partida.py | Recorridos por capas de x y de y en tablero.py, registrados en el despacho de radar.py y disponibles como vistas 7 y 8 del cubo |
| tests | Actualizacion de pruebas y nuevas pruebas de regresion |
| .gitignore | Exclusion de ranking.json y exportaciones/ |
