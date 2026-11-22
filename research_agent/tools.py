"""
research_agent/tools.py - Ferramentas de Pesquisa Vetorial e Calculo Analitico para o Agente RAG.
"""

import os
import json
from typing import Literal
from research_agent.vector_store import VectorStoreRAG

PASTA_DADOS = os.path.join(os.path.dirname(__file__), "data")

# Instancia global do banco vetorial carregado na inicializacao
_vector_store = None


def _obter_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreRAG()
        if os.path.exists(PASTA_DADOS):
            _vector_store.carregar_diretorio(PASTA_DADOS)
    return _vector_store


def pesquisar_documentos_tecnicos(pergunta_ou_termo: str, limite_resultados: int = 3) -> str:
    """
    Realiza busca vetorial semantica na base documental da empresa (relatorios financeiros e diretrizes).
    Retorna os trechos mais relevantes acompanhados de metadados de fonte (documento, secao e score de relevancia).
    
    Args:
        pergunta_ou_termo: A duvida tecnica ou topico a ser pesquisado (ex: 'EBITDA', 'risco de fornecedor', 'classificacao nivel 1').
        limite_resultados: Quantidade de trechos mais relevantes a retornar (padrao: 3).
    """
    print(f"\n🔎 [TOOL RAG] pesquisar_documentos_tecnicos(query='{pergunta_ou_termo}')")
    vs = _obter_vector_store()
    resultados = vs.buscar_top_k(pergunta_ou_termo, k=limite_resultados)

    if not resultados:
        return json.dumps({"status": "vazio", "mensagem": "Nenhum trecho relevante encontrado."}, ensure_ascii=False)

    return json.dumps({
        "status": "sucesso",
        "total_encontrados": len(resultados),
        "trechos": resultados
    }, ensure_ascii=False)


def calcular_metrica_financeira(
    operacao: Literal["variacao_percentual", "margem_percentual", "diferenca_absoluta"],
    valor_a: float,
    valor_b: float
) -> str:
    """
    Calculadora deterministica e precisa para metricas financeiras e operacionais.
    Evita alucinacoes aritmeticas do modelo ao analisar relatorios.
    
    Args:
        operacao: Tipo de calculo ('variacao_percentual', 'margem_percentual', 'diferenca_absoluta').
        valor_a: Primeiro valor numerico (ex: valor atual ou numerador).
        valor_b: Segundo valor numerico (ex: valor anterior ou denominador).
    """
    print(f"\n🧮 [TOOL MATH] calcular_metrica_financeira(op='{operacao}', a={valor_a}, b={valor_b})")
    
    if operacao == "variacao_percentual":
        if valor_b == 0:
            return json.dumps({"erro": "Divisao por zero no valor base."})
        variacao = ((valor_a - valor_b) / valor_b) * 100.0
        return json.dumps({"operacao": operacao, "resultado_percentual": f"{variacao:+.2f}%", "valor_numerico": variacao})

    elif operacao == "margem_percentual":
        if valor_b == 0:
            return json.dumps({"erro": "Divisao por zero na receita total."})
        margem = (valor_a / valor_b) * 100.0
        return json.dumps({"operacao": operacao, "margem_percentual": f"{margem:.2f}%", "valor_numerico": margem})

    elif operacao == "diferenca_absoluta":
        diff = valor_a - valor_b
        return json.dumps({"operacao": operacao, "diferenca_absoluta": diff})

    return json.dumps({"erro": "Operacao invalida."})
