from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


Grid = list[list[int]]


def _copy_grid(grid: Iterable[Iterable[int]]) -> Grid:
    copied = [list(row) for row in grid]
    if len(copied) != 9 or any(len(row) != 9 for row in copied):
        raise ValueError("Un sudoku debe ser una cuadrícula de 9 × 9.")
    if any(type(value) is not int or not 0 <= value <= 9 for row in copied for value in row):
        raise ValueError("Las celdas solo pueden contener valores del 0 al 9.")
    return copied


@dataclass
class Sudoku:
    """Estado de una partida. El cero representa una celda vacía."""

    puzzle: Grid
    solution: Grid | None = None
    grid: Grid = field(init=False)
    fixed: set[tuple[int, int]] = field(init=False)

    def __post_init__(self) -> None:
        self.puzzle = _copy_grid(self.puzzle)
        self.solution = _copy_grid(self.solution) if self.solution else None
        self.grid = _copy_grid(self.puzzle)
        self.fixed = {
            (row, col)
            for row in range(9)
            for col in range(9)
            if self.puzzle[row][col] != 0
        }

    def reset(self) -> None:
        self.grid = _copy_grid(self.puzzle)

    def values(self) -> Grid:
        return _copy_grid(self.grid)

    @staticmethod
    def _position(row, col):
        if type(row) is not int or type(col) is not int or not (0 <= row < 9 and 0 <= col < 9):
            raise ValueError('Índices fuera del rango 0–8.')

    def value(self, row, col):
        self._position(row, col)
        return self.grid[row][col]

    def copy(self):
        result = Sudoku(self.puzzle, self.solution)
        result.grid = self.values()
        return result

    def is_correct(self, row, col, value):
        self._position(row, col)
        if self.solution is None:
            raise ValueError('No hay solución de referencia.')
        return type(value) is int and value == self.solution[row][col]

    def candidates(self, row: int, col: int) -> set[int]:
        self._position(row, col)
        if self.grid[row][col] != 0:
            return set()
        used = set(self.grid[row])
        used.update(self.grid[r][col] for r in range(9))
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        used.update(
            self.grid[r][c]
            for r in range(box_row, box_row + 3)
            for c in range(box_col, box_col + 3)
        )
        return set(range(1, 10)) - used

    def can_place(self, row: int, col: int, value: int) -> bool:
        self._position(row, col)
        if type(value) is not int or not 1 <= value <= 9 or (row, col) in self.fixed:
            return False
        previous = self.grid[row][col]
        self.grid[row][col] = 0
        valid = value in self.candidates(row, col)
        self.grid[row][col] = previous
        return valid

    def set_value(self, row: int, col: int, value: int, *, check_solution: bool = False) -> bool:
        self._position(row, col)
        if type(value) is not int or (row, col) in self.fixed or not 0 <= value <= 9:
            return False
        if value and not self.can_place(row, col, value):
            return False
        if check_solution and value and self.solution and self.solution[row][col] != value:
            return False
        self.grid[row][col] = value
        return True

    @staticmethod
    def _unit_valid(values: list[int]) -> bool:
        present = [value for value in values if value]
        return len(present) == len(set(present))

    def is_valid(self) -> bool:
        rows = all(self._unit_valid(row) for row in self.grid)
        columns = all(self._unit_valid([self.grid[r][c] for r in range(9)]) for c in range(9))
        boxes = all(
            self._unit_valid(
                [self.grid[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)]
            )
            for br in range(0, 9, 3)
            for bc in range(0, 9, 3)
        )
        return rows and columns and boxes

    @property
    def is_complete(self) -> bool:
        return all(value != 0 for row in self.grid for value in row)

    @property
    def is_solved(self):
        return self.is_complete and self.is_valid()
