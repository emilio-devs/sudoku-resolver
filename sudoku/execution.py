"""Ejecutor cooperativo: una petición produce como máximo un evento."""
from dataclasses import replace
from queue import Queue
from threading import Event, Thread
from .algorithm import AlgorithmCancelled
from .diagnostics import print_current_exception

class Execution:
    def __init__(self, algorithm, solution):
        self.algorithm = algorithm
        self.solution = solution
        self.results = Queue()
        self._request = Event()
        self._closed = Event()
        Thread(target=self._work,daemon=True).start()

    def advance(self):
        self._request.set()

    def stop(self):
        self.algorithm._cancel.set()
        self._closed.set()
        self._request.set()

    def _work(self):
        iterator = self.algorithm._run(self.solution)
        try:
            while not self._closed.is_set():
                self._request.wait()
                self._request.clear()
                if self._closed.is_set():
                    break
                try:
                    step = next(iterator)
                except StopIteration:
                    self.results.put(('done',None,replace(self.algorithm._stats)))
                    break
                self.results.put(('step',step,replace(self.algorithm._stats)))
        except AlgorithmCancelled:
            pass
        except Exception as exc:
            print_current_exception(f'Error al ejecutar "{self.algorithm.name}"')
            self.results.put(('error',f'{type(exc).__name__}: {exc}',replace(self.algorithm._stats)))
        finally:
            iterator.close()

def score(board):
    empty = [(r,c) for r in range(9) for c in range(9) if not board.puzzle[r][c]]
    if not empty:
        return 100.0 if board.is_solved else 0.0
    return 100*sum(board.is_correct(r,c,board.grid[r][c]) for r,c in empty)/len(empty)
