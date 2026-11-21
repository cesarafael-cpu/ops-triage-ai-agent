# OpsAgent - Agente Autônomo de Triagem e Operações Corporativas

Este projeto faz parte do portfólio de **AI Engineering & AI Agents**, demonstrando a criação de um agente autônomo com capacidades de **Tool Calling** (chamada de ferramentas), classificação de criticidade e automação de fluxos operacionais corporativos.

---

## 🎯 Problema de Negócio Resolvido
Equipes de operações e suporte frequentemente sofrem com sobrecarga de e-mails e solicitações não estruturadas. Esse agente atua na primeira camada:
1. **Analisa a criticidade** da solicitação em tempo real.
2. **Consulta a base interna de conhecimento** (FAQ / Procedimentos).
3. **Registra automaticamente o chamado** no sistema interno / CRM.
4. **Aciona a equipe de emergência** (Slack/Teams) caso o incidente seja classificado como ALTA ou CRÍTICA urgência.
5. **Gera a resposta rascunhada** pronta para envio.

---

## 🛠️ Tecnologias Utilizadas
* **Python 3.10+**
* **Google GenAI SDK (`google-genai`)**
* **Model:** Gemini 2.5 Flash (com Function Calling nativo)
* **Architecture:** ReAct / Tool-calling loop

---

## 🚀 Como Executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Chave de API
Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```
Edite o arquivo `.env` e insira sua chave gratuita do Google AI Studio:
```env
GEMINI_API_KEY="sua_chave_aqui"
```

### 3. Rodar o Agente
```bash
python agent.py
```
