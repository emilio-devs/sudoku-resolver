import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
from unittest.mock import patch

from sudoku.algorithm import SolvingAlgorithm
from sudoku.benchmark import (BenchmarkCancelled, BenchmarkSuite, CASES_PER_LEVEL,
                              run_benchmark)
from sudoku.generator import DIFFICULTIES, GeneratedSudoku
from sudoku.history import History
from sudoku.logic import analyze
from tests.test_core import SOLUTION, almost


class Complete(SolvingAlgorithm):
    name = 'Completo'
    description = ''

    def solve(self):
        yield self.place(0,0,1)


class Partial(SolvingAlgorithm):
    name = 'Parcial'
    description = ''

    def solve(self):
        total = sum(value for row in self.board for value in row)
        return
        yield


class BenchmarkTests(unittest.TestCase):
    def test_suite_is_created_once_and_reused(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)/'suite.json'
            suite = BenchmarkSuite(path)
            generated = GeneratedSudoku(almost(),SOLUTION,analyze(almost()))
            updates = []
            with patch('sudoku.benchmark.SudokuGenerator.generate',return_value=generated) as generate:
                cases = suite.ensure(progress=lambda done,total,text: updates.append((done,total)))
            self.assertEqual(generate.call_count,40)
            self.assertEqual(len(cases),40)
            self.assertEqual({level:sum(c['difficulty']==level for c in cases)
                              for level in DIFFICULTIES},
                             {level:CASES_PER_LEVEL for level in DIFFICULTIES})
            with patch('sudoku.benchmark.SudokuGenerator.generate') as generate:
                reused = BenchmarkSuite(path).ensure()
            generate.assert_not_called()
            self.assertEqual(reused,cases)

    def test_suite_cancel_does_not_write_partial_file(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)/'suite.json'
            cancel = Event()
            cancel.set()
            with self.assertRaises(BenchmarkCancelled):
                BenchmarkSuite(path).ensure(cancel=cancel)
            self.assertFalse(path.exists())

    def test_run_all_ranks_and_persists_latest_result(self):
        with TemporaryDirectory() as folder:
            history = History(Path(folder)/'history.sqlite3')
            cases = [{'difficulty':level,'puzzle':almost(),'solution':SOLUTION}
                     for level in DIFFICULTIES for _ in range(CASES_PER_LEVEL)]
            progress = []
            run_benchmark([Partial,Complete],cases,history,
                          progress=lambda done,total,text: progress.append((done,total)))
            rows = history.benchmark_results()
            self.assertEqual([row['algorithm'] for row in rows],['Completo','Parcial'])
            complete = rows[0]
            self.assertEqual(complete['overall'],100)
            self.assertEqual(complete['avg_steps'],1)
            self.assertGreater(complete['avg_operations'],0)
            self.assertEqual(complete['errors'],0)
            self.assertEqual(rows[1]['overall'],0)
            self.assertEqual(progress[-1],(80,80))
            # A later run replaces, rather than duplicates, this algorithm.
            run_benchmark([Complete],cases,history)
            self.assertEqual(len(history.benchmark_results()),2)

    def test_cancel_before_run(self):
        with TemporaryDirectory() as folder:
            cancel = Event()
            cancel.set()
            with self.assertRaises(BenchmarkCancelled):
                run_benchmark([Complete],[{'difficulty':'Fácil','puzzle':almost(),
                                           'solution':SOLUTION}],
                              History(Path(folder)/'history.sqlite3'),cancel=cancel)

    def test_shared_cancel_reaches_automatic_meter(self):
        class CancelDuringWork(SolvingAlgorithm):
            name = 'Cancelación cooperativa'
            def solve(self):
                cancel.set()
                total = 0
                for number in range(10_000):
                    total += number
                return
                yield
        with TemporaryDirectory() as folder:
            cancel = Event()
            with self.assertRaises(BenchmarkCancelled):
                run_benchmark([CancelDuringWork],[{'difficulty':'Fácil','puzzle':almost(),
                    'solution':SOLUTION}],History(Path(folder)/'history.sqlite3'),cancel=cancel)


if __name__ == '__main__':
    unittest.main()
