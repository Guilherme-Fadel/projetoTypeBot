''' Rota legada para upload de arquivos para S3

from flask import Blueprint, request, jsonify
from services.s3_uploader import upload_file_to_s3
from services.data_uploader import update_description

upload_bp = Blueprint('upload_bp', __name__)

@upload_bp.route('/upload-to-s3', methods=['POST'])
def upload_to_s3():
    data = request.json
    file_url = data.get('fileUrl')
    file_name = data.get('fileName', 'fileName')
    file_description = data.get('fileDescription', 'fileDescription')

    if not file_url:
        return jsonify({'error': 'URL do arquivo não fornecida'}), 400

    result = upload_file_to_s3(file_url, file_name)
    description = update_description(file_name, file_description)

    if result.get("success") and description.get("success"):
        return jsonify({
            'message': 'Upload feito com sucesso!',
            'file': result['file']
        }), 200
    else:
            return jsonify({
                'error': result.get('error', 'Erro desconhecido')
            }), 500
'''
    