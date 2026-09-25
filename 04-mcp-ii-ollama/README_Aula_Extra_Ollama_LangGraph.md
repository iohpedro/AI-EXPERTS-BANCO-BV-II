# Aula Extra - RAG Local com Ollama e LangGraph

**Banco BV - AI Experts | Ecossistema Moderno de Agentes**

Esta aula extra cria uma ponte entre os notebooks de MCP/RAG e a Aula 05 de Google ADK.

O objetivo é replicar a capacidade de consulta documental do regulamento de fundos, mas sem depender de chave da OpenAI. Tudo roda localmente com Ollama:

- LLM local para classificação e geração de resposta.
- Embeddings locais para indexação semântica.
- ChromaDB como vector store local.
- LangGraph como orquestrador do workflow.

## Arquivo principal

- `BV_AI_EXPERT_EXTRA_OLLAMA_LANGGRAPH_RAG.ipynb`

## Pré-requisitos

1. Instalar o Ollama:

   <https://ollama.com/download>

2. Baixar os modelos usados na aula:

   ```bash
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   ```

3. Garantir que o Ollama esteja rodando:

   ```bash
   ollama serve
   ```

4. Instalar dependências Python:

   ```bash
   pip install -r requirements.txt
   ```

## Documento usado

A aula reaproveita o PDF:

```text
../Aula 03 - MCP II/data/KNCR_Regulamento_05-2025.pdf
```

Se quiser usar outro documento, ajuste a variável `PDF_PATH` no notebook.

## Resultado da aula

Ao final, o aluno terá um workflow LangGraph com quatro etapas:

```text
pergunta
  -> classificar intenção
  -> recuperar trechos no vector store
  -> gerar resposta com Ollama
  -> formatar resposta final com fontes
```

Também haverá um nó de fora de escopo para perguntas que não pertencem ao domínio documental.

## Observação didática

Esta aula não substitui MCP nem Google ADK. Ela mostra uma ideia importante:

> antes de conectar um agente a sistemas externos, o aluno precisa entender como um workflow local decide, recupera contexto, chama modelo e devolve resposta auditável.

