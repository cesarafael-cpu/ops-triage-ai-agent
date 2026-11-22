# ResearchAnalyst AI - Agente Especialista em Pesquisa e Síntese Técnica (RAG Avançado)

Agente autônomo projetado para auditoria documental, análise de relatórios financeiros e governança técnica utilizando **Retrieval-Augmented Generation (RAG)**, busca semântica por embeddings e cálculo determinístico via Tool Calling.

---

## 🏗️ Arquitetura do Motor RAG

```mermaid
flowchart TD
    A[Consulta do Analista / Usuário] --> B[ResearchAnalyst AI - Gemini]
    
    subgraph Cognitive Loop & Tool Calling
        B --> C{Análise da Dúvida}
        C -->|Dúvida Documental| D["pesquisar_documentos_tecnicos(query)"]
        C -->|Métrica Numérica| E["calcular_metrica_financeira(op, a, b)"]
    end
    
    subgraph Vector Retrieval Engine
        D --> F[VectorStoreRAG]
        F -->|Cosine Similarity| G[(Embeddings em Memória / Chunked Docs)]
        G --> H[Top-K Trechos Rastreáveis]
    end
    
    H --> I[Síntese com Citação de Fontes]
    E --> I
    I --> J[Relatório Executivo + Métricas de Tokens e Latência]
```

---

## 🚀 Como Executar

### 1. Teste Automatizado:
```bash
python -m research_agent.agent --teste
```

### 2. Modo Console Interativo:
```bash
python -m research_agent.agent
```

### 3. Rodar Testes Unitários de RAG:
```bash
pytest research_agent/tests/
```
