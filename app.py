from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os

from algorithms.registry import get_algorithm, list_algorithms

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB máximo
ALLOWED_EXTENSIONS = {"txt"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    algorithms = list_algorithms()
    return render_template("index.html", algorithms=algorithms)


@app.route("/api/algorithms")
def api_algorithms():
    return jsonify(list_algorithms())


@app.route("/api/search", methods=["POST"])
def api_search():
    # Validação do arquivo
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Arquivo inválido. Envie um .txt"}), 400

    # Leitura do texto
    try:
        text = file.read().decode("utf-8")
    except UnicodeDecodeError:
        try:
            file.seek(0)
            text = file.read().decode("latin-1")
        except Exception:
            return jsonify({"error": "Não foi possível decodificar o arquivo."}), 400

    # Validação dos parâmetros
    pattern = request.form.get("pattern", "").strip()
    algorithm_key = request.form.get("algorithm", "").strip()

    if not pattern:
        return jsonify({"error": "Informe o termo a pesquisar."}), 400

    if not algorithm_key:
        return jsonify({"error": "Selecione um algoritmo."}), 400

    # Execução da busca
    try:
        strategy = get_algorithm(algorithm_key)
        result = strategy.search(text, pattern)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Erro na busca: {str(e)}"}), 500

    # Retorna só as primeiras 200 posições para não explodir o JSON em textos grandes
    positions_preview = result.positions[:200]

    return jsonify({
        "algorithm": result.algorithm,
        "found": result.found,
        "occurrences": result.occurrences,
        "positions": positions_preview,
        "positions_truncated": len(result.positions) > 200,
        "duration_ms": result.duration_ms,
        "text_size": result.text_size,
        "pattern_size": result.pattern_size,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
