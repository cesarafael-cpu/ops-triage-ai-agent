"""
tests/test_tools.py - Testes Unitarios Deterministicos com Isolamento Hermetico (tmp_path).
Garante que nenhum teste afete o banco real 'data/ops_triage.db'.
"""

import json
import os
import pytest
import tools
from tools import (
    consultar_base_conhecimento,
    registrar_demanda,
    listar_historico_chamados,
    enviar_alerta_slack,
)


@pytest.fixture(autouse=True)
def isolar_banco_de_dados(tmp_path, monkeypatch):
    """
    Fixture automatica que redireciona o DB_PATH para um diretorio temporario.
    Executado antes de cada teste, garantindo estado limpo e isolado.
    """
    banco_temporario = str(tmp_path / "test_ops_triage.db")
    monkeypatch.setattr(tools, "DB_PATH", banco_temporario)
    tools.inicializar_banco()
    yield banco_temporario


def test_consultar_base_conhecimento_encontra_reembolso():
    """Testa se a busca por 'reembolso' retorna a politica oficial de 7 dias."""
    resultado_json = consultar_base_conhecimento("reembolso")
    dados = json.loads(resultado_json)
    assert dados["status"] == "encontrado"
    assert "7 dias" in dados["conteudo"]
    assert "empresa.com/reembolso" in dados["conteudo"]


def test_consultar_base_conhecimento_termo_inexistente():
    """Testa se termos inexistentes retornam status 'nao_encontrado' com seguranca."""
    resultado_json = consultar_base_conhecimento("termo_que_nao_existe_xyz_123")
    dados = json.loads(resultado_json)
    assert dados["status"] == "nao_encontrado"


def test_registrar_demanda_persiste_no_banco_isolado():
    """Testa se a demanda e persistida no banco SQLite isolado do teste."""
    cliente_teste = "Teste Isolado Silva"
    resultado_json = registrar_demanda(
        cliente=cliente_teste,
        categoria="Suporte Tecnico",
        urgencia="CRITICA",
        resumo="Servidor de homologacao caiu"
    )
    dados = json.loads(resultado_json)

    assert "protocolo" in dados
    assert dados["protocolo"].startswith("REQ-")
    assert dados["cliente"] == cliente_teste
    assert dados["urgencia"] == "CRITICA"
    assert dados["status"] == "REGISTRADO"
    assert os.path.exists(tools.DB_PATH)


def test_listar_historico_chamados_recupera_registro_no_banco_isolado():
    """Testa o isolamento e recuperacao de historico no banco de teste."""
    cliente_busca = "Cliente Busca Historico"
    registrar_demanda(
        cliente=cliente_busca,
        categoria="Comercial",
        urgencia="BAIXA",
        resumo="Duvida sobre migracao de plano"
    )

    resultado_json = listar_historico_chamados(cliente_busca)
    dados = json.loads(resultado_json)

    assert dados["status"] == "sucesso"
    assert dados["total"] == 1
    assert dados["chamados"][0]["cliente"] == cliente_busca


def test_enviar_alerta_slack_formato():
    """Testa o formato e payload do alerta de Slack."""
    canal = "#operacoes-criticas"
    msg = "Teste de alerta emergencial"
    resultado_json = enviar_alerta_slack(canal=canal, mensagem=msg)
    dados = json.loads(resultado_json)

    assert dados["status"] == "enviado"
    assert dados["canal"] == canal
    assert dados["mensagem"] == msg
