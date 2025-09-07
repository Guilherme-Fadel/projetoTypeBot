import json
import re

def safe_json_loads(resposta: str):
    try:
        if "```" in resposta:
            partes = re.findall(r"\{[\s\S]*\}", resposta)
            if partes:
                resposta = partes[0]

        resposta = resposta.strip()

        # Tenta converter em JSON
        return json.loads(resposta)
    except Exception as e:
        print(f"[ERRO ao converter resposta em JSON] → {e}")
        return None
