"""Prueba de integración con ventana real; requiere escritorio y Tkinter."""
import time
import gc
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
from sudoku.algorithm import SolvingAlgorithm
from sudoku.generator import GeneratedSudoku
from sudoku.logic import analyze
from ui.app import SudokuApp
from tests.test_core import SOLUTION, OneCellSolver, almost

class UiTests(unittest.TestCase):
    def tearDown(self):
        # Dispose Tk reference cycles on the UI thread before the next test's
        # worker threads can trigger Python's garbage collector.
        gc.collect()

    def test_content_centered_on_first_open_and_resize(self):
        with TemporaryDirectory() as directory:
            app = SudokuApp(history_path=Path(directory)/'history.sqlite3')
            try:
                def assert_centered():
                    app.root.update()
                    actual = app.content.winfo_rootx()+app.content.winfo_width()/2
                    expected = app.viewport.winfo_rootx()+app.viewport.winfo_width()/2
                    self.assertAlmostEqual(actual,expected,delta=1)
                    self.assertEqual(app.viewport.canvasx(0),0)
                assert_centered()  # No manual resize before this assertion.
                for geometry in ('900x800','400x600','620x800'):
                    app.root.geometry(geometry)
                    assert_centered()
                    app.viewport.yview_moveto(.4)
                    assert_centered()
                    app.show('home')
                    assert_centered()
            finally:
                app.close()

    def test_lifecycle(self):
        directory = TemporaryDirectory()
        app = SudokuApp(history_path=Path(directory.name)/'history.sqlite3')
        def pump(until, timeout=5):
            deadline = time.monotonic()+timeout
            while not until() and time.monotonic()<deadline:
                app.root.update()
                time.sleep(.01)
            self.assertTrue(until())
        try:
            app.root.update()
            self.assertEqual(app.view,'home')
            self.assertFalse(app.canvas.winfo_ismapped())
            self.assertEqual(app.scan_button.state,'disabled')
            self.assertEqual(len(app.benchmark_summary_rows),1)
            app.menu_generate.invoke()
            self.assertEqual(app.view,'difficulty')
            self.assertFalse(app.screens['home'].winfo_ismapped())
            app.select_difficulty('Intermedio')
            self.assertTrue(app.difficulty_buttons['Intermedio'].selected)
            app.root.geometry('400x600')
            app.root.update()
            self.assertEqual(app.content.winfo_width(),app.viewport.winfo_width())
            result = GeneratedSudoku(almost(),SOLUTION,analyze(almost()))
            with patch('ui.app.SudokuGenerator.generate',return_value=result):
                app.generate()
                pump(lambda: not app.generating)
            self.assertEqual(app.board.values(),almost())
            self.assertEqual(app.view,'game')
            self.assertFalse(app.screens['home'].winfo_ismapped())
            app.classes = [OneCellSolver]
            app.algorithm.config(values=[OneCellSolver.name])
            app.algorithm.current(0)
            app.step()
            pump(lambda: app.stats.placements==1)
            self.assertTrue(app.paused)
            self.assertTrue(app.board.is_solved)
            app.pause()
            pump(lambda: app.execution is None)
            self.assertEqual(app.status.cget('text'),'Resuelto')
            self.assertEqual(app.view,'summary')
            self.assertEqual(len(app.history.all()),1)
            self.assertGreater(app.stats.animated_seconds,app.stats.elapsed_seconds)
            self.assertEqual(app.metric_values['Resultado'].cget('text'),'Logrado')
            self.assertEqual(app.metric_values['Dificultad'].cget('text'),'Fácil')
            self.assertNotIn('Borrados',app.metric_values)
            self.assertIn('Operaciones Python',app.metric_values)
            self.assertFalse(app.summary_reason.winfo_ismapped())
            self.assertFalse(app.canvas.winfo_ismapped())
            self.assertTrue(app.final_canvas.winfo_ismapped())
            app.retry()
            self.assertEqual(app.view,'game')
            self.assertEqual(app.board.values(),almost())
            app.start(paused=True)
            app.stop()
            self.assertEqual(app.status.cget('text'),'Cancelado')
            app.retry()
            class Stuck(SolvingAlgorithm):
                name = 'Atascado'
                def solve(self):
                    total = sum(value for row in self.board for value in row)
                    return
                    yield
            app.classes = [Stuck]
            app.algorithm.config(values=['Atascado'])
            app.algorithm.current(0)
            app.start()
            pump(lambda: app.execution is None)
            self.assertEqual(app.status.cget('text'),'Sin resolver')
            self.assertEqual(app.metric_values['Resultado'].cget('text'),'Sin resolver')
            self.assertEqual(len(app.history.all()),3)
            class Broken(SolvingAlgorithm):
                name = 'Error de prueba'
                def solve(self):
                    raise RuntimeError('Fallo controlado')
                    yield
            app.retry()
            app.classes = [Broken]
            app.start()
            pump(lambda: app.execution is None)
            self.assertEqual(app.view,'summary')
            self.assertEqual(app.status.cget('text'),'Error')
            self.assertIn('Fallo controlado',app.summary_reason.cget('text'))
            self.assertEqual(app.metric_values['Resultado'].cget('fg'),'#b44848')
            app.go_home()
            self.assertEqual(app.view,'home')
            self.assertIsNone(app.board)
            self.assertFalse(hasattr(app,'resume_button'))
            self.assertFalse(hasattr(app,'speed'))
            self.assertFalse(hasattr(app,'scrollbar'))
            app.comparison()
            rows = app.history_table.get_children()
            self.assertEqual(len(rows),4)
            self.assertEqual(app.history_table.item(rows[0])['values'][0],'Error de prueba')
        finally:
            app.close()
            directory.cleanup()

    def test_benchmark_all_and_individual(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            app = SudokuApp(history_path=root/'history.sqlite3',
                            benchmark_suite_path=root/'suite.json')
            class FastBenchmark(SolvingAlgorithm):
                name = 'Benchmark rápido'
                description = ''
                def solve(self):
                    yield self.place(0,0,1)
            app.classes = [FastBenchmark]
            app.benchmark_algorithm.config(values=['Todos los algoritmos','Benchmark rápido'])
            cases = [{'difficulty':level,'puzzle':almost(),'solution':SOLUTION}
                     for level in ('Fácil','Intermedio','Difícil','Extremo') for _ in range(10)]
            def pump(until,timeout=20):
                deadline = time.monotonic()+timeout
                while not until() and time.monotonic()<deadline:
                    app.root.update()
                    time.sleep(.01)
                self.assertTrue(until())
            try:
                app.root.update()
                app.show('benchmark')
                with patch.object(app.benchmark_suite,'ensure',return_value=cases):
                    app.benchmark_algorithm.current(0)
                    app.start_benchmark()
                    pump(lambda:not app.benchmark_running)
                    self.assertEqual(len(app.history.benchmark_results()),len(app.classes))
                    self.assertEqual(app.benchmark_progress['value'],100)
                    app.benchmark_algorithm.current(1)
                    app.start_benchmark()
                    pump(lambda:not app.benchmark_running)
                    self.assertEqual(len(app.history.benchmark_results()),len(app.classes))
                app.show('home')
                self.assertGreaterEqual(len(app.benchmark_summary_rows),1)
            finally:
                app.close()

if __name__=='__main__':
    unittest.main()
