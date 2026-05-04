# Motor de Busca em Documentos

Trabalho Prático — Algoritmos Avançados  
Prof. Diogo Vinicius Winck — Católica de Santa Catarina

---

## Estrutura do Projeto

```
motor-busca/
├── app.py                    # Servidor Flask (rotas e API)
├── requirements.txt
├── templates/
│   └── index.html            # Interface web
└── algorithms/
    ├── __init__.py
    ├── base.py               # SearchStrategy (interface) + SearchResult
    ├── registry.py           # ← ADICIONE SEUS ALGORITMOS AQUI
    ├── forca_bruta.py        # ✅ Implementado
    ├── rabin_karp.py         # ✅ Implementado
    ├── kmp.py                # 🔲 A colega implementa
    └── boyer_moore.py        # 🔲 A colega implementa
```

---

## Como Rodar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Rodar o servidor
python app.py

# 3. Acessar no navegador
http://localhost:5000
```

---

## Como a Colega Adiciona os Algoritmos

### 1. Criar o arquivo `algorithms/kmp.py`

```python
from typing import List
from .base import SearchStrategy

class KMP(SearchStrategy):
    def name(self) -> str:
        return "KMP"

    def _search(self, text: str, pattern: str) -> List[int]:
        # Implementação aqui
        pass
```

### 2. Registrar em `algorithms/registry.py`

Descomente as linhas já preparadas:

```python
from .kmp import KMP
from .boyer_moore import BoyerMoore

ALGORITHMS = {
    "forca_bruta": ForcaBruta(),
    "rabin_karp": RabinKarp(),
    "kmp": KMP(),           # ← descomentar
    "boyer_moore": BoyerMoore(),  # ← descomentar
}
```

O dropdown na interface vai aparecer automaticamente. ✅

---

## API

### `GET /api/algorithms`
Retorna lista de algoritmos disponíveis.

### `POST /api/search`
**Form data:**
- `file` — arquivo `.txt`
- `pattern` — termo a buscar
- `algorithm` — chave do algoritmo (`forca_bruta`, `rabin_karp`, `kmp`, `boyer_moore`)

**Resposta:**
```json
{
  "algorithm": "Força Bruta",
  "found": true,
  "occurrences": 42,
  "positions": [10, 55, 100, ...],
  "positions_truncated": false,
  "duration_ms": 12.3456,
  "text_size": 4000000,
  "pattern_size": 5
}
```

---

## Algoritmos Implementados

| Algoritmo | Complexidade | Arquivo |
|---|---|---|
| Força Bruta | O(N·M) pior caso | `forca_bruta.py` |
| Rabin-Karp | O(N+M) esperado | `rabin_karp.py` |
| KMP | O(N+M) garantido | `kmp.py` *(colega)* |
| Boyer-Moore | O(N/M) melhor caso | `boyer_moore.py` *(colega)* |

---

## Próximos Passos (OpenTelemetry)

A instrumentação com OpenTelemetry (seção 5 do enunciado) pode ser adicionada em `app.py` na rota `/api/search`, após o `result = strategy.search(...)`.
