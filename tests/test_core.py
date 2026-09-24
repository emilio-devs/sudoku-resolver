import unittest
from contextlib import redirect_stderr
from io import StringIO
from tempfile import TemporaryDirectory
from pathlib import Path
from threading import Event
from unittest.mock import patch

from sudoku.algorithm import SolvingAlgorithm, AlgorithmStats, AlgorithmCancelled
from sudoku.history import History
from sudoku.discovery import discover
from soluciones.s00_ejemplo import NakedSingles as ExampleAlgorithm
from sudoku.execution import Execution, score
from sudoku.generator import SudokuGenerator, GenerationCancelled
from sudoku.logic import analyze
from sudoku.model import Sudoku
from sudoku.solver_utils import count_solutions

SOLUTION = [[(r*3+r//3+c)%9+1 for c in range(9)] for r in range(9)]

def almost():
    grid = [r[:] for r in SOLUTION]
    grid[0][0] = 0
    return grid

class OneCellSolver(SolvingAlgorithm):
    name = 'Solucionador de prueba'
    description = ''

    def solve(self):
        yield self.place(0,0,1)

class CoreTests(unittest.TestCase):
    def test_model_validation_and_copies(self):
        board = Sudoku(almost(),SOLUTION)
        self.assertEqual(board.candidates(0,0),{1})
        self.assertFalse(board.set_value(0,1,0))
        self.assertFalse(board.set_value(0,0,2))
        self.assertFalse(board.set_value(0,0,True))
        with self.assertRaises(ValueError):
            board.value(-1,0)
        with self.assertRaises(ValueError):
            Sudoku([[1.5]*9 for _ in range(9)])
        other = board.copy()
        self.assertTrue(other.set_value(0,0,1))
        self.assertTrue(other.is_solved)
        self.assertFalse(board.is_complete)
        other.grid[0][0] = 2
        self.assertTrue(other.is_complete)
        self.assertFalse(other.is_solved)
        sparse = Sudoku([[0]*9 for _ in range(9)],SOLUTION)
        self.assertTrue(sparse.can_place(0,0,2))
        self.assertFalse(sparse.is_correct(0,0,2))

    def test_uniqueness_and_restore(self):
        grid = almost()
        self.assertEqual(count_solutions(grid),1)
        self.assertEqual(grid,almost())
        self.assertEqual(count_solutions([[0]*9 for _ in range(9)]),2)
        checks = 0
        def interrupt():
            nonlocal checks
            checks += 1
            if checks==2:
                raise RuntimeError()
        with self.assertRaises(RuntimeError):
            count_solutions(grid,checkpoint=interrupt)
        self.assertEqual(grid,almost())

    def test_generated_categories(self):
        for level in ('Fácil','Intermedio','Difícil','Extremo'):
            with self.subTest(level=level):
                result = SudokuGenerator().generate(level,seed=12,timeout=45)
                self.assertEqual(count_solutions(result.puzzle),1)
                self.assertEqual(result.report,analyze(result.puzzle))
                self.assertEqual(result.report.level,level)
                self.assertTrue(Sudoku(result.solution).is_solved)
                self.assertLess(result.report.clues,81)
                if level=='Difícil':
                    self.assertGreater(result.report.eliminations,0)
                    self.assertTrue(result.report.solved)
                if level=='Extremo':
                    self.assertFalse(result.report.solved)

    def test_generation_limits(self):
        event = Event()
        event.set()
        with self.assertRaises(GenerationCancelled):
            SudokuGenerator().generate('Fácil',cancel=event)
        with self.assertRaises(TimeoutError):
            SudokuGenerator().generate('Extremo',timeout=0)

    def test_actions_time_and_score(self):
        class Actions(SolvingAlgorithm):
            def solve(self):
                yield self.place(0,0,1)
                yield self.place(0,0,0,'Retroceso')
                yield self.place(0,0,1)
                yield self.place(0,1,2)
        puzzle = almost()
        puzzle[0][1] = 0
        algorithm = Actions(puzzle)
        # El reloj simulado avanza 1 ms por tramo de cálculo; las esperas entre
        # next() quedan fuera de los intervalos medidos.
        with patch('sudoku.algorithm.time.perf_counter',side_effect=[0,.001,50,50.001,100,100.001,150,150.001]):
            events = list(algorithm._run(SOLUTION))
        stats = algorithm._stats
        self.assertEqual((stats.steps,stats.placements,stats.erasures),(4,3,1))
        self.assertGreater(stats.operations,0)
        self.assertAlmostEqual(stats.elapsed_seconds,.004)
        board = Sudoku(puzzle,SOLUTION)
        self.assertEqual(score(board),0)
        for event in events:
            if event.value is not None:
                self.assertTrue(board.set_value(event.row,event.col,event.value))
        self.assertEqual(score(board),100)

    def test_algorithm_has_minimal_api(self):
        algorithm = OneCellSolver(almost())
        self.assertEqual(algorithm.board,almost())
        for name in ('get_value','candidates','can_place','is_valid','is_correct',
                     '_sudoku','count_check','count_operation','checkpoint','erase','note','run','stats'):
            self.assertFalse(hasattr(algorithm,name))
        self.assertFalse(hasattr(algorithm,'stats'))
        self.assertFalse(hasattr(algorithm,'solution'))
        self.assertFalse(hasattr(algorithm,'_solution'))
        self.assertFalse(hasattr(algorithm._stats,'solved'))
        self.assertFalse(hasattr(algorithm._stats,'checks'))

    def test_wrong_value_ends_attempt_outside_user_generator(self):
        class Probe(SolvingAlgorithm):
            continued = False
            def solve(self):
                try:
                    yield self.place(0,0,2)
                except ValueError:
                    pass
                self.continued = True
                yield self.place(0,0,1)
        # En un tablero vacío, 2 es legal localmente en (0, 0), pero la
        # solución de referencia exige 1. Debe rechazarse igualmente.
        puzzle = [[0 for _ in range(9)] for _ in range(9)]
        algorithm = Probe(puzzle)
        runner = Execution(algorithm,SOLUTION)
        runner.advance()
        kind,message,_ = runner.results.get(timeout=2)
        self.assertEqual(kind,'error')
        self.assertIn('Valor incorrecto',message)
        self.assertFalse(algorithm.continued)
        self.assertEqual(algorithm.board[0][0],0)
        runner.stop()

    def test_local_board_automatic_cost_and_direct_mutation_guard(self):
        class Worker(SolvingAlgorithm):
            def solve(self):
                assert self.board[0][0]==0
                yield self.place(0,0,1)
                assert self.board[0][0]==1
                yield self.place(0,0,0,'Retroceso')
                assert self.board[0][0]==0
        puzzle = almost()
        puzzle[0][1] = 0
        algorithm = Worker(puzzle)
        self.assertEqual(len(list(algorithm._run(SOLUTION))),2)
        self.assertEqual(algorithm._stats.steps,2)
        self.assertGreater(algorithm._stats.operations,0)
        algorithm._cancel.set()
        with self.assertRaises(AlgorithmCancelled):
            list(algorithm._run(SOLUTION))

        class Mutator(SolvingAlgorithm):
            def solve(self):
                self.board[0][0] = 1
                yield self.place(0,0,1)
        with self.assertRaisesRegex(ValueError,'solo lectura'):
            list(Mutator(almost())._run(SOLUTION))

        class SilentMutator(SolvingAlgorithm):
            def solve(self):
                self.board[0][0] = 1
                return
                yield
        with self.assertRaisesRegex(ValueError,'solo lectura'):
            list(SilentMutator(almost())._run(SOLUTION))

    def test_computation_only_execution_reports_cost_without_steps(self):
        class Worker(SolvingAlgorithm):
            def solve(self):
                total = sum(value for row in self.board for value in row)
                return
                yield
        runner = Execution(Worker(almost()),SOLUTION)
        runner.advance()
        kind,_,stats = runner.results.get(timeout=2)
        self.assertEqual(kind,'done')
        self.assertEqual(stats.steps,0)
        self.assertGreater(stats.operations,0)
        runner.stop()

    def test_history_persists_newest_first(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)/'history.sqlite3'
            history = History(path)
            stats = AlgorithmStats(steps=3,elapsed_seconds=.01,animated_seconds=1.25)
            history.add('Primero','2026-09-17T14:20','Sin resolver',30,stats)
            history.add('Segundo','2026-09-17T14:20','Resuelto',100,stats)
            rows = History(path).all()
            self.assertEqual([r['algorithm'] for r in rows],['Segundo','Primero'])
            self.assertEqual(rows[0]['animated_seconds'],1.25)

    def test_worker_error_and_cancel(self):
        class Bad(SolvingAlgorithm):
            def solve(self):
                yield self.place(0,1,0)
        runner = Execution(Bad(almost()),SOLUTION)
        errors = StringIO()
        with redirect_stderr(errors):
            runner.advance()
            self.assertEqual(runner.results.get(timeout=2)[0],'error')
        diagnostic = errors.getvalue()
        self.assertIn('[Sudoku Studio] Error al ejecutar',diagnostic)
        self.assertIn('Traceback (most recent call last)',diagnostic)
        runner.stop()
        runner = Execution(OneCellSolver(almost()),SOLUTION)
        runner.advance()
        self.assertEqual(runner.results.get(timeout=2)[0],'step')
        self.assertTrue(runner.results.empty())
        runner.advance()
        self.assertEqual(runner.results.get(timeout=2)[0],'done')
        runner.stop()

    def test_plugin_failure_does_not_hide_others(self):
        import importlib
        original = importlib.import_module
        from types import SimpleNamespace
        entries = [SimpleNamespace(name='broken'),SimpleNamespace(name='s00_ejemplo')]
        def load(name):
            if name.endswith('.broken'):
                raise SyntaxError('Prueba')
            return original(name)
        diagnostic = StringIO()
        with redirect_stderr(diagnostic), \
                patch('sudoku.discovery.pkgutil.iter_modules',return_value=entries), \
                patch('sudoku.discovery.importlib.import_module',side_effect=load):
            found,errors = discover()
        self.assertIn(ExampleAlgorithm,found)
        self.assertEqual(len(errors),1)
        self.assertIn('No se pudo cargar soluciones.broken',diagnostic.getvalue())

    def test_history_migration_and_best_per_level(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)/'history.sqlite3'
            history = History(path)
            stats = AlgorithmStats(elapsed_seconds=.02)
            history.add('Antiguo','2026-09-17T14:20','Resuelto',100,stats)
            with history.connect() as db:
                db.execute('ALTER TABLE attempts DROP COLUMN difficulty')
            history = History(path)
            self.assertEqual(history.all()[0]['difficulty'],'')
            self.assertEqual(history.best_by_difficulty(),{})
            history.add('Completo','2026-09-17T14:21','Resuelto',100,stats,'Fácil')
            stats.elapsed_seconds = .01
            history.add('Rápido','2026-09-17T14:22','Resuelto',100,stats,'Fácil')
            stats.elapsed_seconds = .001
            history.add('Parcial','2026-09-17T14:23','Sin resolver',60,stats,'Fácil')
            history.add('Otro nivel','2026-09-17T14:24','Sin resolver',40,stats,'Difícil')
            best = history.best_by_difficulty()
            self.assertEqual(best['Fácil']['algorithm'],'Rápido')
            self.assertEqual(best['Difícil']['algorithm'],'Otro nivel')

if __name__=='__main__':
    unittest.main()
