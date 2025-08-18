def montar_prompt(contexto, pergunta):
    return f"""
Você é um assistente técnico. Use o seguinte contexto e a imagem vinculada para responder à pergunta do cliente:

Contexto:
{contexto}
Responda à seguinte pergunta de forma clara, objetiva e sem mencionar nomes próprios ou dados pessoais, e corrigindo erros gramaticais e ortográficos,
lembrando ao usuário que todas as informações são referentes a versões iguais ou superior a "25.05.14-17":
Pergunta:
{pergunta}
"""
