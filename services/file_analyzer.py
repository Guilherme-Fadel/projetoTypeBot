import fitz  # PyMuPDF
import requests
import json
import re
from services.groq_client import chamar_llama, chamar_llama_scout


def extract_json(resposta: str):

    try:
        match = re.search(r"\{[\s\S]*\}", resposta)
        if match:
            clean_json = match.group(0)
            return json.loads(clean_json)

        #Se já for JSON puro
        return json.loads(resposta)
    except Exception as e:
        print(f"[ERRO extract_json] → {e}")
        return None


def analyze_pdf(url, filename):

    response = requests.get(url)
    response.raise_for_status()

    with open("temp.pdf", "wb") as f:
        f.write(response.content)

    texto = ""
    with fitz.open("temp.pdf") as doc:
        for page in doc:
            texto += page.get_text()

    prompt = f"""
Você é um analisador de documentos e telas de sistemas. 
Sua função é extrair informações para um mecanismo de busca semântica.

Regras:
- Responda SOMENTE com um JSON válido.
- O campo "description" deve conter um resumo completo, citando os termos importantes 
  (como 'relatório', 'cadastro', 'usuário', 'login', etc.), 
  e a localização dos elementos visuais (menus, botões, campos, tabelas).
- O campo "tópicos" deve ser uma lista de áreas relevantes da tela/documento, cada uma com:
  - "name": título curto e objetivo (máx. 5 palavras).
  - "description": frase resumida.
  - "content": explicação detalhada do que aparece (ex.: nomes de botões, colunas, ícones, textos). Não cite os dados indicados na imagem, somente utilize-os como base para descrever os elementos visuais.

- Priorize termos funcionais e de negócio em vez de apenas layout.
- Sempre cite explicitamente se houver elementos de relatórios, cadastros, login, parâmetros, etc.

Formato de saída:
{{
  "description": "...",
  "tópicos": [
    {{
      "name": "...",
      "description": "...",
      "content": "..."
    }}
  ]
}}

Texto do PDF/tela:
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
    prompt = f"""
Você é um analisador de documentos e telas de sistemas. 
Sua função é extrair informações para um mecanismo de busca semântica.

Regras:
- Responda SOMENTE com um JSON válido.
- O campo "description" deve conter um resumo completo, citando os termos importantes 
  (como 'relatório', 'cadastro', 'usuário', 'login', etc.), 
  e a localização dos elementos visuais (menus, botões, campos, tabelas).
- O campo "tópicos" deve ser uma lista de áreas relevantes da tela/documento, cada uma com:
  - "name": título curto e objetivo (máx. 5 palavras).
  - "description": frase resumida.
  - "content": explicação detalhada do que aparece (ex.: nomes de botões, colunas, ícones, textos). Não cite os dados indicados na imagem, somente utilize-os como base para descrever os elementos visuais.

- Priorize termos funcionais e de negócio em vez de apenas layout.
- Sempre cite explicitamente se houver elementos de relatórios, cadastros, login, parâmetros, etc.

Formato de saída:
{{
  "description": "...",
  "tópicos": [
    {{
      "name": "...",
      "description": "...",
      "content": "..."
    }}
  ]
}}
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
    if filename.lower().endswith(".pdf"):
        return analyze_pdf(url, filename)
    else:
        return analyze_image(url, filename)
