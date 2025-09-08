
from utils.embedding_utils import carregar_base, buscar_texto_e_imagem
from dotenv import load_dotenv
import os

load_dotenv()


base_conhecimento = carregar_base(
    bucket=os.getenv("S3_BUCKET"),
    key_imagens="images/imagens.json"
)


def buscar(pergunta: str):
    melhor_imagem = buscar_texto_e_imagem(pergunta, base_conhecimento)
    return melhor_imagem

