import os
import json
import boto3
import logging
from sentence_transformers import SentenceTransformer, util
from services.groq_client import chamar_llama
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

model = SentenceTransformer('intfloat/multilingual-e5-large')
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name=os.getenv('AWS_REGION')
)


def carregar_base(bucket=None, key_imagens="images/imagens.json"):
    if bucket is None:
        bucket = os.getenv("S3_BUCKET")

    base = []
    logger.info(
        f"Carregando base de conhecimento do bucket '{bucket}', chave '{key_imagens}'")

    substituicoes = {
        "médico": "médico doutor profissional de saúde clínico",
        "profissional": "profissional colaborador funcionário trabalhador médico doutor",
        "paciente": "paciente cliente pessoa atendida indivíduo usuário",
        "consultório": "consultório clínica sala de atendimento local de saúde",
        "exame": "exame procedimento diagnóstico teste",
        "convênio": "convênio plano de saúde seguro saúde",
    }

    try:
        file_obj = s3.get_object(Bucket=bucket, Key=key_imagens)
        imagens = json.loads(file_obj["Body"].read().decode("utf-8"))
        logger.info(f"{len(imagens)} registros encontrados no JSON")

        for item in imagens:
            descricao = item.get("descricao", "")
            url = item.get("url", "")
            nome = item.get("nome", "")
            topicos = item.get("tópicos", [])

            texto_embedding = f"{nome} {descricao} "
            for topico in topicos:
                texto_embedding += f"{topico.get('name', '')} {topico.get('description', '')} {topico.get('content', '')} "

            texto_lower = texto_embedding.lower()
            for termo, sinonimos in substituicoes.items():
                if termo in texto_lower:
                    texto_embedding += " " + sinonimos

            logger.debug(f"Processando imagem: {nome}")
            emb = model.encode(
                texto_embedding, convert_to_tensor=True, normalize_embeddings=True)

            base.append({
                "tipo": "imagem",
                "arquivo": nome,
                "texto": texto_embedding,
                "imagem": url,
                "tópicos": topicos,
                "embedding": emb
            })

    except s3.exceptions.NoSuchKey:
        logger.warning(
            f"Arquivo '{key_imagens}' não encontrado no bucket '{bucket}'.")

    except Exception as e:
        logger.exception(f"Erro ao carregar base: {str(e)}")

    return base


def buscar_texto_e_imagem(pergunta, base):
    logger.info(
        f"Buscando imagem mais relevante para a pergunta: '{pergunta}'")
    emb_pergunta = model.encode(
        pergunta, convert_to_tensor=True, normalize_embeddings=True)

    imagens_scores = []
    for item in base:
        if item["tipo"] == "imagem":
            score = util.cos_sim(emb_pergunta, item["embedding"]).item()
            imagens_scores.append((item, score))
            logger.debug(f"Similaridade com '{item['arquivo']}': {score:.4f}")

    imagens_scores.sort(key=lambda x: x[1], reverse=True)
    top3 = [img for img, _ in imagens_scores[:3]]

    logger.info(f"Top 3 candidatos: {[img['arquivo'] for img in top3]}")

    if not top3:
        logger.warning("Nenhum candidato encontrado")
        return None

    return selecionar_por_ia(pergunta, top3)


def selecionar_por_ia(pergunta: str, candidatos: list):
    logger.info("Enviando candidatos para IA escolher o mais relevante")
    prompt = f"""
Você é um assistente semântico. Abaixo estão três objetos visuais com descrição e tópicos extraídos.

Sua tarefa é escolher o objeto mais relevante para responder à pergunta: "{pergunta}"

Responda com o nome do arquivo mais relevante, e justifique brevemente sua escolha.

Formato de resposta:
{{
  "arquivo": "nome_do_arquivo_mais_relevante",
  "justificativa": "..."
}}

Objetos:
"""

    for i, item in enumerate(candidatos, start=1):
        prompt += f"\nObjeto {i}:\n"
        prompt += f"Arquivo: {item['arquivo']}\n"
        prompt += f"Descrição: {item['texto']}\n"
        prompt += f"Tópicos:\n"
        for topico in item.get("tópicos", []):
            prompt += f"  - {json.dumps(topico, ensure_ascii=False)}\n"

    logger.debug(f"Prompt enviado à IA:\n{prompt}")

    try:
        resposta = chamar_llama(prompt)
        logger.debug(f"Resposta da IA:\n{resposta}")

        resultado = json.loads(resposta)
        nome = resultado.get("arquivo")
        logger.info(f"IA escolheu o arquivo: {nome}")

        for item in candidatos:
            logger.debug(f"Comparando '{item['arquivo']}' com '{nome}'")
            if item["arquivo"] == nome:
                logger.info(f"Arquivo selecionado: {item['arquivo']}")
                return item

        logger.warning(f"Arquivo '{nome}' não encontrado entre os candidatos")

    except Exception as e:
        logger.exception("Erro ao interpretar resposta da IA")

    logger.warning("Fallback ativado: retornando primeiro candidato")
    return candidatos[0]
