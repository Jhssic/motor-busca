"""
Registro de algoritmos disponíveis.

COMO ADICIONAR UM NOVO ALGORITMO (para a colega):
1. Crie um arquivo em algorithms/ herdando de SearchStrategy
2. Implemente name() e _search()
3. Importe e adicione ao dicionário ALGORITHMS abaixo
"""

from .base import SearchStrategy, SearchResult
from .forca_bruta import ForcaBruta
from .rabin_karp import RabinKarp

# --- A colega deve adicionar os imports dela aqui ---
# from .kmp import KMP
# from .boyer_moore import BoyerMoore

ALGORITHMS: dict[str, SearchStrategy] = {
    "forca_bruta": ForcaBruta(),
    "rabin_karp": RabinKarp(),
    # --- E registrar aqui ---
    # "kmp": KMP(),
    # "boyer_moore": BoyerMoore(),
}


def get_algorithm(key: str) -> SearchStrategy:
    if key not in ALGORITHMS:
        raise ValueError(f"Algoritmo '{key}' não encontrado. Disponíveis: {list(ALGORITHMS.keys())}")
    return ALGORITHMS[key]


def list_algorithms() -> list[dict]:
    return [{"key": k, "name": v.name()} for k, v in ALGORITHMS.items()]
