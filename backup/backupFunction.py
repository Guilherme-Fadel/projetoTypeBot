def buscar_texto_e_imagem(pergunta, base):
    emb_pergunta = model.encode(pergunta, convert_to_tensor=True, normalize_embeddings=True)

    logger.info(f"🔎 Pergunta recebida: {pergunta}")

    melhor_imagem = None
    melhor_score_imagem = float("-inf")

    for item in base:
        score = util.cos_sim(emb_pergunta, item["embedding"]).item()
        logger.info(f"   → Similaridade com '{item['arquivo']}' ({item['tipo']}): {score:.4f}")

        
        if item["tipo"] == "imagem" and score > melhor_score_imagem:
            melhor_score_imagem, melhor_imagem = score, item

    logger.info(f"Imagem escolhida: {melhor_imagem['arquivo'] if melhor_imagem else 'Nenhuma'} (score={melhor_score_imagem:.4f})")

    return melhor_imagem
