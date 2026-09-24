"""API de complementos: emite un evento por cada avance observable."""
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from threading import Event, Lock, local
from sudoku.model import Sudoku

class AlgorithmCancelled(Exception):
    pass


_MONITOR_TOOL_ID = 4
_monitor_state = local()
_monitor_lock = Lock()
_monitor_users = 0
_monitor_ready = False


def _instruction(code, offset):
    counter = getattr(_monitor_state,'counter',None)
    if counter is not None and counter.tracks(code):
        counter.algorithm._stats.operations += 1


def _begin_monitoring(counter):
    global _monitor_ready, _monitor_users
    with _monitor_lock:
        if not _monitor_ready:
            sys.monitoring.use_tool_id(_MONITOR_TOOL_ID,'sudoku-algorithm-meter')
            sys.monitoring.register_callback(_MONITOR_TOOL_ID,
                sys.monitoring.events.INSTRUCTION,_instruction)
            _monitor_ready = True
        _monitor_users += 1
        if _monitor_users == 1:
            sys.monitoring.set_events(_MONITOR_TOOL_ID,sys.monitoring.events.INSTRUCTION)
    _monitor_state.counter = counter


def _end_monitoring():
    global _monitor_users
    _monitor_state.counter = None
    with _monitor_lock:
        _monitor_users -= 1
        if _monitor_users == 0:
            sys.monitoring.set_events(_MONITOR_TOOL_ID,0)


class _OpcodeCounter:
    """Counts Python bytecode executed by an algorithm and its local helpers."""
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.root = Path(algorithm.solve.__code__.co_filename).resolve().parent
        self.base_file = Path(__file__).resolve()
        self.cache = {}

    def tracks(self, code):
        if code not in self.cache:
            try:
                path = Path(code.co_filename).resolve()
                self.cache[code] = path != self.base_file and path.is_relative_to(self.root)
            except (OSError,ValueError):
                self.cache[code] = False
        return self.cache[code]

    def __call__(self, frame, event, arg):
        if event == 'call':
            if not self.tracks(frame.f_code):
                return None
            return self
        if event == 'line':
            self.algorithm._checkpoint()
        return self

@dataclass(frozen=True)
class Step:
    row: int
    col: int
    value: int
    reason: str = ''

@dataclass
class AlgorithmStats:
    steps: int = 0
    placements: int = 0
    erasures: int = 0
    operations: int = 0
    elapsed_seconds: float = 0.0
    animated_seconds: float = 0.0

class SolvingAlgorithm(ABC):
    name = 'Algoritmo sin nombre'
    description = ''

    def __init__(self, puzzle):
        self.board = [row[:] for row in puzzle]
        self._stats = AlgorithmStats()
        self._cancel = Event()
        self._counter = _OpcodeCounter(self)

    def _checkpoint(self):
        if self._cancel.is_set():
            raise AlgorithmCancelled()

    def place(self, row, col, value, reason=''):
        """Construye un evento. El estado cambia cuando se emite con yield."""
        self._checkpoint()
        return Step(row,col,value,reason)

    def _run(self, solution):
        # Validation stays outside solve(): the reference solution is never
        # exposed to the user's algorithm and a rejected move cannot be caught
        # inside its generator or repurposed as a candidate query.
        validator = Sudoku(self.board, solution)
        iterator = None
        while True:
            self._checkpoint()
            expected = validator.values()
            previous_trace = sys.gettrace()
            sys.settrace(self._counter)
            _begin_monitoring(self._counter)
            started = time.perf_counter()
            finished = False
            try:
                if iterator is None:
                    iterator = iter(self.solve())
                frame = getattr(iterator,'gi_frame',None)
                if frame is not None:
                    frame.f_trace = self._counter
                step = next(iterator)
            except StopIteration:
                finished = True
            finally:
                self._stats.elapsed_seconds += time.perf_counter()-started
                _end_monitoring()
                sys.settrace(previous_trace)
            self._checkpoint()
            if self.board != expected:
                raise ValueError('El tablero es de solo lectura: usa yield self.place(...) para modificarlo.')
            if finished:
                return
            if not isinstance(step,Step) or not isinstance(step.reason,str):
                raise ValueError('El algoritmo debe emitir objetos Step válidos.')
            if step.value and not validator.is_correct(step.row,step.col,step.value):
                raise ValueError(f'Valor incorrecto: ({step.row}, {step.col}) = {step.value}')
            if not validator.set_value(step.row,step.col,step.value):
                raise ValueError(f'Movimiento no permitido: ({step.row}, {step.col}) = {step.value}')
            self.board[step.row][step.col] = step.value
            if step.value:
                self._stats.placements += 1
            else:
                self._stats.erasures += 1
            self._stats.steps += 1
            yield step
            if validator.is_solved:
                return

    @abstractmethod
    def solve(self):
        """Generador: usa yield self.place(...). El valor 0 borra una celda."""
        raise NotImplementedError
