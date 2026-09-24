# Plan de implementación

## Revisión 2.1

Reescribir el README como guía breve de instalación, arranque, uso y creación de
soluciones; incluir un ejemplo funcional de la API mínima y mantener los detalles
de implementación en la especificación.

## Revisión 2.0

Inicializar Git en `main`, ignorar todas las soluciones salvo el ejemplo y
desacoplar de ellas las pruebas de infraestructura. Corregir las referencias al
nombre actual del ejemplo, validar una copia publicable y subirla a un repositorio
público nuevo.

## Revisión 1.9

Entregar la solución de referencia únicamente al ejecutor interno y hacer que la
validación externa rechace cualquier número diferente, aunque sea legal por fila,
columna y bloque. Mantener la solución fuera de la instancia educativa, adaptar
benchmark y pruebas, y documentar el contrato estricto.

## Revisión 1.8

Centralizar la impresión del traceback de las excepciones recuperadas. Integrarla
en ejecución, descubrimiento, benchmark y tareas auxiliares sin propagar el fallo
ni cerrar la interfaz. Añadir pruebas sobre la salida de diagnóstico y actualizar
la documentación.

## Revisión 1.7

Mover soluciones existentes a un paquete raíz con nombres importables; trasladar
base y descubrimiento al núcleo; actualizar todos los imports, pruebas y textos.
Crear `.venv` desde el runtime de Codex y añadir configuración, recomendaciones y
lanzadores de VS Code. Verificar imports, descubrimiento, app y suite desde `.venv`.

## Revisión 1.6

Sustituir el contador manual por monitorización de instrucciones Python 3.12,
filtrada al módulo del algoritmo y sus ayudantes locales; integrar cancelación
automática, actualizar ejemplo, benchmark, textos y pruebas de medición sin llamadas
manuales. Documentar límites de bytecode, funciones nativas y sobrecoste medido.

## Revisión 1.5

1. Reducir la API pública a `board`, `place` y `solve`, con
   detección de mutaciones directas y métricas separadas de pasos/operaciones.
2. Crear y versionar una suite persistente de 10 casos por dificultad.
3. Implementar ejecución sin animación, agregación, cancelación y persistencia
   de resultados de benchmark.
4. Añadir la vista Benchmark y sustituir el resumen principal por su clasificación.
5. Adaptar ejemplo, documentación y pruebas del contrato, suite, ranking y UI.

## Revisión 1.4

Sustituir lectura pública de matriz por `get_value`, contar lecturas, adaptar
ejemplo y contrato documentado. Verificar coordenadas, cancelación, lectura tras
colocar/borrar y ejecución con solo lecturas. Incorporar eliminación del botón
redundante de ayuda en la especificación.

## Revisión 1.3 · Ejecutada

Separar menú y dificultad; simplificar textos; migrar historial añadiendo nivel
sin inferir datos antiguos; tabla de mejores resultados; adaptar resumen e historial.
Verificación del recorrido, migración conservadora y desempate por tiempo de cálculo.

## Revisión 1.2 · Ejecutada

1. Retirar ayudas del contrato de algoritmos y adaptar el ejemplo a razonamiento propio.
2. Fijar reproducción en 0,25 segundos y medir cálculo frente a duración total.
3. Ocultar barra lateral, abandonar tablero al volver y rehacer resumen como tabla.
4. Crear historial SQLite global con tabla horizontal, fecha y todos los contadores.
5. Verificar fallo irreversible, persistencia, navegación y métricas; actualizar documentación.

## Revisión 1.1 · Interfaz por vistas

1. Actualizar especificación con el cambio autorizado.
2. Separar presentación de control de ejecución; añadir componentes redondeados
   y un contenedor centrado con desplazamiento para ventanas pequeñas.
3. Construir inicio, juego y resumen; mover opciones y comparativa a vistas auxiliares.
4. Adaptar pruebas al recorrido entre vistas, conservación de resultados y tamaños.
5. Actualizar instrucciones y registro de verificación.

Base: especificación 1.0 validada. Orden de trabajo:

1. Corregir modelo y construir analizador determinista de singles, candidatos
   bloqueados y pares desnudos (RF-01/03; CA-02/03/05).
2. Generar eliminando pistas con unicidad y aceptar únicamente la categoría
   solicitada; añadir límites y cancelación (RF-02; CA-02/04).
3. Construir contrato de eventos, descubrimiento tolerante a errores y ejecución
   en segundo plano con métricas de cálculo independientes de la reproducción
   (RF-04/06; CA-06/09/10).
4. Crear interfaz Tkinter: selección, ayuda, tablero, reproducción, resultados y
   OCR pendiente (RF-05/07; CA-01/07/08).
5. Documentar la extensión y verificar núcleo y recorrido gráfico
   (RF-08; CA-11/12).

Decisiones: Python 3.12+, biblioteca estándar y Tkinter. Ejecución cooperativa
en un hilo con una petición por evento; la UI nunca ejecuta el algoritmo.
Una cancelación descarta sus eventos y libera los controles; los algoritmos
deben consultar `checkpoint()` en bucles largos para terminar el hilo.
Los hilos son daemon para no impedir cerrar la aplicación.

El analizador es infraestructura interna de generación. Solo se ofrece el
ejemplo mínimo de singles como complemento didáctico.

## Resultado

Los cinco pasos están implementados. Verificación registrada en
`docs/VERIFICACION.md`. OCR y las estrategias propias siguen como puntos de
extensión del usuario, conforme al alcance.
