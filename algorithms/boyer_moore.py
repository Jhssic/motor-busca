from typing import List, Dict
from .base import SearchStrategy


class BoyerMoore(SearchStrategy):
    """
    Algoritmo Boyer-Moore.
    Complexidade: O(N/M) melhor caso (sublinear), O(N·M) pior caso.
    Usa duas heurísticas: Bad Character e Good Suffix.
    Muito eficiente para texto natural com alfabeto grande.
    """

    def name(self) -> str:
        return "Boyer-Moore"

    def _build_bad_character_table(self, pattern: str) -> Dict[str, int]:
        """
        Tabela de Bad Character:
        Para cada caractere, armazena a posição da última ocorrência no padrão.
        Usada para pular o texto quando há um mismatch.
        """
        table: Dict[str, int] = {}
        for i, ch in enumerate(pattern):
            table[ch] = i
        return table

    def _build_good_suffix_table(self, pattern: str) -> List[int]:
        """
        Tabela de Good Suffix:
        shift[i] = quantas posições pular quando o mismatch ocorre em pattern[i-1].
        Baseia-se em sufixos do padrão que já foram correspondidos.
        """
        m = len(pattern)
        shift = [m] * (m + 1)
        border = [0] * (m + 1)

        # Fase 1: calcular o border (maior borda do sufixo)
        i = m
        j = m + 1
        border[i] = j

        while i > 0:
            while j <= m and pattern[i - 1] != pattern[j - 1]:
                if shift[j] == m:
                    shift[j] = j - i
                j = border[j]
            i -= 1
            j -= 1
            border[i] = j

        # Fase 2: preencher shifts restantes usando o border de todo o padrão
        j = border[0]
        for i in range(m + 1):
            if shift[i] == m:
                shift[i] = j
            if i == j:
                j = border[j]

        return shift

    def _search(self, text: str, pattern: str) -> List[int]:
        n = len(text)
        m = len(pattern)

        if m == 0:
            return []

        bad_char = self._build_bad_character_table(pattern)
        good_suffix = self._build_good_suffix_table(pattern)

        positions = []
        s = 0  # deslocamento do padrão sobre o texto

        while s <= n - m:
            j = m - 1  # compara da direita para a esquerda

            while j >= 0 and pattern[j] == text[s + j]:
                j -= 1

            if j < 0:
                # Padrão encontrado
                positions.append(s)
                # Avançar usando a tabela de good suffix
                s += good_suffix[0]
            else:
                # Mismatch: usar o máximo entre bad character e good suffix
                bc_shift = j - bad_char.get(text[s + j], -1)
                gs_shift = good_suffix[j + 1]
                s += max(bc_shift, gs_shift)

        return positions