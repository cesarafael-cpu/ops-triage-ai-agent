"""
agent.py - Agente de Triagem e Operacoes Corporativas com Tool Calling e Fallback de Modelos.
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError

# Importa as ferramentas criadas
from tools import (
    consultar_base_conhecimento,
    registrar_demanda,
    enviar_alerta_slack,
)

load_dotenv()

SYSTEM_INSTRUCTION = """
Voce e o 'OpsAgent', um Agente Especialista em Triagem e Automacao de Operacoes Corporativas.
Sua funcao e analisar solicitacoes recebidas por email ou canais internos, agir de forma proativa e estruturada:

DIRETRIZES DE EXECUCAO:
1. Sempre analise o remetente, o contexto e o grau de urgencia ('BAIXA', 'MEDIA', 'ALTA', 'CRITICA').
2. Antes de responder:
   - Se for uma duvida sobre politicas, erros ou sistemas, CONSULTE a base de conhecimento com 'consultar_base_conhecimento'.
   - SEMPRE registre o chamado com 'registrar_demanda' para rastreabilidade operacional.
   - Se a urgencia for ALTA ou CRITICA, envie um alerta com 'enviar_alerta_slack' para '#operacoes-criticas'.
3. Formate sua resposta final de forma profissional:
   - Resumo da acao tomada.
   - Protocolo gerado.
   - Resposta/Rascunho orientador pronto para envio ao cliente/usuario.
"""

# Lista de modelos disponiveis na sua conta
MODELOS_TENTAR = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
]


def executar_agente(mensagem_entrada: str):
    """Executa o agente passando a mensagem e resolvendo o loop de chamadas de ferramentas."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n[ERRO] A variavel GEMINI_API_KEY nao foi configurada no arquivo .env.")
        return

    client = genai.Client(api_key=api_key)

    # Ferramentas disponiveis
    tools = [
        consultar_base_conhecimento,
        registrar_demanda,
        enviar_alerta_slack,
    ]

    print("\n" + "=" * 60)
    print(f"📥 ENTRADA RECEBIDA:\n{mensagem_entrada}")
    print("=" * 60)

    for modelo in MODELOS_TENTAR:
        try:
            print(f"🤖 Tentando modelo: {modelo}...")
            chat = client.chats.create(
                model=modelo,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=tools,
                    temperature=0.2,
                ),
            )
            response = chat.send_message(mensagem_entrada)
            print("\n" + "=" * 60)
            print(f"📤 RESPOSTA FINAL DO AGENTE (Gerada por {modelo}):")
            print("=" * 60)
            print(response.text)
            return
        except ServerError as e:
            print(f"⚠️ Modelo {modelo} com alta demanda ({e.code}). Tentando alternativa...")
        except Exception as e:
            # Se for 404 de modelo nao suportado, pula pro proximo
            if "404" in str(e) or "NOT_FOUND" in str(e):
                continue
            raise e

    print("\n❌ Todos os modelos estao momentaneamente ocupados. Tente novamente em alguns segundos.")


if __name__ == "__main__":
    print("\n--- TESTE DO AGENTE DE OPERACOES ---")
    
    # Exemplo 2: Caso Operacional Padrao (Duvida de Reembolso)
    caso_duvida = (
        "De: Mariana Santos (Cliente)\n"
        "Mensagem: Ola, assinei o plano ontem mas me arrependi e gostaria de saber como funciona o reembolso."
    )

    print("\nExecutando Caso 2 (Duvida / Operacional Padrao):")
    executar_agente(caso_duvida)
