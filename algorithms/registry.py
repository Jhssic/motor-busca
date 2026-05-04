from .forca_bruta import ForcaBruta
from .rabin_karp import RabinKarp
from .kmp import KMP
from .boyer_moore import BoyerMoore

ALGORITHMS = {
    "forca_bruta": ForcaBruta(),
    "rabin_karp": RabinKarp(),
    "kmp": KMP(),
    "boyer_moore": BoyerMoore(),
}

def get_algorithm(name: str):
    if name not in ALGORITHMS:
        raise ValueError(f"Algoritmo não encontrado: {name}")
    return ALGORITHMS[name]

def list_algorithms():
    return list(ALGORITHMS.keys())