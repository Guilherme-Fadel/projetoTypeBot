import os
import json
import boto3
import logging
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv

# 🔧 Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# 🔍 Carregando modelo de embeddings
model = SentenceTransformer('all-mpnet-base-v2')

# ☁️ Configurando cliente S3
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name=os.getenv('AWS_REGION')
)

def carregar_base(pasta_textos="data/textos", bucket=None, key_imagens="images/imagens.json"):
    if bucket is None:
        bucket = os.getenv("S3_BUCKET")

    base = []

    # 📄 Processando arquivos de texto
    for nome in os.listdir(pasta_textos):
        if nome.lower().endswith(".txt"):
            caminho = os.path.join(pasta_textos, nome)
            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                texto = f.read()
            emb = model.encode(texto, convert_to_tensor=True, normalize_embeddings=True)
            base.append({
                "tipo": "texto",
                "arquivo": nome,
                "texto": texto,
                "imagem": None,
                "embedding": emb
            })

    # 🖼️ Processando imagens do S3
    try:
        file_obj = s3.get_object(Bucket=bucket, Key=key_imagens)
        imagens = json.loads(file_obj["Body"].read().decode("utf-8"))
        for item in imagens:
            descricao = item.get("descricao", "")
            url = item.get("url", "")
            emb = model.encode(descricao, convert_to_tensor=True, normalize_embeddings=True)
            base.append({
                "tipo": "imagem",
                "arquivo": item.get("nome"),
                "texto": descricao,
                "imagem": url,
                "embedding": emb
            })
    except s3.exceptions.NoSuchKey:
        logger.warning(f"Arquivo '{key_imagens}' não encontrado no bucket '{bucket}'.")

    return base

def buscar_texto_e_imagem(pergunta, base):
    emb_pergunta = model.encode(pergunta, convert_to_tensor=True, normalize_embeddings=True)

    logger.info(f"🔎 Pergunta recebida: {pergunta}")

    melhor_texto, melhor_imagem = None, None
    melhor_score_texto, melhor_score_imagem = float("-inf"), float("-inf")

    for item in base:
        score = util.cos_sim(emb_pergunta, item["embedding"]).item()
        logger.info(f"   → Similaridade com '{item['arquivo']}' ({item['tipo']}): {score:.4f}")

        if item["tipo"] == "texto" and score > melhor_score_texto:
            melhor_score_texto, melhor_texto = score, item
        elif item["tipo"] == "imagem" and score > melhor_score_imagem:
            melhor_score_imagem, melhor_imagem = score, item

    logger.info(f"✅ Texto escolhido: {melhor_texto['arquivo'] if melhor_texto else 'Nenhum'} (score={melhor_score_texto:.4f})")
    logger.info(f"✅ Imagem escolhida: {melhor_imagem['arquivo'] if melhor_imagem else 'Nenhuma'} (score={melhor_score_imagem:.4f})")

    return melhor_texto, melhor_imagem
