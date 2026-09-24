"""Historial local persistente de ejecuciones, independiente del tablero activo."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / 'data' / 'attempts.sqlite3'

class History:
    def __init__(self, path=DEFAULT_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                algorithm TEXT NOT NULL, date TEXT NOT NULL, state TEXT NOT NULL,
                completion REAL NOT NULL, steps INTEGER NOT NULL,
                placements INTEGER NOT NULL, erasures INTEGER NOT NULL,
                compute_seconds REAL NOT NULL, animated_seconds REAL NOT NULL
            )''')
            columns = {row['name'] for row in db.execute('PRAGMA table_info(attempts)')}
            if 'difficulty' not in columns:
                db.execute("ALTER TABLE attempts ADD COLUMN difficulty TEXT NOT NULL DEFAULT ''")
            if 'operations' not in columns:
                db.execute("ALTER TABLE attempts ADD COLUMN operations INTEGER NOT NULL DEFAULT 0")
            db.execute('''CREATE TABLE IF NOT EXISTS benchmark_results (
                algorithm TEXT PRIMARY KEY, date TEXT NOT NULL,
                easy REAL NOT NULL, medium REAL NOT NULL, hard REAL NOT NULL,
                extreme REAL NOT NULL, overall REAL NOT NULL,
                avg_steps REAL NOT NULL, avg_operations REAL NOT NULL,
                avg_compute REAL NOT NULL, errors INTEGER NOT NULL
            )''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def add(self, algorithm, date, state, completion, stats, difficulty=''):
        with self.connect() as db:
            db.execute('''INSERT INTO attempts
                (algorithm,date,state,completion,steps,placements,erasures,compute_seconds,animated_seconds,difficulty,operations)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                (algorithm,date,state,completion,stats.steps,stats.placements,
                 stats.erasures,stats.elapsed_seconds,stats.animated_seconds,difficulty,
                 stats.operations))

    def best_by_difficulty(self):
        best = {}
        # Completion first, then calculation time; latest wins exact ties.
        for row in sorted(self.all(), key=lambda r: (-r['completion'],r['compute_seconds'],-r['id'])):
            if row['difficulty']:
                best.setdefault(row['difficulty'],row)
        return best

    def save_benchmark(self, result):
        with self.connect() as db:
            db.execute('''INSERT OR REPLACE INTO benchmark_results
                (algorithm,date,easy,medium,hard,extreme,overall,avg_steps,
                 avg_operations,avg_compute,errors) VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                (result['algorithm'],result['date'],result['Fácil'],result['Intermedio'],
                 result['Difícil'],result['Extremo'],result['overall'],result['avg_steps'],
                 result['avg_operations'],result['avg_compute'],result['errors']))

    def benchmark_results(self):
        with self.connect() as db:
            rows = [dict(row) for row in db.execute('''SELECT algorithm,date,
                easy AS [Fácil], medium AS [Intermedio], hard AS [Difícil],
                extreme AS [Extremo], overall, avg_steps, avg_operations,
                avg_compute, errors FROM benchmark_results''')]
        return sorted(rows,key=lambda r:(-r['overall'],r['avg_operations'],r['avg_compute'],r['algorithm']))

    def all(self):
        with self.connect() as db:
            return [dict(row) for row in db.execute('SELECT * FROM attempts ORDER BY id DESC')]
