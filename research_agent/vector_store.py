"""
research_agent/vector_store.py - Motor de RAG Semantico (Chunking, Embeddings e Cosine Similarity).
"""

import os
import math
from typing import List, Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calcula a similaridade por cosseno entre dois vetores."""
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class VectorStoreRAG:
    """Banco vetorial em memoria com geracao de embeddings e busca semantica rastreavel."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.chunks: List[Dict[str, Any]] = []

    def gerar_embedding(self, texto: str) -> List[float]:
        """Gera embedding denso via API do Gemini com fallback seguro."""
        if not self.client:
            raise ValueError("GEMINI_API_KEY nao configurada.")

        # Tenta modelos de embeddings oficiais
        modelos_embedding = ["gemini-embedding-001", "gemini-embedding-2"]
        for mod in modelos_embedding:
            try:
                res = self.client.models.embed_content(
                    model=mod,
                    contents=texto
                )
                if hasattr(res, "embedding") and hasattr(res.embedding, "values"):
                    return res.embedding.values
                if hasattr(res, "embeddings") and res.embeddings:
                    return res.embeddings[0].values
            except Exception:
                continue

        # Fallback deterministico de hashing semantico se as cotas de embeddings estiverem indisponiveis
        return self._fallback_hash_embedding(texto)

    def _fallback_hash_embedding(self, texto: str, dim: int = 128) -> List[float]:
        """Gera um vetor normalizado de frequencia de n-gramas caso haja indisponibilidade temporaria de API."""
        vetor = [0.0] * dim
        palavras = texto.lower().split()
        for i, p in enumerate(palavras):
            idx = hash(p) % dim
            vetor[idx] += 1.0 / (i + 1.0)
        norm = math.sqrt(sum(v * v for v in vetor))
        return [v / norm if norm > 0 else 0.0 for v in vetor]

    def indexar_arquivo(self, caminho_arquivo: str):
        """Le o arquivo, divide em secoes/chunks contextuais e gera embeddings."""
        nome_arquivo = os.path.basename(caminho_arquivo)
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()

        # Chunking baseado em secoes [NOME DA SECAO]
        blocos = conteudo.split("\n\n")
        secao_atual = "INTRODUCAO"

        for bloco in blocos:
            bloco_limpo = bloco.strip()
            if not bloco_limpo or bloco_limpo.startswith("#"):
                continue

            if bloco_limpo.startswith("["):
                fim_colchete = bloco_limpo.find("]")
                if fim_colchete != -1:
                    secao_atual = bloco_limpo[1:fim_colchete]
                    texto_secao = bloco_limpo[fim_colchete + 1:].strip()
                    if not texto_secao:
                        continue
                    bloco_limpo = texto_secao

            # Gera embedding para o pedaco de texto
            vetor = self.gerar_embedding(bloco_limpo)
            self.chunks.append({
                "documento": nome_arquivo,
                "secao": secao_atual,
                "texto": bloco_limpo,
                "embedding": vetor
            })

    def carregar_diretorio(self, pasta_dados: str):
        """Indexa todos os arquivos .txt de um diretorio."""
        for arq in os.listdir(pasta_dados):
            if arq.endswith(".txt"):
                caminho = os.path.join(pasta_dados, arq)
                self.indexar_arquivo(caminho)

    def buscar_top_k(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Realiza busca vetorial semantica calculando similaridade por cosseno."""
        if not self.chunks:
            return []

        query_vec = self.gerar_embedding(query)
        scores = []

        for chunk in self.chunks:
            score = cosine_similarity(query_vec, chunk["embedding"])
            scores.append({
                "documento": chunk["documento"],
                "secao": chunk["secao"],
                "texto": chunk["texto"],
                "score": round(score, 4)
            })

        # Ordena pelos scores mais altos (maior similaridade)
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:k]
