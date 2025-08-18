
from utils.embedding_utils import carregar_base, buscar_texto_e_imagem

base_conhecimento = carregar_base("data/textos", "data/imagens.json")

def buscar(pergunta: str):
    melhor_texto, melhor_imagem = buscar_texto_e_imagem(pergunta, base_conhecimento)
    return melhor_texto, melhor_imagem

