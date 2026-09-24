import importlib
import inspect
import pkgutil
import soluciones
from .algorithm import SolvingAlgorithm
from .diagnostics import print_current_exception

def discover():
    found, errors = [], []
    for entry in sorted(pkgutil.iter_modules(soluciones.__path__),key=lambda x:x.name, reverse=True):
        if entry.name.startswith('_'):
            continue
        try:
            module = importlib.import_module(f'soluciones.{entry.name}')
            for _,cls in inspect.getmembers(module,inspect.isclass):
                if (cls.__module__ == module.__name__ and issubclass(cls,SolvingAlgorithm)
                        and not inspect.isabstract(cls)):
                    if not isinstance(cls.name,str) or not cls.name.strip():
                        raise ValueError('Nombre de algoritmo inválido.')
                    found.append(cls)
        except Exception as exc:
            print_current_exception(f'No se pudo cargar soluciones.{entry.name}')
            errors.append(f'{entry.name}: {type(exc).__name__}: {exc}')
    return found,errors
