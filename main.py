from flask import Flask, request, Response, jsonify
from embedding_utils import carregar_base, buscar_texto
from llama_prompt import montar_prompt
import requests

app = Flask(__name__)
base_conhecimento = carregar_base()

# Chave exatamente como você me passou
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


@app.route("/responder", methods=["POST"])
def responder():
    dados = request.get_json(silent=True) or {}
    pergunta = (dados.get("pergunta") or "").strip()

    if not pergunta:
        texto_resposta = "Desculpe, não entendi sua pergunta. Pode reformular?"

    contexto = buscar_texto(pergunta, base_conhecimento)
    prompt = montar_prompt(contexto, pergunta)

    try:
        texto_resposta = chamar_llama(prompt)  # retorna só string
    except requests.HTTPError as e:
        return Response(
            f"Erro HTTP ao chamar Groq: {e.response.status_code} - {e.response.text}",
            status=502,
            mimetype="text/plain; charset=utf-8"
        )
    except Exception as e:
        return Response(
            f"Falha ao chamar Groq: {str(e)}",
            status=502,
            mimetype="text/plain; charset=utf-8"
        )

    return jsonify({
        "statusCode": 200,
        "response": {
            "resposta": texto_resposta
        }
    })


def chamar_llama(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY não configurada")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Você é um assistente útil e direto."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 512,
    }

    response = requests.post(GROQ_URL, headers=headers,
                             json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return str(data["choices"][0]["message"]["content"]).strip()


if __name__ == "__main__":
    app.run(debug=True)
