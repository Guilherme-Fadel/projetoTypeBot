import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError
import os


def upload_file_to_s3(file_url: str, file_name: str) -> dict:
    try:
        response = requests.get(file_url)
        response.raise_for_status()

        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

        s3.put_object(
            Bucket=os.getenv('S3_BUCKET'),
            Key=file_name,
            Body=response.content,
            ContentType=response.headers.get(
                'Content-Type', 'application/octet-stream'),
            ACL='public-read'
        )

        return {'success': True, 'file': file_name}

    except (requests.RequestException, BotoCoreError, ClientError) as e:
        return {'success': False, 'error': str(e)}


def upload_local_file_to_s3(local_path: str, s3_key: str) -> str:
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

    with open(local_path, 'rb') as f:
        s3.put_object(
            Bucket=os.getenv('S3_BUCKET'),
            Key=s3_key,
            Body=f,
            ContentType='image/png',
            ACL='public-read'
        )

    return f"https://{os.getenv('S3_BUCKET')}.s3.amazonaws.com/{s3_key}"
