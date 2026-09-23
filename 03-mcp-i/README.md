# README · Comece a aula MCP I aqui

Este é um **laboratório guiado pronto**. O professor apresenta e explica os trechos; o aluno executa e interpreta. A aula começa consumindo documentação pública, depois explica nosso servidor Python e finalmente reúne ferramentas em um agente.

| Você quer… | Abra |
|---|---|
| Executar e acompanhar a aula | [AULA_01_MCP_I.ipynb](./AULA_01_MCP_I.ipynb) no VS Code. |
| Inspecionar o código do servidor | [servidor_mcp_bv.py](./servidor_mcp_bv.py). |

## Neste computador

Selecione o kernel **Python · Aula 01 MCP**. Ele utiliza `./.venv/Scripts/python.exe`. A configuração privada do modelo fica no arquivo local `.env`, que não deve ser enviado ao GitHub.

Execute as células na ordem. Antes das chamadas locais do bloco 3, mantenha o servidor aberto em um terminal desta pasta:

```powershell
& './.venv/Scripts/python.exe' servidor_mcp_bv.py
```

Se ele já estiver rodando, use a instância existente. O endpoint é `http://127.0.0.1:8875/mcp`, para clientes MCP. A aula I usa o **MCP Inspector oficial**, sem interface própria na porta 8881.

## Em outra máquina

Use Python 3.13 e as extensões Python/Jupyter do VS Code. No terminal desta pasta:

```powershell
py -3.13 -m venv .venv
$pythonAula = "./.venv/Scripts/python.exe"
& $pythonAula -m pip install -r requirements.lock.txt
& $pythonAula -m pip check
& $pythonAula -m ipykernel install --user --name bv-mcp-1 --display-name "Python · Aula 01 MCP"
```

Depois selecione o kernel e use `& $pythonAula servidor_mcp_bv.py` para iniciar o servidor no bloco 3. Para o agente, copie `.env.example` para `.env` e preencha sua credencial privada. Não compartilhe esse arquivo. Sem chave, as etapas anteriores ao agente continuam utilizáveis.

O Inspector requer Node 22.19 ou superior:

```powershell
npx -y @modelcontextprotocol/inspector@2.7.0 --server-url http://127.0.0.1:8875/mcp --transport http
```

Abra o endereço de sessão impresso. Ao terminar, Ctrl+C nos terminais que você iniciou. O notebook não gera arquivos nem depende da aula II.

## Verificações locais

No ambiente instalado: `python -m pytest -q -p no:cacheprovider tests`. Os testes usam servidor e cliente reais, sem provedor de modelo. A validação com OpenAI e servidores públicos está descrita em VALIDACAO.md.
## Enviar esta pasta ao GitHub manualmente

Envie os arquivos da aula, `assets/` e `tests/`. Deixe de fora `.venv/` (Python e bibliotecas instaladas), `.env` (chave privada), `.vscode/` e caches. O aluno recria `.venv` com os comandos acima usando `requirements.lock.txt`. Tudo para trabalhar localmente fica nesta pasta.
