"""Analizador determinista interno del generador."""
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from .model import Grid, Sudoku

LEVELS = ('Fácil', 'Intermedio', 'Difícil', 'Extremo')
UNITS = ([[ (r,c) for c in range(9)] for r in range(9)]
         + [[(r,c) for r in range(9)] for c in range(9)]
         + [[(r,c) for r in range(br,br+3) for c in range(bc,bc+3)]
            for br in range(0,9,3) for bc in range(0,9,3)])
PEERS = {(r,c): set().union(*(set(u) for u in UNITS if (r,c) in u)) - {(r,c)}
         for r in range(9) for c in range(9)}

@dataclass(frozen=True)
class DifficultyReport:
    level: str
    clues: int
    placements: int
    eliminations: int
    techniques: dict[str,int]
    remaining: int

    @property
    def solved(self):
        return self.remaining == 0

def analyze(grid: Grid) -> DifficultyReport:
    board = Sudoku(grid)
    if not board.is_valid():
        raise ValueError('Pistas contradictorias.')
    options = {(r,c): board.candidates(r,c) for r in range(9) for c in range(9) if not grid[r][c]}
    clues = 81-len(options)
    techniques = Counter()
    placements = eliminations = rank = 0
    while options:
        if any(not v for v in options.values()):
            raise ValueError('Candidatos inconsistentes.')
        move = next(((p,min(v)) for p,v in options.items() if len(v)==1),None)
        technique = 'Single desnudo'
        if move is None:
            for unit in UNITS:
                for n in range(1,10):
                    cells = [p for p in unit if n in options.get(p,())]
                    if len(cells)==1:
                        move = cells[0],n
                        break
                if move:
                    break
            if move:
                technique = 'Single oculto'
                rank = max(rank,1)
        if move:
            cell,n = move
            del options[cell]
            for peer in PEERS[cell]:
                if peer in options:
                    options[peer].discard(n)
            placements += 1
            techniques[technique] += 1
            continue
        removed = set()
        for source in UNITS:
            for n in range(1,10):
                cells = {p for p in source if n in options.get(p,())}
                if len(cells)<2:
                    continue
                for target in UNITS:
                    if source != target and cells <= set(target):
                        removed = {(p,n) for p in target if p not in source and n in options.get(p,())}
                        if removed:
                            break
                if removed:
                    break
            if removed:
                break
        technique = 'Candidatos bloqueados'
        if not removed:
            technique = 'Par desnudo'
            for unit in UNITS:
                pairs = [p for p in unit if len(options.get(p,()))==2]
                for a,b in combinations(pairs,2):
                    if options[a]==options[b]:
                        removed = {(p,n) for p in unit if p not in (a,b)
                                   for n in options[a] if n in options.get(p,())}
                        if removed:
                            break
                if removed:
                    break
        if not removed:
            rank = 3
            break
        for p,n in removed:
            options[p].remove(n)
        eliminations += len(removed)
        techniques[technique] += 1
        rank = max(rank,2)
    return DifficultyReport(LEVELS[rank],clues,placements,eliminations,dict(techniques),len(options))
