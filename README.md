<div align="center">

# BV Assist

### Copiloto Corporativo Interno — Banco BV

*Projeto Integrador · Módulos 3 e 4 · Prof. Ioannis Eleftheriou*

---

![MCP](https://img.shields.io/badge/MCP-Protocol-0057A8?style=flat-square)
![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?style=flat-square&logo=google)
![CrewAI](https://img.shields.io/badge/CrewAI-Multiagente-6B21A8?style=flat-square)
![LangSmith](https://img.shields.io/badge/LangSmith-Observabilidade-F97316?style=flat-square)
![Model Armor](https://img.shields.io/badge/Model_Armor-Guardrails-DC2626?style=flat-square)

</div>

---

## Índice

1. [A dor que originou o case](#a-dor-que-originou-o-case)
2. [Por que este case e não outro?](#por-que-este-case-e-não-outro)
3. [O que o BV Assist resolve](#o-que-o-bv-assist-resolve)
4. [Escopo deliberadamente limitado](#escopo-deliberadamente-limitado)
5. [Referência cruzada](#referência-cruzada)
6. [Ideias de copiloto para seu projeto](#ideias-de-copiloto-para-seu-projeto)

---

## A dor que originou o case

Em grandes bancos, **o conhecimento corporativo existe — mas está inacessível**.

Políticas internas estão em PDFs guardados em portais que ninguém consegue navegar. Abrir um chamado no service desk exige saber o formulário certo, a fila certa, a severidade certa. Um colaborador novo leva semanas para aprender "como as coisas funcionam aqui".

**O resultado prático:**

| Sintoma | Impacto |
|--------|---------|
| Funcionários enviam e-mails sobre o que políticas já respondem | Retrabalho contínuo de RH e Jurídico |
| Chamados abertos com severidade errada | SLAs estourados e realocações manuais |
| Times de TI e RH respondem perguntas repetitivas | Horas de trabalho qualificado desperdiçadas |
| Fricção invisível no onboarding | Custo humano real, ausente dos relatórios |

---

## Por que este case e não outro?

Antes de escrever uma linha de código, aplicamos **7 critérios objetivos** para validar se este era o problema certo a resolver.

| Critério | Análise |
|----------|---------|
| **Aderência ao problema** | O agente precisa consultar dados E executar ações (abrir ticket) — não é só Q&A |
| **Governança** | Banco é regulado: toda decisão precisa de trilha de auditoria |
| **Segurança** | Dados sensíveis de colaboradores + risco de prompt injection exige guardrails reais |
| **Extensibilidade** | O mesmo padrão (MCP + agente) escala para outros domínios do banco |
| **Custo controlado** | Volume alto de consultas diárias torna TCO uma variável crítica |
| **Debugabilidade** | Em produção financeira, "o agente errou" não é resposta suficiente |
| **Portabilidade** | Stack baseada em protocolo aberto (MCP) permite trocar LLM sem reescrever integrações |

> Todos os 7 critérios apontaram na mesma direção. Este não é um case escolhido por estética de apresentação — é um **problema real com critérios verificáveis**.

---

## O que o BV Assist resolve

| Cenário | Antes | Depois |
|---------|-------|--------|
| **Consulta de política** | Portal → pesquisa → PDF → leitura | Resposta em menos de 30 segundos, com fonte e slug da política |
| **Abertura de chamado** | Formulário → fila errada → categorização manual → realocação | Chamado aberto com severidade validada e SLA informado na mesma conversa |

---

## Escopo deliberadamente limitado

O BV Assist **não** é um sistema de todos os problemas do banco. Ele resolve dois fluxos com profundidade:

1. **Consulta de políticas internas** — busca semântica, resposta fundamentada, sem alucinação
2. **Abertura de chamados no service desk** — com validação de severidade e aprovação humana para casos críticos

Esse escopo foi escolhido porque cobre **toda a ementa técnica do curso** sem depender de sistemas reais do banco:

| Tecnologia | Papel no projeto |
|------------|-----------------|
| **MCP** | Servidor com `resource` de políticas e `tool` de tickets |
| **Google ADK** | Copiloto único que consome o servidor MCP |
| **Model Armor** | Filtra entrada (injection) e saída (PII de colaboradores) |
| **CrewAI** | Pipeline multiagente: Triager → Especialista → Auditor |
| **LangSmith** | Trace de cada consulta e cada abertura de chamado |
| **FinOps / TCO** | Custo por jornada de atendimento vs. custo humano equivalente |

---



## Ideias de copiloto para seu projeto

Quatro domínios alternativos que cobrem a mesma ementa técnica — cada um com um problema real e critérios verificáveis.

---

### 1 · Copiloto de Onboarding e RH Interno

Assistente para apoiar novos colaboradores nos primeiros 90 dias. Responde dúvidas sobre benefícios, trilhas obrigatórias, acesso a sistemas e políticas de trabalho híbrido, além de abrir solicitações de onboarding para RH e TI.

**Valor didático:** consulta de base documental + execução de ações com aprovação humana em casos sensíveis.

---

### 2 · Copiloto de Incidentes Operacionais de TI

Assistente para times de suporte durante incidentes. Classifica severidade, consulta runbooks internos, sugere procedimentos de contenção e cria/atualiza chamados com rastreabilidade completa.

**Valor didático:** fluxo multiagente, guardrails de segurança e observabilidade ponta a ponta.

---

### 3 · Copiloto de Crédito e Formalização

Apoia analistas na jornada de crédito PJ/PF: consulta políticas internas de aprovação, valida documentação mínima por produto, sinaliza pendências e abre solicitação de revisão para mesa de crédito.

**Valor didático:** regras de negócio complexas, decisões com aprovação humana e trilha de auditoria.

---

### 4 · Copiloto de Fraude e Segurança Transacional

Ajuda times de prevenção a fraude a classificar alertas, consultar playbooks internos, sugerir ações de contenção (bloqueio, escalonamento, contato com cliente) e registrar incidentes no sistema interno.

**Valor didático:** guardrails robustos, pipeline triagem → investigação → auditoria e observabilidade detalhada.

---

<div align="center">

*Projeto Integrador · Módulos 3 e 4 · Prof. Ioannis Eleftheriou*

</div>
