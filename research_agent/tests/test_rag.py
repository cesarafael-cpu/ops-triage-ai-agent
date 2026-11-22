"""
research_agent/tests/test_rag.py - Testes Unitarios do Motor RAG e Calculadora Financeira.
"""

import json
import pytest
from research_agent.vector_store import cosine_similarity, VectorStoreRAG
from research_agent.tools import calcular_metrica_financeira


def test_cosine_similarity_vetores_identicos():
    """Dois vetores identicos devem ter similaridade exatamente igual a 1.0."""
    v1 = [1.0, 2.0, 3.0]
    v2 = [1.0, 2.0, 3.0]
    assert pytest.approx(cosine_similarity(v1, v2), 0.0001) == 1.0


def test_cosine_similarity_vetores_ortogonais():
    """Dois vetores perpendiculares devem ter similaridade igual a 0.0."""
    v1 = [1.0, 0.0]
    v2 = [0.0, 1.0]
    assert pytest.approx(cosine_similarity(v1, v2), 0.0001) == 0.0


def test_calcular_metrica_financeira_variacao():
    """Testa o calculo deterministico de crescimento percentual."""
    # Receita cresceu de 328 para 420
    res = json.loads(calcular_metrica_financeira("variacao_percentual", 420.0, 328.0))
    assert res["operacao"] == "variacao_percentual"
    assert pytest.approx(res["valor_numerico"], 0.1) == 28.05


def test_calcular_metrica_financeira_margem():
    """Testa o calculo de margem EBITDA (115 / 420)."""
    res = json.loads(calcular_metrica_financeira("margem_percentual", 115.0, 420.0))
    assert res["operacao"] == "margem_percentual"
    assert pytest.approx(res["valor_numerico"], 0.1) == 27.38


def test_vector_store_indexacao_e_busca(tmp_path):
    """Testa se o VectorStore divide em secoes e recupera o trecho correto."""
    doc_teste = tmp_path / "teste_doc.txt"
    doc_teste.write_text(
        "[SECAO_ALVO]\nO projeto de IA reduziu custos operacionais em 42% no periodo.\n\n"
        "[SECAO_OUTRA]\nInformacoes genericas sobre escritorio e cafezinho.",
        encoding="utf-8"
    )

    vs = VectorStoreRAG()
    vs.indexar_arquivo(str(doc_teste))

    assert len(vs.chunks) >= 2
    resultados = vs.buscar_top_k("reduziu custos operacionais IA", k=1)
    assert len(resultados) == 1
    assert resultados[0]["secao"] == "SECAO_ALVO"
    assert "42%" in resultados[0]["texto"]
