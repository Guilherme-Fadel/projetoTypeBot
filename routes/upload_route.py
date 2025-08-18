from flask import Blueprint, request, jsonify
from services.s3_uploader import upload_file_to_s3

upload_bp = Blueprint('upload_bp', __name__)

@upload_bp.route('/upload-to-s3', methods=['POST'])
def upload_to_s3():
    data = request.json
    file_url = data.get('fileUrl')
    file_name = data.get('fileName', 'arquivo_enviado')

    if not file_url:
        return jsonify({'error': 'URL do arquivo não fornecida'}), 400

    result = upload_file_to_s3(file_url, file_name)

    if result['success']:
        return jsonify({'message': 'Upload feito com sucesso!', 'file': result['file']}), 200
    else:
        return jsonify({'error': result['error']}), 500
