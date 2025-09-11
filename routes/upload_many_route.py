from flask import Blueprint, request, jsonify
import requests
import json
import logging
import os
from urllib.parse import urlparse
from services.s3_uploader import upload_file_to_s3
from services.data_uploader import update_description

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
                prefix = '"links":'
                start = raw_data.find(prefix) + len(prefix)
                link_str = raw_data[start:].strip().rstrip('}').strip()
                link_str = link_str.replace('\n', '').replace('"', '').strip()

                url_list = [url.strip() for url in link_str.split(',')]
                data = {'links': url_list}
            else:
                return jsonify({'error': 'Campo "links" não encontrado'}), 400

        file_urls = data.get('links')
        if not file_urls:
            return jsonify({'error': 'URLs dos arquivos não fornecidas'}), 400

        if isinstance(file_urls, str):
            url_list = [url.strip() for url in file_urls.split(',')]
        elif isinstance(file_urls, list):
            url_list = [str(url).strip() for url in file_urls]
        else:
            return jsonify({'error': 'Formato inválido para links'}), 400

        url_map = {os.path.basename(urlparse(url).path): url for url in url_list}

        response = requests.post(
            "http://localhost:5000/analyze-files",
            json={"links": [{"url": url} for url in url_list]},
            timeout=120
        )

        if response.status_code != 200:
            return jsonify({'error': 'Erro ao analisar os arquivos'}), response.status_code

        uploaded_files = []
        for file_info in response.json().get('links', []):
            file_name = file_info.get('filename')
            file_url = url_map.get(file_name)

            if not file_url:
                logger.warning(f"URL não encontrada para {file_name}")
                continue

            result = upload_file_to_s3(file_url, file_name)
            if result.get("success"):
                desc_result = update_description(file_name, file_info)
                if desc_result.get("success"):
                    uploaded_files.append(desc_result['file'])
                else:
                    logger.warning(f"Descrição não atualizada para {file_name}: {desc_result.get('error')}")
            else:
                logger.error(f"Erro ao subir {file_url}: {result.get('error')}")

        return jsonify({
            'message': 'Upload concluído!',
            'files': uploaded_files
        }), 200

    except Exception as e:
        logger.exception("Erro inesperado no upload múltiplo")
        return jsonify({'error': f'Erro inesperado: {str(e)}'}), 500
