import os
import json
import boto3
import logging
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

model = SentenceTransformer('all-mpnet-base-v2')

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

    try:
        file_obj = s3.get_object(Bucket=bucket, Key=key_imagens)
        imagens = json.loads(file_obj["Body"].read().decode("utf-8"))
        for item in imagens:
            descricao = item.get("descricao", "")
            url = item.get("url", "")
            nome = item.get("nome", "")
            topicos = item.get("tópicos", [])
            emb = model.encode(descricao, convert_to_tensor=True, normalize_embeddings=True) 
                #convert_to_tensor retorna como um tensor do Pytorch
                #normalize_embeddings normaliza o vetor para unitario, possibilitando a utilização de similaridade por cosseno.

            base.append({
                "tipo": "imagem",
                "arquivo": nome,
                "texto": descricao,
                "imagem": url,
                "tópicos": topicos,
                "embedding": emb
            })
    except s3.exceptions.NoSuchKey:
        logger.warning(f"Arquivo '{key_imagens}' não encontrado no bucket '{bucket}'.")

    return base

def normalizar_topico(topico):

    #Converte um tópico em string para o embedding.

    if isinstance(topico, dict):
        partes = []
        if "name" in topico:
            partes.append(topico["name"])
        if "description" in topico:
            partes.append(topico["description"])
        if "content" in topico:
            partes.append(topico["content"])
        return " | ".join(partes)

    if isinstance(topico, list):
        return " | ".join(normalizar_topico(t) for t in topico if t)

    if isinstance(topico, str):
        return topico

    return str(topico)


def buscar_texto_e_imagem(pergunta, base):
    emb_pergunta = model.encode(pergunta, convert_to_tensor=True, normalize_embeddings=True)

    logger.info(f"Pergunta recebida: {pergunta}")
    # Seleciona top3
    imagens_scores = []
    for item in base:
        if item["tipo"] == "imagem":
            score = util.cos_sim(emb_pergunta, item["embedding"]).item()
            imagens_scores.append((item, score))
            logger.info(f"   → Similaridade com '{item['arquivo']}': {score:.4f}")

    # Ordenar e pegar top3
    imagens_scores.sort(key=lambda x: x[1], reverse=True)
    top3 = imagens_scores[:3]

    logger.info("Top 3 imagens (descrição):")
    for i, (img, sc) in enumerate(top3, start=1):
        logger.info(f"   {i}. {img['arquivo']} (score={sc:.4f})")

    if not top3:
        return None

    # Selecionar melhor tópico dentre os top3
    melhor_topico = None
    melhor_score_topico = float("-inf")
    melhor_imagem = None

    for img, _ in top3:
        for topico in img.get("tópicos", []):
            texto_topico = normalizar_topico(topico)
            emb_topico = model.encode(texto_topico, convert_to_tensor=True, normalize_embeddings=True)
            score_topico = util.cos_sim(emb_pergunta, emb_topico).item()
            logger.info(f"      → Tópico '{texto_topico}' em '{img['arquivo']}': {score_topico:.4f}")

            if score_topico > melhor_score_topico:
                melhor_score_topico = score_topico
                melhor_topico = topico
                melhor_imagem = img

    logger.info(f"Melhor tópico: {melhor_topico} (score={melhor_score_topico:.4f})")
    logger.info(f"Imagem escolhida: {melhor_imagem['arquivo']}")

    return melhor_imagem
