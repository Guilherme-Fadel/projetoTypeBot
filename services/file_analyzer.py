import fitz  # PyMuPDF
import requests
import json
import re
from services.groq_client import chamar_llama, chamar_llama_scout


def extract_json(resposta: str):
    """
    Extrai JSON válido de uma resposta que pode estar embrulhada em texto ou blocos de código.
    """
    try:
        # Procura um objeto JSON dentro da resposta
        match = re.search(r"\{[\s\S]*\}", resposta)
        if match:
            clean_json = match.group(0)
            return json.loads(clean_json)

        # Se já for JSON puro
        return json.loads(resposta)
    except Exception as e:
        print(f"[ERRO extract_json] → {e}")
        return None


def analyze_pdf(url, filename):
    """
    Faz o download de um PDF, extrai texto e envia para o LLM resumir em JSON.
    """
    response = requests.get(url)
    response.raise_for_status()

    # Abre o PDF
    with open("temp.pdf", "wb") as f:
        f.write(response.content)

    texto = ""
    with fitz.open("temp.pdf") as doc:
        for page in doc:
            texto += page.get_text()

    prompt = f"""
Você é um analisador de documentos. Leia o texto abaixo e retorne SOMENTE um JSON válido no seguinte formato:

{{
  "description": "Resumo geral do documento",
  "tópicos": [
    {{
      "name": "Nome do tópico",
      "description": "Descrição curta",
      "content": "Conteúdo relevante resumido"
    }}
  ]
}}

Texto do PDF:
\"\"\"{texto}\"\"\"
"""

    resposta = chamar_llama(prompt)
    json_resp = extract_json(resposta)

    if json_resp:
        return {
            "filename": filename,
            "type": "pdf",
            "description": json_resp.get("description", ""),
            "tópicos": json_resp.get("tópicos", []),
        }
    else:
        return {
            "filename": filename,
            "type": "pdf",
            "description": texto[:500],  # fallback
            "tópicos": [],
        }


def analyze_image(url, filename):
    """
    Envia a imagem para o LLM descrever e extrair informações em JSON.
    """
    prompt = """
Você é um analisador de imagens de sistemas. Descreva a imagem e retorne SOMENTE um JSON válido no formato:

{
  "description": "Descrição geral da imagem",
  "tópicos": [
    {
      "name": "Nome da seção",
      "description": "Descrição curta",
      "content": "Conteúdo detalhado ou resumo do que aparece"
    }
  ]
}
"""

    resposta = chamar_llama_scout(prompt, url)
    json_resp = extract_json(resposta)

    if json_resp:
        return {
            "filename": filename,
            "type": "imagem",
            "description": json_resp.get("description", ""),
            "tópicos": json_resp.get("tópicos", []),
        }
    else:
        return {
            "filename": filename,
            "type": "imagem",
            "description": resposta,
            "tópicos": [],
        }


def analyze_file(url, filename):
    """
    Detecta se o arquivo é PDF ou imagem e chama o analisador correspondente.
    """
    if filename.lower().endswith(".pdf"):
        return analyze_pdf(url, filename)
    else:
        return analyze_image(url, filename)
