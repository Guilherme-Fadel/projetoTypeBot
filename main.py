from flask import Flask, request, Response, jsonify
from embedding_utils import carregar_base, buscar_texto_e_imagem
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
        return jsonify({"resposta": "Desculpe, não entendi sua pergunta."})

    melhor_texto, melhor_imagem = buscar_texto_e_imagem(
        pergunta, base_conhecimento)

    contexto = melhor_texto["texto"] if melhor_texto else ""
    prompt = montar_prompt(contexto, pergunta)

    try:
        resposta = chamar_llama(prompt)
    except Exception as e:
        return jsonify({"resposta": f"Erro ao chamar Llama: {str(e)}"})

    return jsonify({
        "resposta": resposta,
        "imagem": melhor_imagem.get("imagem") if melhor_imagem else None
    })


def chamar_llama(prompt: str) -> str:
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
