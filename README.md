# Sudoku Studio

Aplicación de escritorio para generar sudokus, ejecutar tus propios algoritmos de
resolución y comparar sus resultados.

## Requisitos

- Windows.
- Python 3.12 o posterior con Tkinter.
- No requiere paquetes externos.

## Preparación

Clona el repositorio y entra en su carpeta:

```powershell
git clone https://github.com/emilio-devs/sudoku-resolver.git
cd sudoku-resolver
```

Abre esa carpeta completa en VS Code y ejecuta una vez:

```powershell
.\configurar_entorno.cmd
```

Esto crea el entorno local `.venv`. Si VS Code no lo selecciona automáticamente:

1. Pulsa `Ctrl+Shift+P`.
2. Busca `Python: Select Interpreter`.
3. Elige `.venv\Scripts\python.exe`.

## Iniciar la aplicación

Abre:

```powershell
.\iniciar.cmd
```

También puedes iniciarla desde una terminal:

```powershell
.\.venv\Scripts\python.exe main.py
```

Conviene utilizar la terminal mientras desarrollas: si un algoritmo falla, la
interfaz permanece abierta y el error completo aparece en la consola.

## Uso

1. Pulsa **Generar sudoku**.
2. Selecciona una dificultad y crea el tablero.
3. Elige uno de los algoritmos encontrados en `soluciones/`.
4. Usa **Ejecutar** para reproducirlo o **Un paso** para avanzar movimiento a
   movimiento.
5. Al terminar se muestran el resultado, el porcentaje completado, los pasos, las
   operaciones medidas y los tiempos.

Desde Inicio también puedes consultar el historial o ejecutar el benchmark. El
benchmark prueba cada algoritmo con los mismos diez sudokus de cada dificultad.
El escaneo de imágenes todavía no está implementado.

## Crear una solución

Crea un archivo `.py` dentro de `soluciones/`. Su nombre debe ser válido en Python,
por ejemplo:

```text
soluciones/s01_mi_algoritmo.py
```

Cada archivo debe contener una clase que herede de `SolvingAlgorithm`. El ejemplo
solo prueba un número aleatorio en la primera celda vacía; muestra cómo conectar
un algoritmo sin regalar una estrategia de resolución:

```python
import random

from sudoku.algorithm import SolvingAlgorithm


class MiAlgoritmo(SolvingAlgorithm):
    name = "Ejemplo aleatorio"
    description = "Prueba un número aleatorio."

    def solve(self):
        for fila in range(9):
            for columna in range(9):
                if self.board[fila][columna] == 0:
                    numero = random.randint(1, 9)
                    yield self.place(
                        fila,
                        columna,
                        numero,
                        "Número aleatorio",
                    )
                    return
```

Este ejemplo normalmente fallará porque no intenta descubrir el valor correcto.
Su única finalidad es enseñar la estructura y dejar la estrategia en tus manos.

Reinicia la aplicación después de crear o modificar un archivo para que vuelva a
descubrir las soluciones.

### API disponible

| Elemento | Uso |
| --- | --- |
| `self.board` | Matriz local 9 × 9. `0` representa una celda vacía. |
| `self.place(fila, columna, valor, motivo)` | Crea un movimiento. Debe emitirse con `yield`. |
| `solve()` | Método generador donde implementas tu estrategia. |
| `name` | Nombre mostrado en la interfaz. |
| `description` | Explicación breve del algoritmo. |

Las filas y columnas utilizan índices del `0` al `8`. Puedes leer `self.board` y
crear todas las funciones o estructuras auxiliares que necesites, pero no debes
modificar la matriz directamente. Después de cada `yield self.place(...)`, el
tablero se actualiza antes de que `solve()` continúe.

La aplicación comprueba cada colocación fuera de tu algoritmo. Si el número no
coincide con la solución, el intento termina como error; no puede utilizarse
`place()` para ir probando candidatos. La medición de operaciones y tiempo es
automática: no necesitas añadir contadores ni decoradores.

## Ejecutar las pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -v
```

Las pruebas de interfaz abren una ventana brevemente.
