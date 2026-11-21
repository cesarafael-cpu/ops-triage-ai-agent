"""
scripts/check_models.py - Script utilitario para diagnosticar modelos Gemini disponiveis na API Key.
"""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("[ERRO] GEMINI_API_KEY nao configurada no arquivo .env.")
    exit(1)

client = genai.Client(api_key=api_key)

print("Consultando modelos disponiveis para a sua chave...")
try:
    models = client.models.list()
    encontrados = []
    for m in models:
        name = getattr(m, 'name', '') or str(m)
        if "gemini" in name:
            encontrados.append(name)
            print(f" -> {name}")
    print(f"\nTotal de modelos Gemini encontrados: {len(encontrados)}")
except Exception as e:
    print(f"Erro ao listar modelos: {e}")
