from __future__ import annotations

import random

from .model import Grid


def candidates(grid: Grid, row: int, col: int) -> set[int]:
    if grid[row][col]:
        return set()
    used = set(grid[row])
    used.update(grid[r][col] for r in range(9))
    br, bc = (row // 3) * 3, (col // 3) * 3
    used.update(grid[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3))
    return set(range(1, 10)) - used


def solve_grid(grid: Grid, *, randomized: bool = False) -> bool:
    """Resuelve in-place con MRV. Se usa para generar, no como algoritmo visual."""
    empty: list[tuple[int, int, set[int]]] = []
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                options = candidates(grid, row, col)
                if not options:
                    return False
                empty.append((row, col, options))
    if not empty:
        return True
    row, col, options = min(empty, key=lambda item: len(item[2]))
    values = list(options)
    if randomized:
        random.shuffle(values)
    for value in values:
        grid[row][col] = value
        if solve_grid(grid, randomized=randomized):
            return True
    grid[row][col] = 0
    return False


def count_solutions(grid: Grid, limit: int = 2, *, checkpoint=lambda: None) -> int:
    """Cuenta como máximo ``limit`` soluciones sin conservar cambios."""
    checkpoint()
    best: tuple[int, int, set[int]] | None = None
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                options = candidates(grid, row, col)
                if not options:
                    return 0
                if best is None or len(options) < len(best[2]):
                    best = (row, col, options)
    if best is None:
        return 1
    row, col, options = best
    total = 0
    try:
        for value in options:
            grid[row][col] = value
            total += count_solutions(grid, limit - total, checkpoint=checkpoint)
            if total >= limit:
                break
    finally:
        grid[row][col] = 0
    return total
