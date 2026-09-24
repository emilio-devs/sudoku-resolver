from __future__ import annotations

from collections.abc import Iterator

from sudoku.algorithm import SolvingAlgorithm, Step

import random

class NakedSingles(SolvingAlgorithm):
    name = "0. Candidato único"
    description = "Rellena con un numero fijo"

    def solve(self) -> Iterator[Step]:
        while True:
            progress = False
            for row in range(9):
                for col in range(9):
                    if self.board[row][col]:
                        number = random.randint(1, 9)
                        yield self.place(row, col, number, "Se añade un número aleatorio a ver si cuela")
                        progress = True

            if not progress:
                return
