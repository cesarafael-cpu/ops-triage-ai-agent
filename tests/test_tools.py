"""
tests/test_tools.py - Testes Unitarios Deterministicos para as Ferramentas do Agente.
Nao consome cota de API LLM.
"""

import json
import os
import pytest
from tools import (
    consultar_base_conhecimento,
    registrar_demanda,
    listar_historico_chamados,
    enviar_alerta_slack,
    DB_PATH
)


def test_consultar_base_conhecimento_encontra_reembolso():
    """Testa se a busca por 'reembolso' retorna a politica oficial de 7 dias."""
    resultado_json = consultar_base_conhecimento("reembolso")
    dados = json.loads(resultado_json)
    assert dados["status"] == "encontrado"
    assert "7 dias" in dados["conteudo"]
    assert "empresa.com/reembolso" in dados["conteudo"]


def test_consultar_base_conhecimento_termo_inexistente():
    """Testa se termos inexistentes retornam status 'nao_encontrado' de forma segura."""
    resultado_json = consultar_base_conhecimento("termo_que_nao_existe_xyz_123")
    dados = json.loads(resultado_json)
    assert dados["status"] == "nao_encontrado"


def test_registrar_demanda_persiste_no_sqlite():
    """Testa o registro de demanda no SQLite e verifica se o protocolo e gerado."""
    cliente_teste = "Teste Unitario Silva"
    categoria_teste = "Suporte Tecnico"
    urgencia_teste = "CRITICA"
    resumo_teste = "Servidor instavel no ambiente de homologacao"

    resultado_json = registrar_demanda(
        cliente=cliente_teste,
        categoria=categoria_teste,
        urgencia=urgencia_teste,
        resumo=resumo_teste
    )
    dados = json.loads(resultado_json)

    assert "protocolo" in dados
    assert dados["protocolo"].startswith("REQ-")
    assert dados["cliente"] == cliente_teste
    assert dados["urgencia"] == "CRITICA"
    assert dados["status"] == "REGISTRADO"
    assert os.path.exists(DB_PATH)


def test_listar_historico_chamados_recupera_registro():
    """Testa se uma demanda recem-criada e listada na busca de historico."""
    cliente_busca = "Cliente Busca Historico"
    registrar_demanda(
        cliente=cliente_busca,
        categoria="Comercial",
        urgencia="BAIXA",
        resumo="Duvida sobre plano"
    )

    resultado_json = listar_historico_chamados(cliente_busca)
    dados = json.loads(resultado_json)

    assert dados["status"] == "sucesso"
    assert dados["total"] >= 1
    assert any(c["cliente"] == cliente_busca for c in dados["chamados"])


def test_enviar_alerta_slack_formato():
    """Testa se o alerta de Slack retorna payload estruturado com canal e status."""
    canal = "#operacoes-criticas"
    msg = "Teste de alerta de incidente"
    resultado_json = enviar_alerta_slack(canal=canal, mensagem=msg)
    dados = json.loads(resultado_json)

    assert dados["status"] == "enviado"
    assert dados["canal"] == canal
    assert dados["mensagem"] == msg
