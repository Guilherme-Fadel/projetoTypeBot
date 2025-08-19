import requests
import json
import os
import boto3

def update_description(file_url: str, file_name: str, file_description: str):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

        bucket = os.getenv('S3_BUCKET')
        json_key = 'images/imagens.json'

        try:
            response = s3.get_object(Bucket=bucket, Key=json_key)
            imagens = json.loads(response['Body'].read().decode('utf-8'))
        except s3.exceptions.NoSuchKey:
            imagens = []

        nova_imagem = {
            "nome": file_name,
            "descricao": file_description,
            # 👇 sempre usa a URL fixa
            "url": f"https://typebotstorage-mkteste.s3.us-east-1.amazonaws.com/{file_name}"
        }
        imagens.append(nova_imagem)

        s3.put_object(
            Bucket=bucket,
            Key=json_key,
            Body=json.dumps(imagens, indent=2, ensure_ascii=False).encode('utf-8'),
            ContentType='application/json',
            ACL="public-read"
        )

        return {"success": True, "file": nova_imagem}

    except Exception as e:
        return {"success": False, "error": str(e)}
