from services.pdf_image_converter import analisar_pdf_com_scout
from services.groq_client import chamar_llama, chamar_llama_scout

def analyze_file(url: str, filename: str) -> dict:
    ext = filename.split('.')[-1].lower()

    if ext == "pdf":
        imagens_png = analisar_pdf_com_scout(url)

        descricoes = []
        for i, caminho_png in enumerate(imagens_png):
            pergunta = f"Descreva o conteúdo da página {i+1} do documento '{filename}'."
            resposta = chamar_llama_scout(caminho_png, pergunta)
            descricoes.append(f"Página {i+1}: {resposta}")

        return {
            "filename": filename,
            "type": "pdf",
            "description": "\n".join(descricoes)
        }

    else:
        prompt = f"Analise o conteúdo do arquivo '{filename}' disponível em: {url}"
        resposta = chamar_llama(prompt)
        return {
            "filename": filename,
            "type": "texto",
            "description": resposta
        }
