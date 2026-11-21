"""
tools.py - Ferramentas (Tools) disponíveis para o Agente de Operações.
Em projetos reais, estas funções chamam APIs reais (Slack Webhooks, Google Sheets API, Notion, etc).
"""

import json
from datetime import datetime

# Banco de dados simulado em memória para o FAQ / Base de Conhecimento
KNOWLEDGE_BASE = {
    "reembolso": "Politica de Reembolso: O cliente tem ate 7 dias corridos para solicitar. Envie link: empresa.com/reembolso.",
    "erro_login": "Erro 500 no login: Orientar o usuario a limpar cookies/cache ou resetar a senha via portal de acesso.",
    "faturamento": "Faturamento/NF: Notas sao emitidas sempre no dia 5 util de cada mes pelo setor financeiro (financeiro@empresa.com).",
    "status_servidor": "Sistemas operando normalmente (99.9% uptime). Nenhuma instabilidade detectada hoje."
}

def consultar_base_conhecimento(termo_busca: str) -> str:
    """
    Pesquisa informacoes internas na base de conhecimento da empresa (FAQ, politicas, procedimentos).
    
    Args:
        termo_busca: Palavra-chave ou topico a ser pesquisado (ex: 'reembolso', 'erro_login', 'faturamento').
    """
    print(f"\n[TOOL EXECUTADA] consultar_base_conhecimento com termo: '{termo_busca}'")
    termo = termo_busca.lower()
    for chave, conteudo in KNOWLEDGE_BASE.items():
        if chave in termo or termo in chave:
            return json.dumps({"status": "encontrado", "resultado": conteudo}, ensure_ascii=False)
            
    return json.dumps({"status": "nao_encontrado", "mensagem": "Nenhum procedimento especifico encontrado. Recomenda-se encaminhamento humano."}, ensure_ascii=False)


def registrar_demanda(cliente: str, categoria: str, urgencia: str, resumo: str) -> str:
    """
    Registra uma solicitacao ou chamado no sistema interno / planilha de operacoes.
    
    Args:
        cliente: Nome ou identificador do cliente/remetente.
        categoria: Categoria da solicitacao (ex: 'Suporte Tecnico', 'Financeiro', 'Comercial', 'Outros').
        urgencia: Nivel de criticidade ('BAIXA', 'MEDIA', 'ALTA', 'CRITICA').
        resumo: Sintese em 1 linha do problema ou pedido.
    """
    registro = {
        "id_protocolo": f"REQ-{datetime.now().strftime('%H%M%S')}",
        "data_hora": datetime.now().isoformat(),
        "cliente": cliente,
        "categoria": categoria,
        "urgencia": urgencia.upper(),
        "resumo": resumo,
        "status": "REGISTRADO"
    }
    print(f"\n[TOOL EXECUTADA] registrar_demanda: {registro['id_protocolo']} | {cliente} | Urgencia: {registro['urgencia']}")
    return json.dumps(registro, ensure_ascii=False)


def enviar_alerta_slack(canal: str, mensagem: str) -> str:
    """
    Dispara um alerta imediato no Slack / Teams para a equipe responsavel.
    Deve ser usada principalmente para demandas com urgencia ALTA ou CRITICA.
    
    Args:
        canal: Nome do canal de destino (ex: '#operacoes-criticas', '#suporte-geral').
        mensagem: Texto de alerta detalhado com contexto e solicitacao de acao.
    """
    alerta = {
        "status": "enviado",
        "canal": canal,
        "mensagem": mensagem,
        "timestamp": datetime.now().isoformat()
    }
    print(f"\n[TOOL EXECUTADA] enviar_alerta_slack no canal '{canal}': {mensagem}")
    return json.dumps(alerta, ensure_ascii=False)
