# Sudoku · Laboratorio de algoritmos

Aplicación de escritorio en español para generar sudokus y experimentar con tus
propias estrategias de resolución. Python 3.12+ y Tkinter; sin paquetes externos.

## Preparar VS Code

Este equipo no tenía Python instalado globalmente. Durante el desarrollo se usó
el intérprete privado incluido con Codex:

`C:\Users\ejper\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

Ya se ha creado `.venv` dentro del proyecto con Python 3.12.14. La configuración
de `.vscode/settings.json` apunta a `.venv/Scripts/python.exe`, añade la raíz del
proyecto a las rutas de análisis y permite que Pylance resuelva imports y muestre
sugerencias.

Abre en VS Code la carpeta completa `Sudoku resolver`, no un archivo suelto. Instala
las extensiones recomendadas **Python** y **Pylance** si VS Code las propone. Si el
intérprete no se selecciona automáticamente:

1. Pulsa `Ctrl+Shift+P`.
2. Ejecuta `Python: Select Interpreter`.
3. Elige `.venv\Scripts\python.exe`.

Puedes recrear el entorno ejecutando `configurar_entorno.cmd`. No hay paquetes de
terceros que instalar. `pyproject.toml` declara Python 3.12 o posterior y ayuda al
editor a reconocer la estructura.

## Iniciar

En Windows puedes abrir **iniciar.cmd**. Primero utiliza el entorno `.venv` del
proyecto y conserva como respaldo el Python privado de Codex.
Con una instalación de Python con Tkinter:

```powershell
python main.py
```

Si Windows abre la tienda, instala Python con Tcl/Tk o utiliza `iniciar.cmd` en este
equipo. El lanzador no instala nada. Ventana mínima de 400 × 600 píxeles, con
contenido desplazable y una columna centrada también al maximizar.

## Navegación

1. **Inicio:** Generar sudoku, Escanear sudoku (deshabilitado), Historial,
   Benchmark y Salir. Debajo aparece la clasificación compacta del último
   benchmark de cada algoritmo. El eslogan es «Crea el mejor algoritmo».
2. **Dificultad:** selecciona un nivel, consulta su explicación y crea el tablero.
   «Volver» regresa al menú; si se está generando, cancela primero.
3. **Juego:** el tablero y la selección de algoritmo son los protagonistas.
   Ejecuta, pausa, continúa, avanza un paso o termina. El ritmo es fijo: una espera
   de 0,25 segundos entre eventos, la mitad de rápido que antes. La ayuda de
   dificultad sigue disponible. No hay selector de velocidad.
4. **Resumen:** al resolver, atascarse, cancelar o fallar aparece el tablero final,
   el estado y una tabla vertical de métricas. Verde indica logrado; rojo indica
   fallido (sin resolver, cancelado o error). «Reintentar» recupera las pistas del
   mismo sudoku. «Inicio» abandona el tablero, que ya no puede recuperarse.
   El historial global está disponible desde Inicio y desde el resumen.
5. **Benchmark:** ejecuta uno o todos los algoritmos sobre los mismos 40 casos y
   muestra la clasificación detallada. Puede cancelarse entre operaciones.

La interfaz utiliza botones redondeados, tonos suaves y un formato inspirado en
apps móviles. Sigue siendo una aplicación de escritorio. En ventanas pequeñas,
usa la rueda o RePág/AvPág para acceder al contenido: la barra lateral está oculta
y no ocupa ancho. Los botones
permiten navegación con Tab y activación con Enter o espacio.

## Tu primer algoritmo

Duplica `soluciones/s00_ejemplo.py`, cambia el nombre del archivo,
de la clase y de su
atributo `name`, y escribe `solve()`. Reinicia la aplicación: las clases concretas
se descubren automáticamente. Cada archivo utiliza el import absoluto mostrado
en el ejemplo siguiente.

```python
from sudoku.algorithm import SolvingAlgorithm

class MiEstrategia(SolvingAlgorithm):
    name = "Mi primera estrategia"
    description = "Aquí explico cómo pienso resolverlo."

    def solve(self):
        # self.board es tu matriz local: 0 representa una celda vacía.
        for fila in range(9):
            for columna in range(9):
                if self.board[fila][columna] == 0:
                    # Aquí desarrollas tu propio razonamiento.
                    pass
        # Cuando tengas un valor decidido:
        # yield self.place(fila, columna, valor, "Motivo opcional")
```

Este ejemplo puede terminar sin resolver. Esa situación es normal y se muestra
como «Sin resolver». La infraestructura de clasificación vive en `sudoku/logic.py`;
no necesitas modificarla ni usarla para escribir tus algoritmos.

### API del algoritmo

| Operación | Significado |
| --- | --- |
| `self.board` | Tu matriz local 9 × 9. Puedes leerla y crear tus propias estructuras de candidatos. |
| `yield self.place(fila, columna, valor, motivo)` | Coloca un número y anima el evento. |
| `yield self.place(fila, columna, 0, motivo)` | Borra una colocación durante un retroceso. |
| `solve()` | Método que implementas; produce los movimientos mediante `yield`. |

Los índices son enteros de 0 a 8; los valores son enteros de 0 a 9. `place`
construye el evento: el cambio ocurre al emitirlo con `yield`, antes de reanudar tu
método. No modifiques las pistas. Un número que no coincide con la solución
termina como error irreversible, aunque en ese momento no repita valores en su
fila, columna o caja. También fallan los movimientos que vulneran la estructura
del tablero. La validación ocurre fuera de `solve()`, por lo que no puedes capturar
el fallo con un `try/except` alrededor del `yield` ni usarlo para probar candidatos.
`place()` solo construye una acción y no devuelve si una jugada es correcta. La
solución de referencia nunca se entrega al algoritmo. La clase base no expone
candidatos, comprobadores, un objeto Sudoku ni un indicador de solución válida.
El cálculo de opciones te corresponde a ti; puedes guardar sus resultados en
atributos propios sin volver a construirlos en cada paso.

Cuando una colocación completa correctamente el sudoku, el ejecutor finaliza el
intento automáticamente; no necesitas detectar el tablero completo para salir de
`solve()`.

`self.board` se actualiza después de cada `yield self.place(...)`, antes de que
`solve()` continúe. Léelo libremente, pero no cambies sus números de forma directa:
la app detecta esa mutación y termina el intento. Así todas las modificaciones se
validan, se animan y se contabilizan.

No tienes que añadir contadores ni decoradores. El ejecutor mide automáticamente
las instrucciones de bytecode Python de `solve()` y de las funciones auxiliares
locales llamadas desde tu algoritmo. También mide el tiempo de cálculo. Esta medida
no demuestra la complejidad asintótica: es feedback empírico para comparar versiones
en el mismo Python y equipo.

Para la infraestructura interna del juego y el futuro OCR, `Sudoku` ofrece
`values()`, `value()`, `copy()`, `candidates()`, `can_place()`,
`set_value()`, `reset()`, `is_valid()`, `is_complete` e `is_solved`.
`is_correct()` requiere solución de referencia y es independiente de la legalidad
local. Las coordenadas inválidas lanzan `ValueError`; `set_value()` devuelve
`False` al rechazar valores o cambios de pistas. `is_complete` solo indica si está
lleno; `is_solved` exige además validez. Estas ayudas no forman parte del contrato
de los algoritmos. Python local no es un entorno aislado: no se impide que alguien
importe deliberadamente código interno, pero la API de aprendizaje no lo ofrece.

### Reproducción y cancelación

Ejecutar reinicia las pistas. Puedes pausar, avanzar un evento, continuar,
detener o reintentar. Solo hay una ejecución visible activa. Pausar
detiene la reproducción y las nuevas peticiones de avance; un cálculo de evento
ya iniciado puede acabar y quedar pendiente de mostrar.

El cálculo ocurre en un hilo. Detener descarta eventos pendientes y conserva el
tablero visible. Los bucles de Python atienden la cancelación automáticamente.
Una operación larga implementada dentro de una biblioteca nativa puede tardar en
responder hasta que devuelva el control a Python. No se intenta matar hilos ni
aislar código local de confianza.

Si una solución produce una excepción, la aplicación no se cierra: el intento se
marca como error en la interfaz y la terminal muestra el traceback completo con el
archivo y la línea que fallaron. Por eso, durante el desarrollo conviene iniciar
la aplicación desde la terminal integrada de VS Code.

### Métricas

- Pasos: movimientos emitidos y aceptados mediante `place()`. Son las acciones
  visuales del algoritmo.
- Operaciones Python: instrucciones de bytecode ejecutadas automáticamente por el
  algoritmo y sus ayudantes locales. No son instrucciones de CPU. El trabajo
  interno de funciones nativas no se desglosa y el valor puede cambiar al usar
  otra versión de Python.
- Colocaciones: números colocados. Los borrados siguen siendo acciones posibles
  para algoritmos con retroceso, pero no se muestran como métrica.
- Tiempo de cálculo: suma de tramos de `solve()`, excluyendo espera entre eventos,
  animación y pausas. En cancelación se conservan métricas de los eventos mostrados;
  un tramo aún en curso no se incluye. Incluye el pequeño coste del medidor de
  bytecode, aplicado por igual a todos los algoritmos.
- Tiempo total animado: desde pulsar Ejecutar hasta finalizar, incluidas la
  animación y las pausas manuales. Es el tiempo que has visto transcurrir; no es
  una estimación ni una segunda ejecución del algoritmo.
- Score: porcentaje de celdas inicialmente vacías con valor final correcto. No es
  una puntuación de velocidad. El acierto y la eficiencia se presentan separados.

El historial se guarda localmente en `data/attempts.sqlite3` y persiste al cambiar
de tablero o cerrar la app. Una tabla horizontal muestra algoritmo, fecha y hora
(hasta minutos), dificultad, resultado, porcentaje, pasos, operaciones,
colocaciones y los dos
tiempos; los intentos más recientes aparecen primero. Solo se guarda un resumen
por ejecución, no una grabación de cada movimiento. El tiempo de cálculo depende
del equipo y su carga. Se ha eliminado la métrica de comprobaciones.

El resumen incluye la dificultad después de fecha y hora. Los registros antiguos
sin dificultad muestran «—» y no participan en la tabla de mejores resultados.
No se inventa el nivel de esos intentos; el historial anterior se conserva.

## Benchmark

La vista Benchmark usa 40 casos guardados en `data/benchmark_suite.json`: diez por
dificultad. La suite se genera una sola vez, está versionada y se reutiliza para
que todos los algoritmos compitan sobre exactamente los mismos tableros. Puedes
ejecutar un algoritmo o todos; siempre se prueban las cuatro dificultades y no se
reproduce la animación.

Por algoritmo se muestran los porcentajes medios de Fácil, Intermedio, Difícil y
Extremo, la media global, pasos, operaciones, tiempo de cálculo y errores. La
clasificación ordena primero por mayor porcentaje global; en empate, por menos
operaciones y después por menor tiempo. El resultado más reciente de cada
algoritmo sustituye al anterior. Inicio muestra una versión compacta del ranking.

## Dificultad y generación

El generador retira pistas manteniendo solución única. Solo entrega un tablero
cuando el analizador confirma exactamente el nivel solicitado:

- Fácil: celdas con un único candidato.
- Intermedio: números que solo pueden ir en una celda de su fila, columna o bloque.
- Difícil: necesita además candidatos bloqueados o pares desnudos.
- Extremo: se atasca incluso con ese repertorio; mantiene solución única.

El analizador vuelve a las técnicas sencillas tras cada avance y usa un orden
determinista. El informe muestra técnicas, colocaciones, eliminaciones y celdas
pendientes. Las eliminaciones cuentan las técnicas explícitas de reducción, no
la retirada rutinaria de candidatos tras colocar un valor.

No es una escala universal; extremo no significa que haya que adivinar. Las pistas
no determinan la etiqueta. La generación tiene un máximo de 30 segundos y 100
intentos; si no encuentra un tablero muestra un error recuperable. Se puede
cancelar. Para experimentos reproducibles existe `generate(nivel, seed=...)`.
La diversidad se obtiene permutando una cuadrícula válida y retirando pistas;
no se pretende muestrear uniformemente todos los sudokus posibles.

## Futuro OCR

El botón está deshabilitado a propósito. Tu reconocimiento deberá devolver una
lista de nueve filas con nueve enteros cada una, usando 0 en vacíos. Construye un
`Sudoku(matriz)` y comprueba `is_valid()`; eso detecta conflictos locales, pero no
garantiza existencia o unicidad. `count_solutions()` sirve sobre pistas previamente
validadas para comprobar unicidad. La importación, corrección y obtención de una
solución de referencia se integrarán cuando desarrolles esta funcionalidad.

## Estructura y verificación

- `sudoku/`: modelo, generación, clasificación y ejecución.
- `soluciones/`: algoritmos del usuario; cada archivo válido se descubre al iniciar.
- `sudoku/algorithm.py`: contrato y medición interna de los algoritmos.
- `sudoku/discovery.py`: descubrimiento automático de `soluciones/`.
- `ui/`: interfaz Tkinter.
- `tests/`: invariantes, generación, métricas y recorrido gráfico.
- `docs/ESPECIFICACION.md`: alcance validado.
- `docs/PLAN.md`: planificación vinculada a requisitos.

```powershell
python -m unittest discover -v
```

Las pruebas gráficas abren brevemente una ventana y necesitan escritorio y
Tkinter. Las de generación verifican los cuatro niveles y pueden tardar unos
segundos. El juego manual y OCR funcional quedan fuera
de esta versión.
