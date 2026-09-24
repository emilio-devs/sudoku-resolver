import time
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from .views import Views
from queue import Queue, Empty
from threading import Event, Thread

from sudoku.algorithm import AlgorithmStats
from sudoku.diagnostics import print_current_exception
from sudoku.discovery import discover
from sudoku.execution import Execution, score
from sudoku.generator import DIFFICULTIES, SudokuGenerator, GenerationCancelled
from sudoku.model import Sudoku
from sudoku.history import History, DEFAULT_PATH
from sudoku.benchmark import (BenchmarkSuite, DEFAULT_SUITE_PATH, BenchmarkCancelled,
                              run_benchmark)

BG = '#f3f5f9'
INK = '#19283e'
ACCENT = '#176c70'

class SudokuApp(Views):
    def __init__(self, history_path=DEFAULT_PATH, benchmark_suite_path=DEFAULT_SUITE_PATH):
        self.history = History(history_path)
        self.benchmark_suite = BenchmarkSuite(benchmark_suite_path)
        self.benchmark_running = False
        self.benchmark_cancel = None
        self.benchmark_results = Queue()
        self.started_at = None
        self.attempt_date = ''
        self.root = tk.Tk()
        self.root.title('Sudoku · Laboratorio de algoritmos')
        self.root.geometry(f'620x{min(900, self.root.winfo_screenheight()-100)}')
        self.root.minsize(400,600)
        self.root.configure(bg=BG)
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.board = self.generated = self.execution = None
        self.generating = False
        self.generation_cancel = None
        self.generation_results = Queue()
        self.stats = AlgorithmStats()
        self.pending = False
        self.buffered = None
        self.paused = False
        self.single_step = False
        self.next_at = 0
        self.highlight = None
        self.classes,self.load_errors = discover()
        self._build()
        self._controls()
        self._poll_job = self.root.after(30,self._poll)
        if self.load_errors:
            self.root.after(100,lambda: messagebox.showwarning('Complementos omitidos','\n'.join(self.load_errors)))

    def help_difficulty(self):
        messagebox.showinfo(self.difficulty.get(),DIFFICULTIES[self.difficulty.get()])

    def report(self):
        if not self.generated:
            return
        r = self.generated.report
        messagebox.showinfo(r.level,DIFFICULTIES[r.level])

    def generate(self):
        if self.generating or self.execution:
            return
        self.generating = True
        self.generation_cancel = Event()
        cancel = self.generation_cancel
        level = self.difficulty.get()
        self.home_hint.config(text='Buscando un sudoku con solución única…')
        self._controls()
        def work():
            try:
                self.generation_results.put(('ok',SudokuGenerator().generate(level,cancel=cancel)))
            except GenerationCancelled:
                self.generation_results.put(('cancel',None))
            except Exception as exc:
                print_current_exception('Error inesperado al generar un sudoku')
                self.generation_results.put(('error',str(exc)))
        Thread(target=work,daemon=True).start()

    def cancel_generation(self):
        if self.generation_cancel:
            self.generation_cancel.set()

    def start_benchmark(self):
        if self.benchmark_running or not self.classes:
            return
        selected = self.benchmark_algorithm.current()
        classes = self.classes if selected <= 0 else [self.classes[selected-1]]
        self.benchmark_running = True
        self.benchmark_cancel = Event()
        cancel = self.benchmark_cancel
        self.benchmark_status.config(text='Preparando el conjunto de casos…')
        self.benchmark_progress['value'] = 0
        self._controls()

        def progress(done,total,label):
            self.benchmark_results.put(('progress',(done,total,label)))

        def work():
            try:
                cases = self.benchmark_suite.ensure(cancel=cancel,progress=progress)
                run_benchmark(classes,cases,self.history,cancel=cancel,progress=progress)
                self.benchmark_results.put(('done',None))
            except BenchmarkCancelled:
                self.benchmark_results.put(('cancel',None))
            except Exception as exc:
                print_current_exception('Error inesperado al ejecutar el benchmark')
                self.benchmark_results.put(('error',f'{type(exc).__name__}: {exc}'))
        Thread(target=work,daemon=True).start()

    def cancel_benchmark(self):
        if self.benchmark_cancel:
            self.benchmark_cancel.set()

    def start(self, paused=False):
        if self.execution or not self.board or self.generating:
            return
        i = self.algorithm.current()
        if i<0:
            return
        self.board.reset()
        self.started_at = time.perf_counter()
        self.attempt_date = datetime.now().isoformat(timespec='minutes')
        self.stats = AlgorithmStats()
        self.highlight = None
        self.paused = paused
        self.pending = False
        self.buffered = None
        self.single_step = False
        self.next_at = 0
        try:
            self.execution = Execution(
                self.classes[i](self.board.values()), self.generated.solution
            )
        except Exception as exc:
            print_current_exception(f'Error al preparar "{self.classes[i].name}"')
            self.reason.config(text=str(exc))
            self.finish('Error')
            return
        self.status.config(text='En pausa' if paused else 'Resolviendo…')
        self.reason.config(text='Esperando el primer evento…')
        self.draw()
        self._controls()
        self._metrics()

    def pause(self):
        if self.execution:
            self.paused = not self.paused
            self.single_step = False
            self.status.config(text='En pausa' if self.paused else 'Resolviendo…')
            self._controls()

    def step(self):
        if not self.execution:
            self.start(paused=True)
        if self.execution:
            self.paused = True
            self.single_step = True
            self.next_at = 0
            self._controls()

    def stop(self):
        if self.execution:
            self.finish('Cancelado')

    def reset(self):
        if self.board and not self.execution and not self.generating:
            self.board.reset()
            self.stats = AlgorithmStats()
            self.highlight = None
            self.status.config(text='Tablero reiniciado')
            self.reason.config(text='')
            self.draw()
            self._metrics()

    def finish(self,state):
        self.stats.animated_seconds = max(0, time.perf_counter()-self.started_at) if self.started_at is not None else 0
        self.started_at = None
        if self.execution:
            self.execution.stop()
            self.execution = None
        self.pending = False
        self.buffered = None
        self.single_step = False
        self.status.config(text=state)
        try:
            self.history.add(self.classes[self.algorithm.current()].name,self.attempt_date,
                             state,score(self.board),self.stats,self.generated.report.level)
        except Exception as exc:
            print_current_exception('No se pudo guardar el intento en el historial')
            messagebox.showerror('Historial',f'No se pudo guardar este intento: {exc}')
        self.render_summary(state)
        self._metrics()
        self._controls()

    def _poll(self):
        try:
            while True:
                kind,payload = self.benchmark_results.get_nowait()
                if kind=='progress':
                    done,total,label = payload
                    self.benchmark_progress['value'] = 100*done/max(1,total)
                    self.benchmark_status.config(text=f'{label} · {done}/{total}')
                else:
                    self.benchmark_running = False
                    if kind=='done':
                        self.benchmark_progress['value'] = 100
                        self.benchmark_status.config(text='Benchmark terminado y guardado.')
                    elif kind=='cancel':
                        self.benchmark_status.config(text='Benchmark cancelado.')
                    else:
                        self.benchmark_status.config(text='No se pudo completar el benchmark.')
                        messagebox.showerror('Benchmark',payload)
                    self.refresh_benchmark_tables()
                    self._controls()
        except Empty:
            pass
        try:
            kind,payload = self.generation_results.get_nowait()
            self.generating = False
            if kind=='ok' and not self.generation_cancel.is_set():
                self.generated = payload
                self.board = Sudoku(payload.puzzle,payload.solution)
                self.stats = AlgorithmStats()
                self.highlight = None
                self.puzzle_label.config(text=f'{payload.report.level} · {payload.report.clues} pistas · Solución única verificada')
                self.status.config(text='Elige un algoritmo')
                self.reason.config(text='')
                self.home_hint.config(text='')
                self.show('game')
                self.draw()
                self._metrics()
            elif kind=='error':
                self.home_hint.config(text='No se pudo generar. Puedes volver a intentarlo.')
                messagebox.showerror('Generación',payload)
            else:
                self.home_hint.config(text='Generación cancelada.')
            self._controls()
        except Empty:
            pass
        if self.execution:
            if self.buffered is None:
                try:
                    self.buffered = self.execution.results.get_nowait()
                except Empty:
                    pass
            if self.buffered and (not self.paused or self.single_step):
                kind,payload,self.stats = self.buffered
                self.buffered = None
                self.pending = False
                self.single_step = False
                if kind=='step':
                    if payload.value is not None:
                        if not self.board.set_value(payload.row,payload.col,payload.value):
                            self.reason.config(text='Movimiento rechazado por el tablero.')
                            self.finish('Error')
                        else:
                            self.highlight = (payload.row,payload.col)
                    self.reason.config(text=payload.reason or 'Movimiento sin descripción')
                    self.draw()
                    self._metrics()
                    self.next_at = time.monotonic()+0.25
                elif kind=='done':
                    self.finish('Resuelto' if self.board.is_solved else 'Sin resolver')
                else:
                    self.reason.config(text=payload)
                    self.finish('Error')
            if self.execution and not self.pending and (not self.paused or self.single_step) and time.monotonic()>=self.next_at:
                self.pending = True
                self.execution.advance()
        self._poll_job = self.root.after(20,self._poll)

    def close(self):
        self.root.after_cancel(self._poll_job)
        self.cancel_generation()
        self.cancel_benchmark()
        if self.execution:
            self.finish('Cancelado')
        self.root.destroy()

    def run(self):
        self.root.mainloop()
