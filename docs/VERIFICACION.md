# Verificación de la versión inicial

## Revisión 2.0

**21 pruebas correctas.** El índice de Git contiene `s00_ejemplo.py`, pero no las
soluciones personales `s01`–`s05`, el historial SQLite, `.venv` ni cachés. Las
pruebas usan solucionadores internos y pasan sin depender de archivos ignorados.
También se comprobó el índice en busca de credenciales habituales sin encontrar
coincidencias y `git diff --cached --check` no detectó errores de formato.

## Revisión 1.9

**21 pruebas correctas.** Se probó expresamente un `2` legal en la posición
`(0, 0)` de un tablero vacío cuya solución exige `1`: el intento devuelve «Valor
incorrecto», no actualiza el tablero y no ejecuta el código posterior al `yield`.
La instancia educativa no contiene atributos `solution` ni `_solution`. También
se comprobó que el ejecutor termina automáticamente al aceptar la última celda.

## Revisión 1.8

**21 pruebas correctas.** Un fallo intencionado de una solución produce en
`stderr` un encabezado contextual y el traceback con archivo, línea y excepción;
al mismo tiempo, el ejecutor devuelve un resultado de tipo error y mantiene vivo
el proceso. También se verificó que un módulo que falla al cargarse deja el
diagnóstico en consola sin ocultar las demás soluciones.

## Revisión 1.7

Se creó `.venv` con Python 3.12.14 a partir del runtime privado de Codex. VS Code
tiene instaladas las extensiones `ms-python.python` y `ms-python.vscode-pylance`;
el workspace selecciona el intérprete local y añade su raíz al análisis.

Los tres archivos existentes se conservaron y trasladaron a `soluciones/` con
nombres de módulo válidos. La base y el descubrimiento pasaron a `sudoku/` y se
eliminó la carpeta antigua después de comprobar que no quedaban fuentes dentro.
Desde `.venv`, la compilación completa no produce errores, el descubrimiento
encuentra «Ejemplo: candidato único», «RandomFiller» y
«CheckAvailablesRandomSelect», la app abre en Inicio y las **21 pruebas pasan**.

## Revisión 1.6

**21 pruebas correctas.** Se verifica que un algoritmo sin ninguna llamada de
instrumentación obtiene Operaciones Python, que un cálculo sin movimientos tiene
operaciones pero cero pasos, que la API pública ya no contiene el contador manual
y que la cancelación alcanza automáticamente un bucle instrumentado.

Se recalculó el benchmark real de los dos algoritmos descubiertos para reemplazar
los resultados obtenidos con la métrica manual anterior. Ambos ejecutaron una
media de 39.444,4 instrucciones Python por caso; sus tiempos guardados incluyen
la instrumentación automática, como especifica la documentación.

## Revisión 1.5

Suite completa: **21 pruebas correctas**.
Se cubren la API mínima, coste declarado, rechazo de mutaciones directas, ejecución
sin eventos, creación/reutilización/cancelación de la suite, ranking, sustitución
del último resultado, ejecución individual y conjunta, y resumen en Inicio.

Se creó `data/benchmark_suite.json` con 40 casos distintos. La verificación real
confirma 10 casos por dificultad, categoría correcta y solución única en los 40.
Se ejecutó el benchmark inicial sobre los dos algoritmos descubiertos. La apertura
real confirma dos filas de ranking y los 40 casos cargados. También se
revisaron capturas de Inicio, Benchmark y Resumen con la nueva métrica Operaciones.

## Revisión 1.3

Tres pruebas dirigidas correctas: centrado inicial/redimensionado, recorrido
menú → dificultad → juego → resumen y migración del historial con clasificación
de mejores resultados. Se comprueban botón de escaneo deshabilitado, cuatro filas
de resultados, dificultad en el resumen, ausencia de borrados y notas de movimiento,
y estado «Sin resolver» sin prefijos. La migración conserva registros anteriores
sin asignarles una dificultad inventada.

## Corrección de centrado inicial

Se reprodujo un desplazamiento horizontal de 50 píxeles antes de redimensionar.
El área desplazable ahora abarca todo el ancho de la ventana y mantiene su origen
horizontal en cero. La prueba gráfica verifica centrado al abrir, al cambiar entre
400, 620 y 900 píxeles de ancho y al desplazar el contenido. También se cancela el
temporizador de actualización al cerrar para evitar callbacks de ventanas destruidas.

## Revisión 1.2

Suite completa: **11 pruebas correctas**. Cubre API sin candidatos ni validadores,
error de colocación que detiene la ejecución fuera del generador del usuario,
historial persistente ordenado incluso con fechas iguales, ausencia de selector
de velocidad y barra lateral, abandono de tablero, tabla de resultados y colores.
El recorrido gráfico comprueba que tiempo total animado supera al cálculo y que
el historial horizontal contiene todos los intentos con el más reciente primero.
Se revisó una captura del nuevo resumen vertical. Las capturas ilustrativas y
las pruebas usan bases de datos temporales, sin contaminar el historial real.

El cálculo conserva la medición entre eventos de la versión anterior. La nueva
duración total usa un reloj monotónico desde el inicio al resultado; incluye
pausas manuales por definición y se guarda en una columna independiente.

## Revisión de interfaz 1.1

Se adaptó la prueba gráfica a inicio → juego → resumen. Verifica selección por
botones, una sola vista visible, tablero final visible, reinicio sobre las mismas
pistas, cancelación y conservación de tres intentos. También prueba el ancho
mínimo de 400 píxeles y el regreso del inicio al resumen.

Se revisaron capturas reales de las tres vistas a 620 × 760. Se ajustaron tamaño
y centrado del tablero, espaciado y métricas. `tests/preview_ui.py` permite
reproducir las capturas en `artifacts/`; usa Pillow únicamente para esta revisión,
no como dependencia de la aplicación. Los números de la captura de resumen son
datos ilustrativos de la herramienta de vista previa.

La disposición anterior y sus medidas mínimas quedan sustituidas por esta revisión.

Entorno: Windows, Python del entorno local de Codex, Tkinter 8.6.

Se ejecutó `python -m unittest discover -v`: 8 pruebas correctas. Después del
ajuste del tamaño de ventana se repitió la prueba gráfica.

| Cobertura | Evidencia |
| --- | --- |
| CA-01/07/08/09 | Integración con ventana real: generación, paso, pausa, continuar, resuelto, reinicio, cancelación, sin resolver y conservación de resultados. |
| CA-02/03 | Generación de las cuatro categorías con semilla 12, unicidad y clasificación reproducible; difícil utiliza eliminaciones y extremo queda bloqueado. |
| CA-04 | Cancelación previa y tiempo límite generan sus estados de salida sin devolver otro nivel. |
| CA-05 | Protección de pistas, tipos, índices, copias y distinción entre completo, válido y correcto. |
| CA-06 | Un error de importación simulado no impide descubrir el ejemplo válido. |
| CA-09/10 | Ejecutor detecta un movimiento inválido; secuencia de eventos conocida verifica contadores y score. Reloj simulado verifica exclusión de espera. |
| CA-11/12 | README documenta API y futura matriz OCR; solo se incluye el ejemplo mínimo de singles. |

La comprobación gráfica automatizada verifica que el historial es visible,
incluido el tamaño mínimo. No sustituye una evaluación visual humana del diseño.

Límites explícitos: generación con límite de tiempo e intentos, clasificación
relativa al repertorio descrito y cancelación cooperativa para código propio.
La muestra de generación prueba las categorías, no garantiza un tiempo máximo
de éxito para todas las semillas; el límite se trata como resultado recuperable.
