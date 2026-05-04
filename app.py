import logging
import os

from flask import Flask, request, jsonify, render_template

# OpenTelemetry
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# Algoritmos
from algorithms.registry import ALGORITHMS

OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

resource = Resource.create({"service.name": "motor-busca"})

# Traces
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True))
)
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("motor-busca")

# Métricas
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=OTEL_ENDPOINT, insecure=True),
    export_interval_millis=5_000,
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("motor-busca")

search_duration_histogram = meter.create_histogram(
    name="search_duration_ms",
    description="Duração da busca em milissegundos",
    unit="ms",
)
search_requests_counter = meter.create_counter(
    name="search_requests_total",
    description="Total de requisições de busca realizadas",
)
document_size_histogram = meter.create_histogram(
    name="document_size_chars",
    description="Tamanho do documento em caracteres",
    unit="chars",
)

# Logs
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(endpoint=OTEL_ENDPOINT, insecure=True))
)
set_logger_provider(logger_provider)

otel_handler = LoggingHandler(level=logging.DEBUG, logger_provider=logger_provider)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), otel_handler],
)
logger = logging.getLogger("motor-busca")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB


def extract_text(file) -> str:
    """Extrai texto de arquivos .txt ou .pdf."""
    filename = file.filename.lower()
    raw = file.read()

    if filename.endswith(".pdf"):
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=raw, filetype="pdf")
            return "\n".join(page.get_text() for page in doc)
        except Exception as e:
            raise ValueError(f"Erro ao extrair texto do PDF: {e}")

    # TXT — tenta UTF-8, cai para latin-1
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


@app.route("/")
def index():
    algorithms = [{"key": key, "name": algo.name()} for key, algo in ALGORITHMS.items()]
    return render_template("index.html", algorithms=algorithms)


@app.route("/api/algorithms")
def get_algorithms():
    return jsonify(
        [{"key": key, "name": algo.name()} for key, algo in ALGORITHMS.items()]
    )


@app.route("/api/search", methods=["POST"])
def search():
    with tracer.start_as_current_span("search_request") as root_span:

        algorithm_key = request.form.get("algorithm", "forca_bruta")
        pattern = request.form.get("pattern", "")
        file = request.files.get("file")

        if not file:
            return jsonify({"error": "Nenhum arquivo enviado."}), 400
        if not pattern:
            return jsonify({"error": "Padrão de busca não informado."}), 400
        if algorithm_key not in ALGORITHMS:
            return jsonify({"error": f"Algoritmo '{algorithm_key}' não encontrado."}), 400

        strategy = ALGORITHMS[algorithm_key]
        root_span.set_attribute("algorithm", algorithm_key)
        root_span.set_attribute("pattern", pattern)

        # Leitura e extração do arquivo
        with tracer.start_as_current_span("load_document") as file_span:
            try:
                text = extract_text(file)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
            except Exception as e:
                file_span.record_exception(e)
                return jsonify({"error": "Erro ao ler o arquivo."}), 500

            n = len(text)
            m = len(pattern)
            file_span.set_attribute("document_size_chars", n)
            file_span.set_attribute("pattern_size_chars", m)
            file_span.set_attribute("file_type", file.filename.rsplit(".", 1)[-1].lower())

        logger.info(
            "Iniciando busca | algoritmo=%s | N=%d | M=%d",
            strategy.name(), n, m,
        )

        # Execução do algoritmo
        with tracer.start_as_current_span("execute_algorithm") as algo_span:
            algo_span.set_attribute("algorithm.name", strategy.name())
            algo_span.set_attribute("text.length", n)
            algo_span.set_attribute("pattern.length", m)
            result = strategy.search(text, pattern)

        # Formatação do resultado
        with tracer.start_as_current_span("format_result"):
            found = result.found
            occurrences = result.occurrences
            duration_ms = result.duration_ms
            positions = result.positions
            positions_truncated = len(positions) > 500
            positions_display = positions[:500] if positions_truncated else positions

        # Métricas
        labels = {"algorithm": algorithm_key, "found": str(found).lower()}
        search_duration_histogram.record(duration_ms, attributes=labels)
        search_requests_counter.add(1, attributes=labels)
        document_size_histogram.record(n, attributes={"algorithm": algorithm_key})

        root_span.set_attribute("result.found", found)
        root_span.set_attribute("result.occurrences", occurrences)
        root_span.set_attribute("result.duration_ms", duration_ms)

        logger.info(
            "Busca concluída | algoritmo=%s | encontrado=%s | ocorrências=%d | tempo=%.3f ms",
            strategy.name(), found, occurrences, duration_ms,
        )

        return jsonify({
            "algorithm": strategy.name(),
            "found": found,
            "occurrences": occurrences,
            "positions": positions_display,
            "positions_truncated": positions_truncated,
            "duration_ms": round(duration_ms, 4),
            "text_size": n,
            "pattern_size": m,
        })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)