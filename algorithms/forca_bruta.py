from typing import List
from .base import SearchStrategy


class ForcaBruta(SearchStrategy):
    """
    Algoritmo Força Bruta (Naive Search) — O(N·M) pior caso.

    Para cada posição i no texto, compara caractere a caractere com o padrão.
    Se todos batem, registra a posição.
    """

    def name(self) -> str:
        return "Força Bruta"

    def _search(self, text: str, pattern: str) -> List[int]:
        n = len(text)
        m = len(pattern)
        positions = []

        if m == 0 or m > n:
            return positions

        for i in range(n - m + 1):
            j = 0
            while j < m and text[i + j] == pattern[j]:
                j += 1
            if j == m:
                positions.append(i)

        return positions
