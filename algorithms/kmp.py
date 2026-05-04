from typing import List
from .base import SearchStrategy


class KMP(SearchStrategy):
    """
    Algoritmo Knuth-Morris-Pratt (KMP).
    Complexidade: O(N + M) garantido — usa tabela de falhas (failure function)
    para nunca regredir no texto, evitando comparações redundantes.
    """

    def name(self) -> str:
        return "KMP"

    def _build_failure_table(self, pattern: str) -> List[int]:
        """
        Constrói a tabela de falhas (também chamada de prefix function).
        failure[i] = tamanho do maior prefixo próprio de pattern[0..i]
        que também é sufixo.
        """
        m = len(pattern)
        failure = [0] * m
        j = 0  # comprimento do prefixo atual

        for i in range(1, m):
            # Regride pelo prefixo enquanto não há correspondência
            while j > 0 and pattern[i] != pattern[j]:
                j = failure[j - 1]

            if pattern[i] == pattern[j]:
                j += 1

            failure[i] = j

        return failure

    def _search(self, text: str, pattern: str) -> List[int]:
        n = len(text)
        m = len(pattern)

        if m == 0:
            return []

        failure = self._build_failure_table(pattern)
        positions = []
        j = 0  # número de caracteres do padrão já correspondidos

        for i in range(n):
            # Regride pelo prefixo enquanto não há correspondência
            while j > 0 and text[i] != pattern[j]:
                j = failure[j - 1]

            if text[i] == pattern[j]:
                j += 1

            if j == m:
                # Padrão encontrado: posição de início
                positions.append(i - m + 1)
                # Regredir para continuar procurando sobreposições
                j = failure[j - 1]

        return positions