import requests
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
})


def chamar_llama(prompt: str) -> str:
    payload = {
        "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": "Você é um assistente útil e direto."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,
        "max_tokens": 2048,
    }
    resp = session.post(GROQ_URL, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return str(data["choices"][0]["message"]["content"]).strip()


def chamar_llama_scout(pergunta: str, imagem_url: str) -> str:
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": pergunta},
                    {"type": "image_url", "image_url": {"url": imagem_url}}
                ]
            }
        ],
        "temperature": 0.0,
        "max_tokens": 2048
    }

    resp = session.post(GROQ_URL, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return str(data["choices"][0]["message"]["content"]).strip()
