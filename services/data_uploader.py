import requests
import json
import os


def update_description(file_url: str, file_name: str, file_description: str) -> dict:
    try:
        json_path = os.path.join('data', 'imagens.json')
        if not os.path.exists(json_path):
            with open(json_path, 'w') as f:
                json.dump([], f)

        with open(json_path, 'r', encoding='utf-8') as f:
            imagens = json.load(f)

        nova_imagem = {
            "nome": file_name,
            "descricao": file_description,
            "url": f"https://typebotstorage-mkteste.s3.us-east-1.amazonaws.com/{file_name}"
        }

        imagens.append(nova_imagem)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(imagens, f, indent=2, ensure_ascii=False)

        return {'success': True, 'message': 'Descrição atualizada com sucesso'}

    except Exception as e:
        return {'success': False, 'error': str(e)}
