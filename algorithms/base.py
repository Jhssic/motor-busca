from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List
import time


@dataclass
class SearchResult:
    positions: List[int]
    occurrences: int
    found: bool
    duration_ms: float
    text_size: int      # N
    pattern_size: int   # M
    algorithm: str


class SearchStrategy(ABC):
    """Interface comum para todos os algoritmos de busca — Strategy Pattern."""

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def _search(self, text: str, pattern: str) -> List[int]:
        """Retorna lista de posições onde o padrão foi encontrado."""
        pass

    def search(self, text: str, pattern: str) -> SearchResult:
        start = time.perf_counter()
        positions = self._search(text, pattern)
        elapsed_ms = (time.perf_counter() - start) * 1000

        return SearchResult(
            positions=positions,
            occurrences=len(positions),
            found=len(positions) > 0,
            duration_ms=round(elapsed_ms, 4),
            text_size=len(text),
            pattern_size=len(pattern),
            algorithm=self.name(),
        )
