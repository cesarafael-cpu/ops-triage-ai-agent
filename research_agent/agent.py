"""
research_agent/agent.py - Agente Especialista de Pesquisa e Analise Tecnica (RAG Avancado).
"""

import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

# Garante path correto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from research_agent.tools import pesquisar_documentos_tecnicos, calcular_metrica_financeira

load_dotenv()

SYSTEM_INSTRUCTION_RAG = """
Voce e o 'ResearchAnalyst AI', um Agente Especialista Senior em Pesquisa, Auditoria Tecnica e Sintese Documental.
Sua funcao e analisar relatorios financeiros, estrategicos e regulatorios com rigor analitico, precisao e rastreabilidade total.

DIRETRIZES DE EXECUCAO E AUDITORIA:
1. NUNCA responda baseado apenas em suposicoes gerais se houver documentos disponiveis. Sempre acione 'pesquisar_documentos_tecnicos' para ancorar suas conclusoes nos dados reais.
2. Se houver calculo de margem, crescimento ou variacao, NUNCA calcule de cabeca: chame 'calcular_metrica_financeira' para precisao matematica absoluta.
3. RASTREABILIDADE OBRIGATORIA DE FONTES:
   - Ao citar qualquer dado, risco ou fato, cite explicitamente a fonte no formato:
     `[Fonte: <documento>, Seção: <secao>]`
4. PADRAO DE RESPOSTA EXECUTIVA:
   - **Síntese Executiva:** 1 a 2 paragrafos com a conclusao central.
   - **Evidências e Pontos-Chave:** Lista de metricas, citando as fontes exatas.
   - **Análise Crítica & Implicações:** Avaliacao de riscos e impacto operacional.
   - **Auditoria de Fontes:** Lista consolidada dos documentos consultados.
"""

MODELOS_DISPONIVEIS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
]


def executar_pesquisa(pergunta_usuario: str):
    """Executa o agente RAG resolvendo a busca semantica e formatando a analise tecnica."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n[ERRO] A variavel GEMINI_API_KEY nao foi configurada no arquivo .env.")
        return

    client = genai.Client(api_key=api_key)

    tools = [
        pesquisar_documentos_tecnicos,
        calcular_metrica_financeira,
    ]

    print("\n" + "=" * 70)
    print(f"📖 CONSULTA DE PESQUISA:\n{pergunta_usuario}")
    print("=" * 70)

    for modelo in MODELOS_DISPONIVEIS:
        try:
            print(f"🤖 ResearchAnalyst analisando documentos (Modelo: {modelo})...")
            inicio = time.perf_counter()

            chat = client.chats.create(
                model=modelo,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION_RAG,
                    tools=tools,
                    temperature=0.1,  # Alto determinismo analitico
                ),
            )
            response = chat.send_message(pergunta_usuario)
            duracao = time.perf_counter() - inicio

            print("\n" + "=" * 70)
            print("📑 SÍNTESE TÉCNICA E RELATÓRIO DO AGENTE:")
            print("=" * 70)
            print(response.text)

            # Metricas de Observabilidade
            print("\n" + "─" * 70)
            print("📊 MÉTRICAS DE EXECUÇÃO & OBSERVABILIDADE:")
            print(f"  • Modelo Utilizado:  {modelo}")
            print(f"  • Latência Total:    {duracao:.2f}s")
            usage = getattr(response, "usage_metadata", None)
            if usage:
                print(f"  • Tokens Entrada:   {getattr(usage, 'prompt_token_count', 'N/A')}")
                print(f"  • Tokens Saída:     {getattr(usage, 'candidates_token_count', 'N/A')}")
                print(f"  • Total Tokens:     {getattr(usage, 'total_token_count', 'N/A')}")
            print("─" * 70)
            return

        except (ClientError, ServerError) as e:
            if "429" in str(e) or "503" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"⚠️ Modelo {modelo} ocupado/cota excedida. Tentando fallback...")
                continue
            raise e
        except Exception as e:
            if "404" in str(e):
                continue
            raise e

    print("\n❌ Nao foi possivel conectar aos modelos no momento.")


def console_pesquisa():
    """Console interativo para pesquisa em profundidade."""
    print("\n" + "=" * 70)
    print("🔬 ResearchAnalyst AI - CONSOLE DE ANÁLISE TÉCNICA E DOCUMENTAL")
    print("Faça perguntas complexas sobre os relatórios corporativos da empresa.")
    print("Digite 'sair' para encerrar.")
    print("=" * 70)

    while True:
        try:
            print("\n" + "-" * 70)
            pergunta = input("Pergunta de pesquisa (ou 'sair'): ").strip()
            if not pergunta:
                continue
            if pergunta.lower() in ["sair", "exit", "quit"]:
                print("\nEncerrando ResearchAnalyst. Ate logo!")
                break
            executar_pesquisa(pergunta)
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando ResearchAnalyst.")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--teste":
        consulta_teste = (
            "Qual foi a receita e o EBITDA da TechCorp no Q3 2026? "
            "Quais são os principais riscos operacionais apontados e como o projeto de IA impactou os custos?"
        )
        executar_pesquisa(consulta_teste)
    else:
        console_pesquisa()
