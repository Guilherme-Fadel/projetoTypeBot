import os
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')


def carregar_base(pasta="textos"):
    base = []
    for nome in os.listdir(pasta):
        if nome.endswith(".txt"):
            caminho = os.path.join(pasta, nome)
            with open(caminho, "r", encoding="utf-8") as f:
                texto = f.read()
                emb = model.encode(texto)
                base.append(
                    {"arquivo": nome, "texto": texto, "embedding": emb})
    return base


def buscar_texto(pergunta, base):
    emb_pergunta = model.encode(pergunta)
    melhor_score = -1
    melhor_texto = ""
    for item in base:
        score = util.cos_sim(emb_pergunta, item["embedding"])
        if score > melhor_score:
            melhor_score = score
            melhor_texto = item["texto"]
    return melhor_texto
