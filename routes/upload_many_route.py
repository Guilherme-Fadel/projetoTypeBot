from flask import Blueprint, request, jsonify
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

upload_many_bp = Blueprint('upload_many_bp', __name__)

@upload_many_bp.route('/upload-many-to-s3', methods=['POST'])
def upload_many_to_s3():
    try:
        raw_data = request.get_data(as_text=True)

        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            if 'links' in raw_data:
                # Extrai os links da string
                prefix = '"links":'
                start = raw_data.find(prefix) + len(prefix)
                link_str = raw_data[start:].strip().rstrip('}').strip()
                link_str = link_str.replace('\n', '').replace('"', '').strip()

                url_list = [url.strip() for url in link_str.split(',')]
                data = {'links': url_list}
            else:
                return jsonify({'error': 'Campo "links" não encontrado'}), 400

        file_url = data.get('links')

        if not file_url:
            return jsonify({'error': 'URLs dos arquivos não fornecidas'}), 400

        if isinstance(file_url, str):
            url_list = [url.strip() for url in file_url.split(',')]
        elif isinstance(file_url, list):
            url_list = [str(url).strip() for url in file_url]
        else:
            return jsonify({'error': 'Formato inválido para links'}), 400

        url_json = [{"url": url} for url in url_list]

        response = requests.post(
            "http://localhost:5000/analyze-files",
            json={"links": url_json},
            timeout=120
        )
        logger.info(url_json)
        print(jsonify(response.json()), response.status_code)
        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({'error': f'Erro inesperado: {str(e)}'}), 500
