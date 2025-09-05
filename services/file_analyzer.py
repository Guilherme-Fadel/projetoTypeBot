from services.pdf_image_converter import converter_pdf_para_png
from services.groq_client import chamar_llama_scout, chamar_llama
from services.s3_uploader import upload_local_file_to_s3
from urllib.parse import urlparse
import os

def analyze_file(url: str, filename: str) -> dict:
    ext = filename.split('.')[-1].lower()

    if ext == "pdf":
        # Converte PDF em imagens PNG
        caminho_pdf = url  # URL do PDF
        imagens_png = converter_pdf_para_png(caminho_pdf)

        descricoes = []
        for i, caminho_png in enumerate(imagens_png):
            nome_arquivo = os.path.basename(caminho_png)
            s3_key = f"temp-uploads/{nome_arquivo}"
            url_s3 = upload_local_file_to_s3(caminho_png, s3_key)

            pergunta = f"Descreva o conteúdo da página {i+1} do documento '{filename}'."
            resposta = chamar_llama_scout(pergunta, url_s3)
            descricoes.append(f"Página {i+1}: {resposta}")

        return {
            "filename": filename,
            "type": "pdf",
            "description": "\n".join(descricoes)
        }

    else:
        # Para imagens ou outros arquivos já públicos
        pergunta = f"Analise o conteúdo do arquivo '{filename}' disponível em: {url}"
        resposta = chamar_llama(pergunta)
        return {
            "filename": filename,
            "type": "imagem",
            "description": resposta
        }
