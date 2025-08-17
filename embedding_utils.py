import os
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')


def carregar_base(pasta="textos"):
    base = []
    for nome in os.listdir(pasta):
        if nome.lower().endswith(".txt"):
            caminho = os.path.join(pasta, nome)
            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                texto = f.read()
            emb = model.encode(texto, convert_to_tensor=True,
                               normalize_embeddings=True)
            base.append({"arquivo": nome, "texto": texto, "embedding": emb})
    return base


def buscar_texto(pergunta, base):
    emb_pergunta = model.encode(
        pergunta, convert_to_tensor=True, normalize_embeddings=True)
    melhor_score = float("-inf")
    melhor_texto = ""
    for item in base:
        # <- torna escalar
        score = util.cos_sim(emb_pergunta, item["embedding"]).item()
        if score > melhor_score:
            melhor_score = score
            melhor_texto = item["texto"]
    return melhor_texto
