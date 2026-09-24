"""Capturas de las tres vistas de la propia aplicación para revisión visual."""
from pathlib import Path
import time
from tempfile import TemporaryDirectory
from PIL import ImageGrab
from ui.app import SudokuApp
from sudoku.generator import SudokuGenerator
from sudoku.model import Sudoku

def main():
    output = Path('artifacts')
    output.mkdir(exist_ok=True)
    directory = TemporaryDirectory()
    app = SudokuApp(history_path=Path(directory.name)/'preview.sqlite3')
    for index,name in enumerate(('Mi algoritmo','Otra estrategia')):
        app.history.save_benchmark({'algorithm':name,'date':'2026-09-22T13:36',
            'Fácil':100-index*5,'Intermedio':82-index*8,'Difícil':61-index*7,
            'Extremo':35-index*9,'overall':69.5-index*7.25,'avg_steps':120+index*10,
            'avg_operations':2400+index*300,'avg_compute':.012+index*.004,'errors':index})
    app.refresh_benchmark_tables()
    app.root.geometry('620x760+50+30')
    app.root.attributes('-topmost',True)
    def capture(name):
        app.root.update()
        for _ in range(10):
            app.root.update()
            time.sleep(.05)
        x,y = app.root.winfo_rootx(),app.root.winfo_rooty()
        ImageGrab.grab(bbox=(x,y,x+app.root.winfo_width(),y+app.root.winfo_height())).save(output / f'{name}.png')
    try:
        capture('inicio')
        app.show('benchmark')
        capture('benchmark')
        app.show('difficulty')
        capture('dificultad')
        app.generated = SudokuGenerator().generate('Fácil',seed=12)
        app.board = Sudoku(app.generated.puzzle,app.generated.solution)
        app.puzzle_label.config(text='Fácil · 45 pistas · Solución única')
        app.show('game')
        app._controls()
        capture('juego')
        app.board.grid = [row[:] for row in app.generated.solution]
        app.stats.steps = app.stats.placements = 36
        app.stats.elapsed_seconds = .0025
        app.started_at = time.perf_counter()-9.0
        app.attempt_date = '2026-09-17T14:20'
        app.finish('Resuelto')
        capture('resumen')
    finally:
        app.close()
        directory.cleanup()

if __name__ == '__main__':
    main()
