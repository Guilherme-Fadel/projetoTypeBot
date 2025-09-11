from flask import Blueprint, request, jsonify
from services.file_analyzer import analyze_file
from urllib.parse import urlparse
import os

analyze_files_bp = Blueprint("analyze_files_bp", __name__)

@analyze_files_bp.route("/analyze-files", methods=["POST"])
def analyze_files():
    data = request.json
    files = data.get("links", [])

    if not files or not isinstance(files, list):
        return jsonify({"error": "Envie uma lista no campo 'links'"}), 400

    results = []

    for file in files:
        url = file.get("url")
        if not url:
            continue

        path = urlparse(url).path
        filename = os.path.basename(path) or "desconhecido"

        analysis = analyze_file(url, filename)
        print(f"[ANÁLISE] {filename} →", analysis)

        results.append(analysis)

    return jsonify({"links": results}), 200
