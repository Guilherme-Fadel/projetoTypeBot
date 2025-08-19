import os
import json
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-mpnet-base-v2')


def carregar_base(pasta_textos="data/textos", arquivo_imagens="data/imagens.json"):
    base = []

    # carrega textos
    for nome in os.listdir(pasta_textos):
        if nome.lower().endswith(".txt"):
            caminho = os.path.join(pasta_textos, nome)
            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                texto = f.read()
            emb = model.encode(texto, convert_to_tensor=True,
                               normalize_embeddings=True)
            base.append({"tipo": "texto", "arquivo": nome,
                        "texto": texto, "imagem": None, "embedding": emb})

    # carrega descrições de imagens
    if os.path.exists(arquivo_imagens):
        with open(arquivo_imagens, "r", encoding="utf-8") as f:
            imagens = json.load(f)
        for item in imagens:
            descricao = item.get("descricao", "")
            url = item.get("url", "")
            emb = model.encode(
                descricao, convert_to_tensor=True, normalize_embeddings=True)
            base.append({"tipo": "imagem", "arquivo": item.get(
                "nome"), "texto": descricao, "imagem": url, "embedding": emb})

    return base


def buscar_texto_e_imagem(pergunta, base):
    emb_pergunta = model.encode(
        pergunta, convert_to_tensor=True, normalize_embeddings=True)

    melhor_texto = None
    melhor_imagem = None
    melhor_score_texto = float("-inf")
    melhor_score_imagem = float("-inf")

    for item in base:
        score = util.cos_sim(emb_pergunta, item["embedding"]).item()
        if item["tipo"] == "texto" and score > melhor_score_texto:
            melhor_score_texto = score
            melhor_texto = item
        elif item["tipo"] == "imagem" and score > melhor_score_imagem:
            melhor_score_imagem = score
            melhor_imagem = item

    return melhor_texto, melhor_imagem
