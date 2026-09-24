# Especificación · Laboratorio de Sudoku

Versión: 2.0 · Estado: **revisiones solicitadas y autorizadas por el usuario**

### Revisión 2.0 · Distribución pública

El repositorio público contiene únicamente `soluciones/s00_ejemplo.py` y el
inicializador del paquete. Los demás archivos Python de `soluciones/` se consideran
trabajo personal del usuario: permanecen en su equipo y `.gitignore` evita que se
publiquen ahora o en commits futuros. Las pruebas del núcleo no dependen de esos
algoritmos privados y deben funcionar en una copia limpia del repositorio.

### Revisión 1.9 · Colocaciones estrictamente correctas

Cada número emitido mediante `yield self.place(...)` debe coincidir con el valor
de la solución única de referencia. No basta con que sea un candidato legal que
no produzca duplicados en ese momento. Una discrepancia termina inmediatamente
el intento como error y deja un traceback en la consola. La comprobación se hace
fuera de `solve()` y la solución no se entrega ni se expone al algoritmo, por lo
que el fallo no puede capturarse dentro del generador ni emplearse para probar
candidatos. El valor 0 continúa representando el borrado de una colocación propia.
Cuando una colocación completa correctamente el tablero, el ejecutor da por
terminado el algoritmo sin exigir que el generador del usuario haga `return`.

### Revisión 1.8 · Diagnóstico en consola

Los errores inesperados de una solución se seguirán capturando para que la
interfaz permanezca abierta y pueda mostrar el intento como error. Además, se
imprimirá en la consola el traceback completo, con el archivo y la línea de
origen. Este diagnóstico se aplica a la ejecución normal, la carga de soluciones
y los casos de benchmark. También se registrarán los fallos inesperados de
generación, preparación de una ejecución y persistencia del historial.

### Revisión 1.7 · Soluciones y entorno de desarrollo

Los algoritmos del usuario viven exclusivamente en el paquete raíz `soluciones/`.
La clase base y el descubrimiento son infraestructura interna de `sudoku/`. Cada
solución usa el import absoluto `from sudoku.algorithm import SolvingAlgorithm`;
los nombres de archivo deben ser identificadores Python válidos. Se conservan y
adaptan las tres soluciones existentes del usuario.

El proyecto requiere Python 3.12 por la medición automática. Debe incluir una
configuración de VS Code que seleccione `.venv/Scripts/python.exe`, configure la
raíz para el análisis, recomiende Python y Pylance, y permita iniciar app y pruebas.
Un script crea `.venv` usando primero el runtime privado de Codex y después una
instalación normal como alternativa. El proyecto no depende de que `python` esté
registrado globalmente en Windows.

### Revisión 1.6 · Medición automática

Se elimina `count_operation()`: el autor no instrumenta manualmente su estrategia.
El ejecutor cuenta automáticamente las instrucciones de bytecode Python ejecutadas
por `solve()` y por las funciones auxiliares locales a su módulo. Esta cifra se
muestra como **Operaciones Python**. Incluye bucles, accesos, comparaciones y demás
instrucciones interpretadas; no incluye el trabajo interno de funciones nativas
implementadas en C y puede cambiar entre versiones de Python. No representa
instrucciones de CPU ni demuestra la complejidad asintótica, pero permite feedback
repetible dentro de la misma versión y entorno.

La instrumentación es automática y no requiere decorador. También observa las
líneas de Python para atender una cancelación durante bucles largos. Una llamada
nativa que tarda mucho solo podrá interrumpirse cuando devuelva el control a
Python. El tiempo de cálculo incluye el pequeño coste de la instrumentación;
todos los algoritmos del benchmark se miden de la misma forma. La versión mínima
pasa a Python 3.12, que proporciona la API de monitorización usada.

La API educativa visible queda formada por `self.board`, `self.place()` y
`solve()`, además de `name` y `description`. Los pasos siguen siendo movimientos
aceptados, mientras que Operaciones Python mide el trabajo de cálculo automático.
Esta revisión prevalece sobre las referencias anteriores a operaciones declaradas.

### Revisión 1.5 · API mínima y benchmark

Esta revisión sustituye el contrato 1.4. Un algoritmo recibe una copia completa
del tablero en `self.board`, implementa `solve()` y comunica cambios mediante
`yield self.place(fila, columna, valor, motivo opcional)`. El valor 0 permite
borrar durante un retroceso. El tablero se actualiza después de aceptar cada
acción; el usuario puede construir y conservar sus propias estructuras de
candidatos sin consultar al modelo. No se exponen `get_value`, candidatos,
validadores, solución, notas, borrado separado ni comprobación final.

`self.count_operation(cantidad=1)` registra el coste lógico que el autor decida
medir —comparaciones, candidatos examinados, iteraciones u otra unidad estable—.
La cantidad debe ser un entero positivo. Este contador atiende también la
cancelación cooperativa. El tiempo de cálculo se mide automáticamente. La app
no puede deducir la complejidad asintótica de una sola ejecución; por ello se
presentan operaciones declaradas y tiempo medido, con su significado documentado.
Cada colocación aceptada continúa contando como un paso visual; las operaciones
son una métrica independiente. El tablero solo debe modificarse mediante `place`;
las mutaciones directas se detectan y terminan el intento como error.

Se añade una vista **Benchmark**, accesible desde Inicio. Existe un conjunto
versionado y persistente de 40 casos: 10 sudokus con solución única por cada
dificultad. Se crea una sola vez y se reutiliza en ejecuciones posteriores; puede
reconstruirse explícitamente si cambia su versión. El benchmark no reproduce
animaciones y ejecuta siempre las cuatro dificultades. Permite seleccionar un
algoritmo o todos los algoritmos descubiertos, muestra progreso y permite cancelar
cooperativamente.

Por algoritmo y dificultad se calcula la media de porcentaje completado, pasos,
operaciones declaradas y tiempo de cálculo sobre 10 casos. La puntuación global
es la media de los 40 porcentajes. La clasificación se ordena por puntuación
global descendente, después por operaciones medias ascendentes y tiempo medio
ascendente. Un error o sudoku sin resolver conserva el porcentaje alcanzado y
cuenta dentro de la media; un bloqueo no cooperativo queda sujeto a la limitación
ya documentada del código local de confianza.

Los resultados de benchmark se guardan localmente y la ejecución más reciente
de cada algoritmo sustituye su resultado anterior. Inicio muestra un resumen
compacto de esa clasificación —algoritmo, Fácil, Intermedio, Difícil, Extremo y
media— en lugar de los mejores intentos individuales. La vista Benchmark muestra
además operaciones, pasos, tiempo, fecha y cantidad de errores. Los intentos
animados y el historial normal permanecen independientes del benchmark.

### Revisión 1.4 · Lectura de celdas y pasos

El contrato del algoritmo sustituye la propiedad `board` por
`get_value(fila, columna)`: índices enteros 0–8, devuelve 0–9, con 0 para vacío.
Cada lectura válida cuenta un paso, incluidas lecturas repetidas. No requiere
`yield`, no genera animación ni espera. Las coordenadas inválidas lanzan error
sin sumar pasos. Colocaciones, borrados y notas aceptados siguen sumando un paso.
`checkpoint()` únicamente atiende cancelación y no suma pasos; se invoca también
desde la lectura. La validación del sudoku sigue fuera de la API del algoritmo.

Las lecturas se reflejan en las métricas del siguiente evento o al finalizar.
Los intentos anteriores se conservan, pero sus pasos no incluían lecturas.
Esta definición prevalece sobre los apartados anteriores que definían pasos
únicamente como eventos visuales. El ejemplo y la documentación usan la nueva API.

Se incorpora asimismo el ajuste de interfaz pendiente de documentación: la vista
de dificultad muestra su explicación al seleccionar nivel, sin el botón redundante
«Qué significa este nivel».

### Revisión 1.3 · Menú, lenguaje y mejores resultados

Esta revisión prevalece sobre las anteriores. Inicio contiene «Generar sudoku»,
«Escanear sudoku» (botón gris deshabilitado), «Historial» y «Salir». El eslogan es
«Crea el mejor algoritmo». Después de Salir aparece una tabla de tres columnas:
Dificultad, Algoritmo y Resultado; cuatro filas, una por dificultad. Se elige el
mayor porcentaje y, en empate, el menor tiempo de cálculo; en empate total el
intento más reciente. Sin intentos se muestra «—».

Generar sudoku abre una vista independiente con selección, explicación sencilla,
acción de generación y Volver. La ayuda evita jerga y avisos genéricos sobre la
escala de dificultad. Durante la generación se puede cancelar antes de volver.

El resumen muestra el porcentaje solo, el estado sin prefijo «Fallido», y la
dificultad después de fecha y hora. Se eliminan las notas del último movimiento,
las aclaraciones de tiempos y la métrica visible de borrados. Se conserva el
detalle de errores reales. El historial también incluye dificultad y omite
borrados; el almacenamiento antiguo se preserva. Registros anteriores sin nivel
no participan en la tabla por dificultad y muestran «—» en historial.

### Revisión 1.2 · Contrato de aprendizaje, tiempos e historial

Esta revisión prevalece sobre los requisitos anteriores que contradiga:

- Ritmo fijo con 0,25 segundos de espera entre eventos (antes 0,125). Se elimina
  cualquier selector de velocidad.
- Desplazamiento sin barra lateral visible ni espacio reservado para ella;
  rueda, RePág/AvPág y navegación por foco siguen disponibles.
- Volver a Inicio abandona el tablero. Se elimina «Volver a mi tablero». Si hay
  ejecución activa, se registra como cancelada antes de abandonar.
- La clase base de algoritmo solo proporciona matriz y emisión de acciones,
  cancelación cooperativa y métricas. No ofrece candidatos, validación, corrección
  ni estado de resolución. Se elimina el contador de comprobaciones.
- Un `yield self.place(...)` inválido detiene definitivamente el intento como
  error. La validación está fuera del método del usuario y no se puede usar como
  consulta mediante captura de excepciones dentro de `solve()`. Las reglas
  internas del modelo permanecen para el juego, no como API del algoritmo.
- Resultado en tabla vertical: algoritmo, fecha/hora, estado, completado, pasos,
  colocaciones, borrados, tiempo de cálculo y tiempo total animado. El cálculo
  excluye las esperas añadidas por el reproductor; el total incluye todo el tiempo
  desde Ejecutar hasta terminar, incluidas pausas manuales.
- Éxito en verde, cualquier finalización sin resolver en rojo, con estado textual
  que distingue cancelación, atasco y error. Botones «Reintentar» e «Inicio».
- Historial global persistente local, accesible en Inicio y Resultado. Tabla
  horizontal con las mismas métricas, fecha/hora hasta minutos, más reciente
  primero. Sustituye la comparación limitada al sudoku actual. No almacena
  una traza de movimientos ni permite recuperar tableros abandonados.

Criterios: comprobar ausencia de API de ayudas y selector de velocidad, error
irreversible ante movimiento inválido, tiempos separados, abandono del tablero,
colores/etiquetas, persistencia y orden del historial entre partidas y sesiones.

### Revisión 1.1 · Navegación y diseño

La interfaz se divide en tres vistas, sustituyendo el panel único descrito en la
primera versión. Este cambio ha sido solicitado y autorizado por el usuario.

- **Inicio:** composición centrada, cuatro botones de dificultad seleccionables,
  ayuda de dificultad, generar y salir. Escaneo queda como opción pendiente.
  Durante la generación se muestra progreso y cancelación en esta vista.
- **Juego:** tablero protagonista, selección de algoritmo y controles de
  reproducción. Sin tabla de resultados ni métricas detalladas simultáneas.
  Velocidad e informe de dificultad quedan en opciones secundarias.
- **Resumen:** conserva el tablero final —también si queda incompleto— y muestra
  estado, score, pasos, colocaciones, borrados, comprobaciones y tiempo. Permite
  probar otro algoritmo en el mismo tablero o volver al inicio. Las comparativas
  de la partida se consultan bajo demanda.

Estética inspirada en aplicaciones móviles: columna de contenido limitada y
centrada, tarjetas y botones redondeados, fondos suaves, espacios y jerarquía
tipográfica clara. Sigue siendo una aplicación de escritorio Python/Tkinter.
La ventana admite un formato estrecho y contenido desplazable cuando no cabe.
La navegación no debe perder los resultados del tablero actual ni dejar una
ejecución activa al volver al inicio. Los requisitos funcionales del núcleo se
mantienen; esta revisión prevalece sobre descripciones anteriores de distribución.

Criterios adicionales: solo una vista principal visible; dificultad seleccionada
indicada con texto y estilo; ninguna métrica detallada en juego; resumen automático
para resuelto/sin resolver/cancelado/error; controles accesibles en ventana estrecha.

Este documento define el alcance y el comportamiento esperado. No es un plan de
implementación. Las decisiones técnicas se concretarán después de su aprobación.

## 1. Objetivo

Crear un juego de escritorio en Python que sirva como laboratorio de aprendizaje:
generar sudokus, desarrollar algoritmos propios, observar su ejecución sobre el
tablero y comparar sus resultados.

El usuario quiere programar principalmente las estrategias de resolución y, más
adelante, la lectura de sudokus mediante OCR o visión. La base del proyecto debe
permitirle hacerlo sin tener que desarrollar la interfaz, las animaciones, las
métricas o el generador.

## 2. Acuerdo de trabajo con SDD

1. Revisar y validar esta especificación.
2. Después de la validación, preparar la planificación y los pasos de trabajo,
   vinculados a los requisitos y criterios de aceptación de este documento.
3. Implementar y verificar el alcance aprobado.

Cualquier ampliación material se reflejará en la especificación antes de
implementarse. Los detalles internos que no alteren el comportamiento acordado
podrán decidirse durante la planificación.

Antes de este acuerdo se crearon archivos preliminares en `sudoku/`, `algorithms/`,
`main.py` y `README.md`. Son borradores sin validar: no condicionan las decisiones
de esta especificación y no constituyen una aplicación terminada. Su continuidad
se evaluará tras la aprobación. No se seguirá implementando durante la revisión.

## 3. Alcance de la primera versión

- Sudoku clásico de 9 × 9, con números del 1 al 9 y regiones de 3 × 3.
- Aplicación local de escritorio escrita en Python, con interfaz en español.
- Selección y generación en cuatro niveles: fácil, intermedio, difícil y extremo.
- Generación con solución única y explicación verificable de la dificultad.
- Tablero visual para observar la resolución.
- Carpeta de algoritmos propios, con un contrato común y descubrimiento automático.
- Ejecución animada, controles de reproducción y resultados medibles.
- Punto de extensión documentado para incorporar OCR posteriormente.
- Documentación suficiente para escribir el primer algoritmo sin conocer la UI.

### Fuera del alcance

- Implementar OCR, visión, selección de imágenes o captura de pantalla.
- Desarrollar un catálogo de algoritmos de resolución para el usuario.
- Variantes como sudoku diagonal, killer, irregular o tableros de otro tamaño.
- Cuentas, servicios remotos, multijugador, publicación o aplicación móvil.
- Editor manual, modo de juego manual completo, guardado de partidas e historial
  persistente de comparativas.
- Clasificaciones universales de dificultad o puntuaciones comparables con otras apps.

Se incluirá únicamente un ejemplo mínimo de integración, claramente identificado
como didáctico, que puede detenerse sin resolver el tablero. La lógica interna
necesaria para generar, comprobar unicidad y clasificar no será presentada como
una colección de algoritmos del usuario.

## 4. Recorrido de uso

1. El usuario abre la aplicación y encuentra las opciones «Generar sudoku» y
   «Escanear sudoku». La segunda aparece deshabilitada y explica que está pendiente
   de implementación por el usuario.
2. Selecciona una dificultad. Una interrogación permite consultar su definición,
   las técnicas contempladas y los límites de la clasificación.
3. Solicita un tablero. La aplicación muestra que está generando y mantiene la
   interfaz operativa.
4. Se muestra el sudoku, su dificultad verificada y los algoritmos disponibles.
5. El usuario selecciona un algoritmo, consulta su descripción y lo ejecuta.
6. Observa los cambios animados y sus explicaciones, pudiendo pausar, avanzar un
   paso, continuar, cambiar la velocidad o detener la ejecución.
7. Al terminar, ve el resultado y las métricas. Puede reiniciar el mismo sudoku y
   probar otro algoritmo en las mismas condiciones, o generar uno nuevo.

## 5. Requisitos funcionales

### RF-01 · Modelo del sudoku

La clase de dominio debe ofrecer:

- Lectura de la matriz y de una celda; el cero representa una celda vacía.
- Identificación de las pistas iniciales, que permanecen inmutables.
- Consulta de candidatos legales por fila, columna y región.
- Colocación y borrado de valores en celdas editables.
- Reinicio al estado inicial y copia independiente para una ejecución.
- Estado de tablero completo y estado de tablero válido por separado.
- Comprobación de si un movimiento respeta las reglas locales.
- Comprobación opcional de coincidencia con la solución conocida, diferenciada
  de la legalidad local: un valor puede respetar las reglas y ser incorrecto.

Se documentarán índices, tipos y errores de entrada. Un tablero lleno con
conflictos no se considerará resuelto. El estado de dominio será utilizable sin
abrir una ventana; las animaciones se producirán al comunicar movimientos a la UI.

### RF-02 · Generación y unicidad

Cada sudoku aceptado por el generador debe tener pistas válidas, al menos una
celda vacía y exactamente una solución. La comprobación de unicidad será explícita.

La generación podrá producir tableros diferentes para una misma dificultad.
El generador devolverá el tablero inicial, la solución y un informe de
clasificación. La solución de referencia no formará parte de la API pública
entregada a los algoritmos del usuario.

Si no se consigue un tablero de la dificultad solicitada dentro de un límite de
intentos o tiempo, se informará de ello y se permitirá reintentar. No se entregará
silenciosamente un tablero de otra categoría. Se podrá cancelar la generación.

### RF-03 · Dificultad explicable

Los nombres de dificultad son categorías de este proyecto. La cantidad de pistas
se mostrará como información, pero no bastará para determinar la dificultad.

Se propone el siguiente clasificador determinista, que intenta las técnicas en
orden creciente y vuelve a las más sencillas tras cada avance:

| Nivel | Condición de clasificación |
| --- | --- |
| Fácil | El analizador resuelve el tablero usando solo celdas con un único candidato —singles desnudos—. |
| Intermedio | El nivel anterior se atasca, pero se resuelve añadiendo singles ocultos: un número solo puede ir en una celda de una fila, columna o región. |
| Difícil | Los niveles anteriores se atascan, pero se resuelve añadiendo candidatos bloqueados y pares desnudos. |
| Extremo | El analizador con todas las técnicas anteriores se atasca, aunque se ha verificado que el tablero tiene solución única. |

«Extremo» significa que el tablero excede el repertorio de este analizador; no
afirma que sea necesario adivinar, ni identifica una técnica avanzada que no se
haya comprobado. La clasificación describe una ruta de análisis reproducible,
no una medida absoluta del esfuerzo de cualquier persona o algoritmo.

El informe incluirá número de pistas, técnicas usadas, número de colocaciones y
eliminaciones de candidatos, y si el analizador terminó o quedó bloqueado. No
llamará «suposiciones» al número de celdas pendientes.

La interrogación de cada dificultad explicará sus reglas con lenguaje sencillo.
Para un tablero concreto también se podrá consultar la evidencia de su categoría.

### RF-04 · Contrato de algoritmos y extensibilidad

Una clase base centralizará el acceso al tablero y las métricas. Cada algoritmo
aportará nombre, descripción y un método de resolución.

El usuario podrá añadir un archivo a una carpeta documentada y una clase que
cumpla el contrato. Al reiniciar la aplicación aparecerá como opción sin editar
la interfaz ni un registro central. Un archivo defectuoso no impedirá cargar los
demás: se mostrará un diagnóstico comprensible.

El algoritmo trabajará con una copia del tablero y emitirá eventos de avance
mediante una API sencilla. Se admitirán colocación, borrado —necesario para
retroceso— y eventos informativos sin cambiar valores. Cada evento podrá incluir
una explicación. El contrato documentará cómo registrar comprobaciones propias
y cómo colaborar con las órdenes de pausa y cancelación.

El algoritmo podrá explorar valores legalmente posibles sin que se le exija
coincidir inmediatamente con la solución final. Las entradas mal formadas, los
cambios de pistas y los movimientos que violen reglas se comunicarán como errores;
no se presentarán como una resolución correcta.

### RF-05 · Ejecución y animación

- Solo habrá una ejecución activa por partida.
- Cada ejecución comenzará desde las mismas pistas iniciales.
- Se distinguirán visualmente las pistas de los valores del algoritmo y se
  resaltará la celda modificada más recientemente.
- Se mostrará la explicación del último evento cuando exista.
- Habrá ejecutar, pausar/continuar, avanzar un evento, detener y reiniciar.
- La velocidad de animación será ajustable sin alterar las métricas de cómputo.
- El tablero parcial permanecerá visible al detenerse, atascarse o producirse un error.
- Los controles impedirán mezclar eventos de una ejecución anterior con otra.
- La interfaz no se bloqueará durante la generación ni durante el cálculo normal.

La ejecución termina con uno de estos estados: resuelto, finalizado sin resolver,
cancelado o error. «Resuelto» exige tablero completo y válido, verificado por el
sistema, y no solo una afirmación del algoritmo.

La cancelación de código propio deberá tener un comportamiento documentado.
La primera versión no pretende aislar código malicioso; los algoritmos locales
son código de confianza del usuario.

### RF-06 · Métricas y resultado

Cada ejecución mostrará:

- Eventos o pasos emitidos, incluidas las acciones informativas.
- Colocaciones y borrados, contados por separado.
- Comprobaciones: consultas instrumentadas a ayudas del modelo y operaciones
  adicionales registradas explícitamente por el algoritmo.
- Tiempo de cálculo del algoritmo, excluyendo pausas, espera de animación y
  renderizado de la interfaz.
- Porcentaje de celdas inicialmente vacías que terminan correctas respecto a la
  solución de referencia.
- Estado final y detalle del error, si lo hay.

El «score» propuesto será ese porcentaje de acierto, de 0 a 100. La eficiencia se
examinará con las métricas de trabajo y tiempo mostradas al lado; no se mezclarán
en una fórmula arbitraria. Resolver el sudoku con más pasos no restará acierto.

El contador de comprobaciones no se presentará como todas las operaciones de
Python: su significado depende de que los algoritmos instrumenten el trabajo de
forma comparable. El tiempo es una medición local y puede variar entre ejecuciones.

Se conservarán en pantalla los resultados de las ejecuciones de la partida actual
para comparar algoritmos sobre el mismo tablero. Se limpiarán al generar otro.

### RF-07 · Preparación del OCR

Se documentará el formato de entrada que una futura función de reconocimiento
deberá devolver: matriz 9 × 9 con enteros 0–9. La incorporación posterior reutilizará
la validación del modelo. Esta versión no leerá imágenes ni incluirá dependencias
de OCR. No se diseñará todavía un flujo completo de reconocimiento y corrección.

### RF-08 · Documentación y ejemplo

La documentación describirá cómo ejecutar el proyecto, añadir un algoritmo,
consultar candidatos, emitir movimientos, registrar comprobaciones, interpretar
resultados y usar pausas/cancelación. Incluirá el significado exacto de dificultad
y score, así como los límites conocidos.

El ejemplo mínimo demostrará la integración y el caso de finalización sin
resolver. No se implementarán por adelantado las estrategias que el usuario
quiere desarrollar como ejercicio.

## 6. Requisitos no funcionales

- Separación entre modelo, generación/clasificación, ejecución de algoritmos y UI.
- Código legible y documentado, priorizando facilidad de aprendizaje.
- Funcionamiento local sin servicios externos ni claves.
- Compatibilidad inicial con Windows y versión de Python documentada.
- Biblioteca gráfica y dependencias mínimas a decidir en la planificación;
  Tkinter es una propuesta preliminar, no una decisión validada.
- Mensajes de error visibles y recuperables sin perder toda la sesión.
- No se dependerá solo del color para comunicar estados.
- Verificación automatizada de invariantes del modelo, unicidad, clasificación,
  contrato de algoritmos y métricas; comprobación del recorrido de la interfaz.

## 7. Criterios de aceptación

| ID | Evidencia esperada |
| --- | --- |
| CA-01 | La aplicación se inicia siguiendo las instrucciones y muestra generación y escaneo pendiente. |
| CA-02 | Para cada nivel, los tableros aceptados tienen solución única y cumplen exactamente su criterio de clasificación. |
| CA-03 | La ayuda de dificultad describe el criterio implementado y el informe del tablero lo respalda. |
| CA-04 | Un límite de generación o una cancelación no produce un tablero mal etiquetado ni bloquea la ventana. |
| CA-05 | El modelo protege pistas, valida entradas y distingue legalidad local, corrección, completitud y resolución válida. |
| CA-06 | Añadir un algoritmo en la carpeta basta para descubrirlo al reiniciar; un complemento defectuoso no bloquea los demás. |
| CA-07 | Colocaciones, borrados y explicaciones se reproducen en orden; pausa, paso, velocidad y detención funcionan. |
| CA-08 | Repetir con otro algoritmo empieza con las mismas pistas y mantiene los resultados comparables de la partida. |
| CA-09 | Resuelto, sin resolver, cancelado y error se distinguen correctamente. |
| CA-10 | Un algoritmo de prueba con acciones conocidas produce contadores y score esperados; introducir pausas no aumenta el tiempo de cálculo medido. |
| CA-11 | La documentación permite crear un algoritmo sin modificar la interfaz y explica cómo conectar el futuro OCR. |
| CA-12 | No se incluye OCR funcional ni una colección de solucionadores que sustituya el trabajo de aprendizaje del usuario. |

## 8. Puntos propuestos para validar

La revisión debe confirmar especialmente:

- Las cuatro dificultades basadas en el repertorio lógico descrito, con «extremo»
  definido como límite del analizador.
- El score como porcentaje de acierto, acompañado de métricas de eficiencia.
- El ejemplo didáctico mínimo y los controles de ejecución incluidos.
- La observación de algoritmos como foco inicial, dejando el juego manual completo
  y el historial persistente fuera de esta versión.

El usuario ha validado esta especificación y autorizado la planificación e implementación.
