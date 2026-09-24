"""Salida de diagnóstico para fallos recuperados por la interfaz."""
from __future__ import annotations

import sys
import traceback


def print_current_exception(context: str) -> None:
    """Imprime el traceback activo sin propagar la excepción."""
    print(f'\n[Sudoku Studio] {context}', file=sys.stderr, flush=True)
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
