# Motor de Busca em Documentos

**Trabalho Prático — Algoritmos Avançados**  
Prof. Diogo Vinicius Winck — Católica de Santa Catarina

Alunos:
Jhessica Alves
Laíza Silva
Victor Moy

Aplicação web para pesquisa de padrões em documentos de texto e PDF, com quatro algoritmos de substring search, instrumentação OpenTelemetry completa (traces, métricas e logs) e dashboard Grafana + Prometheus via docker-compose.

---

## Sumário

1. [Funcionalidades](#funcionalidades)
2. [Algoritmos Implementados](#algoritmos-implementados)
3. [Estrutura do Projeto](#estrutura-do-projeto)
4. [Instalação e Execução](#instalação-e-execução)
5. [Observabilidade — OpenTelemetry](#observabilidade--opentelemetry)
6. [Dashboard — Grafana + Prometheus](#dashboard--grafana--prometheus)
7. [API](#api)
8. [Uso de IA](#uso-de-ia)

---

## Funcionalidades

- Upload de arquivos `.txt` e `.pdf` (até 20 MB)
- Seleção do algoritmo via dropdown em tempo de execução
- Exibe: encontrado?, número de ocorrências, posições (índices), tempo em ms, tamanho N e M
- Telemetria completa com OpenTelemetry: traces, métricas e logs
- Dashboard Grafana pré-configurado com Prometheus via docker-compose

---

## Algoritmos Implementados

| Algoritmo | Complexidade | Estratégia |
|-----------|-------------|------------|
| Força Bruta | O(N·M) pior caso | Comparação caractere a caractere |
| Rabin-Karp | O(N+M) esperado | Hash rolante |
| KMP | O(N+M) garantido | Tabela de falhas (prefix function) |
| Boyer-Moore | O(N/M) melhor caso | Bad character + Good suffix |

Todos implementados sem uso de `indexOf()`, `contains()` ou similares como lógica central, seguindo o **Strategy Pattern** com interface comum `SearchStrategy`.

---

## Estrutura do Projeto

```
motor-busca/
├── app.py                          # Servidor Flask com OpenTelemetry
├── requirements.txt
├── Dockerfile                      # Imagem da aplicação
├── docker-compose.yml              # App + stack de observabilidade completa
├── algorithms/
│   ├── __init__.py
│   ├── base.py                     # SearchStrategy + SearchResult
│   ├── registry.py                 # Registro dos algoritmos
│   ├── forca_bruta.py
│   ├── rabin_karp.py
│   ├── kmp.py
│   └── boyer_moore.py
├── templates/
│   └── index.html
└── monitoring/
    ├── otel-collector.yaml
    ├── prometheus.yml
    ├── tempo.yaml
    └── grafana/
        └── provisioning/
            ├── datasources/datasources.yaml
            └── dashboards/
                ├── dashboards.yaml
                └── motor-busca.json
```

---

## Instalação e Execução

### Pré-requisitos

- Docker e Docker Compose

### Opção 1 — Tudo via Docker (recomendado)

Sobe a aplicação + toda a stack de observabilidade com um único comando:

```bash
docker compose up --build
```

| Serviço | URL | Função |
|---------|-----|--------|
| App Flask | http://localhost:5000 | Interface de busca |
| Grafana | http://localhost:3000 | Dashboard (admin/admin) |
| Prometheus | http://localhost:9090 | Métricas |
| OTEL Collector | localhost:4317 | Recebe telemetria |
| Grafana Tempo | localhost:3200 | Traces |

Para encerrar:
```bash
docker compose down -v
```

### Opção 2 — Execução local (sem Docker)

```bash
git clone https://github.com/Jhssic/motor-busca
cd motor-busca
pip install -r requirements.txt
python app.py
```

Acesse em: **http://localhost:5000**

> Sem Docker, a app funciona normalmente. Os exportadores OTEL falham silenciosamente sem quebrar a aplicação.

---

## Observabilidade — OpenTelemetry

A aplicação é instrumentada com OpenTelemetry SDK para Python, registrando **traces**, **métricas** e **logs** a cada operação de busca.

### Traces

Cada requisição de busca gera um trace com 3 spans:

| Span | O que registra |
|------|----------------|
| `load_document` | Leitura e extração do arquivo (txt ou pdf), tamanho N |
| `execute_algorithm` | Execução do algoritmo escolhido, tempo real |
| `format_result` | Formatação da resposta antes de retornar ao cliente |

### Métricas

| Métrica | Tipo | Labels |
|---------|------|--------|
| `search_duration_ms` | Histogram | algorithm, found |
| `search_requests_total` | Counter | algorithm, found |
| `document_size_chars` | Histogram | algorithm |

### Logs

- **Ao iniciar a busca:** algoritmo utilizado, N e M
- **Ao finalizar:** tempo de execução e número de ocorrências

Os dados são exportados via **OTLP gRPC** para o OpenTelemetry Collector (porta 4317).

---

## Dashboard — Grafana + Prometheus

Após subir com `docker compose up --build`, acesse **http://localhost:3000** (admin/admin).

O dashboard **Motor de Busca — Observabilidade** exibe automaticamente:
- Total de buscas por algoritmo
- Taxa de buscas por minuto
- Tempo médio de execução por algoritmo (ms)
- Percentis P50, P95 e P99 de duração
- Comparação visual entre algoritmos (barchart)
- Proporção encontrado vs não encontrado
- Taxa de sucesso (%)

### Traces no Grafana Tempo

Em **Explore → Tempo**, filtre por `service.name = motor-busca` para ver os traces de cada busca com os 3 spans detalhados.

---

## API

### `GET /api/algorithms`

Retorna lista de algoritmos disponíveis.

```json
[
  { "key": "forca_bruta", "name": "Força Bruta" },
  { "key": "rabin_karp",  "name": "Rabin-Karp"  },
  { "key": "kmp",         "name": "KMP"          },
  { "key": "boyer_moore", "name": "Boyer-Moore"  }
]
```

### `POST /api/search`

**Form data:**
- `file` — arquivo `.txt` ou `.pdf`
- `pattern` — termo a buscar
- `algorithm` — chave do algoritmo

**Resposta:**

```json
{
  "algorithm": "KMP",
  "found": true,
  "occurrences": 42,
  "positions": [10, 55, 100],
  "positions_truncated": false,
  "duration_ms": 12.3456,
  "text_size": 4000000,
  "pattern_size": 5
}
```

---

## Uso de IA

**Prompts principais utilizados:**

1. *"Implemente KMP em Python seguindo a interface SearchStrategy do projeto, com explicação da tabela de falhas"*
2. *"Implemente Boyer-Moore com Bad Character e Good Suffix, sem usar indexOf"*
3. *"Configure OpenTelemetry no Flask com traces (3 spans por requisição), métricas histogram/counter e logs via OTLP gRPC"*
4. *"Crie um docker-compose com OTEL Collector, Prometheus, Grafana Tempo e Grafana com datasources e dashboard pré-provisionados"*
5. *"Adicione suporte a extração de texto de PDF usando PyMuPDF antes de passar para o algoritmo de busca"*

**O que a IA produziu:** estrutura dos algoritmos KMP e Boyer-Moore, configuração YAML completa da stack de observabilidade, integração do LoggingHandler OTEL com o logging padrão do Python, extração de texto de PDF, dashboard Grafana em JSON.

**O que foi ajustado manualmente:** nomes das métricas alinhados com o prefixo do Prometheus, portas sem conflito entre Tempo e Collector, passagem da variável `algorithms` para o template Jinja2, testes com os documentos do enunciado.

**Onde a IA foi genérica:** a tabela de good suffix do Boyer-Moore precisou de revisão — a versão inicial não implementava a fase 2 do preenchimento dos shifts restantes via border array.
