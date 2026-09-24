import random
import time
from dataclasses import dataclass
from threading import Event
from .logic import DifficultyReport, analyze
from .model import Grid
from .solver_utils import count_solutions

DIFFICULTIES = {
    'Fácil': 'Se resuelve buscando celdas con un único candidato.',
    'Intermedio': 'También hay que buscar números que solo pueden ir en una celda de una fila, columna o bloque.',
    'Difícil': 'Hay que descartar opciones comparando grupos de celdas. Por ejemplo, si dos celdas solo admiten los mismos dos números, esos números se descartan en las demás celdas de su grupo.',
    'Extremo': 'Requiere deducciones más complejas que las anteriores. El analizador básico no consigue completarlo.',
}

@dataclass(frozen=True)
class GeneratedSudoku:
    puzzle: Grid
    solution: Grid
    report: DifficultyReport

class GenerationCancelled(Exception):
    pass

class SudokuGenerator:
    def generate(self, difficulty_name, *, cancel=None, timeout=30, max_attempts=100, seed=None):
        if difficulty_name not in DIFFICULTIES:
            raise ValueError('Dificultad desconocida.')
        cancel = cancel or Event()
        deadline = time.perf_counter()+timeout
        rng = random.Random(seed)
        def checkpoint():
            if cancel.is_set():
                raise GenerationCancelled()
            if time.perf_counter() >= deadline:
                raise TimeoutError('No se encontró un tablero del nivel solicitado. Prueba de nuevo.')
        for _ in range(max_attempts):
            checkpoint()
            groups = lambda: rng.sample(range(3),3)
            rows = [g*3+i for g in groups() for i in groups()]
            cols = [g*3+i for g in groups() for i in groups()]
            digits = rng.sample(range(1,10),9)
            solution = [[digits[(r*3+r//3+c)%9] for c in cols] for r in rows]
            puzzle = [row[:] for row in solution]
            for r,c in rng.sample([(r,c) for r in range(9) for c in range(9)],81):
                checkpoint()
                old = puzzle[r][c]
                puzzle[r][c] = 0
                if count_solutions(puzzle,checkpoint=checkpoint)!=1:
                    puzzle[r][c] = old
                    continue
                if sum(bool(v) for row in puzzle for v in row)>45:
                    continue
                report = analyze(puzzle)
                if report.level==difficulty_name:
                    return GeneratedSudoku(puzzle,solution,report)
        raise TimeoutError('Se agotaron los intentos. Prueba de nuevo.')
