"""Suite persistente y ejecución sin animación de benchmarks."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from threading import Event

from .algorithm import AlgorithmCancelled
from .diagnostics import print_current_exception
from .generator import DIFFICULTIES, SudokuGenerator, GenerationCancelled
from .model import Sudoku

SUITE_VERSION = 1
CASES_PER_LEVEL = 10
DEFAULT_SUITE_PATH = Path(__file__).resolve().parent.parent / 'data' / 'benchmark_suite.json'


class BenchmarkCancelled(Exception):
    pass


class BenchmarkSuite:
    def __init__(self, path=DEFAULT_SUITE_PATH):
        self.path = Path(path)

    def load(self):
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        cases = data.get('cases', [])
        counts = {level: sum(case.get('difficulty') == level for case in cases)
                  for level in DIFFICULTIES}
        if data.get('version') != SUITE_VERSION or any(n != CASES_PER_LEVEL for n in counts.values()):
            return None
        try:
            for case in cases:
                board = Sudoku(case['puzzle'],case['solution'])
                if not board.is_valid() or not Sudoku(case['solution']).is_solved:
                    return None
        except (KeyError,ValueError,TypeError):
            return None
        return cases

    def ensure(self, cancel=None, progress=lambda done,total,text: None):
        cases = self.load()
        if cases is not None:
            progress(40,40,'Suite preparada')
            return cases
        cancel = cancel or Event()
        cases = []
        total = len(DIFFICULTIES)*CASES_PER_LEVEL
        for level_index,level in enumerate(DIFFICULTIES):
            for index in range(CASES_PER_LEVEL):
                if cancel.is_set():
                    raise BenchmarkCancelled()
                done = len(cases)
                progress(done,total,f'Creando casos · {level} {index+1}/{CASES_PER_LEVEL}')
                seed = 150_000 + level_index*10_000 + index*997
                try:
                    generated = SudokuGenerator().generate(level,cancel=cancel,timeout=90,
                                                            max_attempts=300,seed=seed)
                except GenerationCancelled as exc:
                    raise BenchmarkCancelled() from exc
                cases.append({'difficulty':level,'puzzle':generated.puzzle,
                              'solution':generated.solution})
        self.path.parent.mkdir(parents=True,exist_ok=True)
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps({'version':SUITE_VERSION,'cases':cases},
                                   ensure_ascii=False,separators=(',',':')),encoding='utf-8')
        os.replace(temp,self.path)
        progress(total,total,'Suite preparada')
        return cases


def _completion(puzzle, solution, grid):
    empty = [(r,c) for r in range(9) for c in range(9) if not puzzle[r][c]]
    return 100*sum(grid[r][c] == solution[r][c] for r,c in empty)/len(empty)


def run_benchmark(classes, cases, history, cancel=None, progress=lambda done,total,text: None):
    cancel = cancel or Event()
    total = len(classes)*len(cases)
    done = 0
    results = []
    for algorithm_class in classes:
        by_level = {level:[] for level in DIFFICULTIES}
        steps = operations = compute = errors = 0
        for case in cases:
            if cancel.is_set():
                raise BenchmarkCancelled()
            progress(done,total,f'{algorithm_class.name} · {case["difficulty"]}')
            algorithm = algorithm_class(case['puzzle'])
            algorithm._cancel = cancel
            try:
                for _ in algorithm._run(case['solution']):
                    pass
            except (AlgorithmCancelled,BenchmarkCancelled):
                raise BenchmarkCancelled()
            except Exception:
                print_current_exception(
                    f'Error en benchmark: "{algorithm_class.name}" - {case["difficulty"]}'
                )
                errors += 1
            by_level[case['difficulty']].append(
                _completion(case['puzzle'],case['solution'],algorithm.board))
            steps += algorithm._stats.steps
            operations += algorithm._stats.operations
            compute += algorithm._stats.elapsed_seconds
            done += 1
        result = {'algorithm':algorithm_class.name,
                  'date':datetime.now().isoformat(timespec='minutes'),
                  **{level:sum(values)/len(values) for level,values in by_level.items()},
                  'overall':sum(sum(values) for values in by_level.values())/len(cases),
                  'avg_steps':steps/len(cases),'avg_operations':operations/len(cases),
                  'avg_compute':compute/len(cases),'errors':errors}
        history.save_benchmark(result)
        results.append(result)
    progress(total,total,'Benchmark terminado')
    return results
