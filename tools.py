"""
tools.py - Ferramentas com SQLite Nativo, Tipagem Estrita e Busca em Base de Conhecimento.
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Literal

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "ops_triage.db")
KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), "data", "procedimentos.txt")

# Tipagens estritas para garantir que o LLM so utilize categorias e urgencias validas
UrgenciaType = Literal["BAIXA", "MEDIA", "ALTA", "CRITICA"]
CategoriaType = Literal["Suporte Tecnico", "Financeiro", "Comercial", "Operacoes", "Outros"]


def inicializar_banco():
    """Garante a criacao da tabela de chamados e indices no SQLite."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chamados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocolo TEXT UNIQUE NOT NULL,
                data_hora TEXT NOT NULL,
                cliente TEXT NOT NULL,
                categoria TEXT NOT NULL,
                urgencia TEXT NOT NULL,
                resumo TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cliente ON chamados(cliente)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_urgencia ON chamados(urgencia)")
        conn.commit()


# Inicializa o banco automaticamente ao carregar o modulo
inicializar_banco()


def consultar_base_conhecimento(termo_busca: str) -> str:
    """
    Pesquisa procedimentos e politicas internas na base de conhecimento oficial (data/procedimentos.txt).
    
    Args:
        termo_busca: Palavra-chave ou assunto a consultar (ex: 'reembolso', 'login', 'nota fiscal', 'desconto').
    """
    print(f"\n⚙️  [TOOL] consultar_base_conhecimento(termo='{termo_busca}')")
    if not os.path.exists(KNOWLEDGE_PATH):
        return json.dumps({"status": "erro", "mensagem": "Arquivo de procedimentos nao encontrado."}, ensure_ascii=False)

    with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    resultados = []
    bloco_atual = []
    relevante = False
    termo = termo_busca.lower()

    for linha in linhas:
        if linha.startswith("["):
            if relevante and bloco_atual:
                resultados.append("".join(bloco_atual).strip())
            bloco_atual = [linha]
            relevante = termo in linha.lower()
        else:
            bloco_atual.append(linha)
            if termo in linha.lower():
                relevante = True

    if relevante and bloco_atual:
        resultados.append("".join(bloco_atual).strip())

    if resultados:
        return json.dumps({"status": "encontrado", "conteudo": "\n\n".join(resultados)}, ensure_ascii=False)
    
    return json.dumps({"status": "nao_encontrado", "mensagem": "Nenhum procedimento especifico encontrado."}, ensure_ascii=False)


def registrar_demanda(cliente: str, categoria: CategoriaType, urgencia: UrgenciaType, resumo: str) -> str:
    """
    Registra um chamado ou incidente diretamente no banco de dados relacional SQLite de operacoes.
    
    Args:
        cliente: Nome ou identificador do cliente/solicitante.
        categoria: Categoria estrita da demanda ('Suporte Tecnico', 'Financeiro', 'Comercial', 'Operacoes', 'Outros').
        urgencia: Nivel de criticidade estrito ('BAIXA', 'MEDIA', 'ALTA', 'CRITICA').
        resumo: Sintese em 1 linha do problema ou pedido.
    """
    inicializar_banco()
    sufixo_unico = uuid.uuid4().hex[:6].upper()
    protocolo = f"REQ-{datetime.now().strftime('%Y%m%d')}-{sufixo_unico}"
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "REGISTRADO"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chamados (protocolo, data_hora, cliente, categoria, urgencia, resumo, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (protocolo, data_hora, cliente, categoria, urgencia, resumo, status))
        conn.commit()

    registro = {
        "protocolo": protocolo,
        "data_hora": data_hora,
        "cliente": cliente,
        "categoria": categoria,
        "urgencia": urgencia,
        "resumo": resumo,
        "status": status,
        "armazenamento": "SQLite (data/ops_triage.db)"
    }
    print(f"\n💾 [TOOL] registrar_demanda: Gravado em SQLite -> {protocolo} | {cliente} | {urgencia}")
    return json.dumps(registro, ensure_ascii=False)


def listar_historico_chamados(cliente: str) -> str:
    """
    Consulta o historico de chamados anteriores ja registrados para um determinado cliente no SQLite.
    
    Args:
        cliente: Nome ou parte do nome do solicitante para pesquisa.
    """
    print(f"\n🔍 [TOOL] listar_historico_chamados(cliente='{cliente}')")
    inicializar_banco()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT protocolo, data_hora, cliente, categoria, urgencia, resumo, status
            FROM chamados
            WHERE cliente LIKE ?
            ORDER BY id DESC
            LIMIT 5
        """, (f"%{cliente}%",))
        rows = cursor.fetchall()

    if rows:
        historico = [dict(row) for row in rows]
        return json.dumps({"status": "sucesso", "total": len(historico), "chamados": historico}, ensure_ascii=False)
    
    return json.dumps({"status": "vazio", "mensagem": f"Nenhum chamado anterior encontrado para '{cliente}'."}, ensure_ascii=False)


def enviar_alerta_slack(canal: str, mensagem: str) -> str:
    """
    Dispara uma notificacao emergencial para a equipe no Slack / Teams.
    Deve ser acionado prioritariamente para incidentes de urgencia ALTA ou CRITICA.
    
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
    print(f"\n🚨 [TOOL] enviar_alerta_slack no canal '{canal}':\n{mensagem}\n")
    return json.dumps(alerta, ensure_ascii=False)
