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
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Você é um assistente útil e direto."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 512,
    }
    resp = session.post(GROQ_URL, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return str(data["choices"][0]["message"]["content"]).strip()

def chamar_llama_scout(pergunta: str, imagem_url: str) -> str:
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": "Você é um assistente visual que descreve imagens com precisão."},
            {"role": "user", "content": pergunta}
        ],
        "temperature": 0.2,
        "max_tokens": 512,
        "image": [imagem_url]
    }
    resp = session.post(GROQ_URL, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return str(data["choices"][0]["message"]["content"]).strip()
