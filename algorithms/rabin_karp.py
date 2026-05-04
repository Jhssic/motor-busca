from typing import List
from .base import SearchStrategy


class RabinKarp(SearchStrategy):
    """
    Algoritmo Rabin-Karp — O(N+M) esperado, usando hash rolante.

    Calcula o hash do padrão e vai rolando uma janela de tamanho M no texto.
    Só compara caractere a caractere quando os hashes batem (evita falsos positivos).
    """

    BASE = 256       # número de caracteres possíveis (ASCII)
    MOD = 101        # número primo para reduzir colisões

    def name(self) -> str:
        return "Rabin-Karp"

    def _search(self, text: str, pattern: str) -> List[int]:
        n = len(text)
        m = len(pattern)
        positions = []

        if m == 0 or m > n:
            return positions

        base = self.BASE
        mod = self.MOD

        # h = base^(m-1) % mod  → usado para remover o caractere que sai da janela
        h = pow(base, m - 1, mod)

        # Hash inicial do padrão e da primeira janela do texto
        hash_pattern = 0
        hash_window = 0
        for i in range(m):
            hash_pattern = (base * hash_pattern + ord(pattern[i])) % mod
            hash_window = (base * hash_window + ord(text[i])) % mod

        for i in range(n - m + 1):
            if hash_pattern == hash_window:
                # Verificação caractere a caractere (evita falso positivo)
                if text[i:i + m] == pattern:
                    positions.append(i)

            # Rola a janela: remove text[i], adiciona text[i+m]
            if i < n - m:
                hash_window = (
                    base * (hash_window - ord(text[i]) * h) + ord(text[i + m])
                ) % mod

                # Garante que o hash seja não-negativo
                if hash_window < 0:
                    hash_window += mod

        return positions
