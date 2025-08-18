from flask import Blueprint, request, jsonify
from utils.knowledge_base import buscar
from services.groq_client import chamar_llama_scout

responder_bp = Blueprint("responder", __name__)

@responder_bp.route("/responder", methods=["POST"])
def responder():
    dados = request.get_json(silent=True) or {}
    pergunta = (dados.get("pergunta") or "").strip()

    if not pergunta:
        return jsonify({"resposta": "Desculpe, não entendi sua pergunta."})

    melhor_texto, melhor_imagem = buscar(pergunta)

    contexto = melhor_texto["texto"] if melhor_texto else ""
    imagem_url = melhor_imagem.get("imagem") if melhor_imagem else ""

    descricao_visual = ""
    if imagem_url:
        try:
            descricao_visual = chamar_llama_scout(pergunta, imagem_url)
        except Exception as e:
            descricao_visual = f"[Erro ao descrever imagem: {str(e)}]"

    return jsonify({
        "resposta": contexto,
        "imagem": imagem_url,
        "descricao_visual": descricao_visual
    })
