"""Servidor completo da aula I. Leia junto ao capítulo 3 do notebook.

HTTP:  python servidor_mcp_bv.py
stdio: python servidor_mcp_bv.py --transport stdio
Nenhuma credencial ou chamada a modelo é necessária neste servidor.
"""

# 1. Bibliotecas e instância: o framework cuida da comunicação MCP.
import argparse
import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("BV — Laboratório guiado de MCP")

# 2. Contratos: nomes, tipos, limites e descrições chegam ao consumidor.
Valor = Annotated[float, Field(gt=0, le=10_000_000, allow_inf_nan=False,
                              description="Principal em reais, maior que zero.")]
Parcelas = Annotated[int, Field(ge=1, le=360, strict=True,
                                description="Número inteiro de prestações mensais.")]
Taxa = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False,
                             description="Taxa decimal: 0.0199 equivale a 1,99%.")]


# 3. Ferramenta: código de cálculo real, registrado com @mcp.tool.
@mcp.tool
def simular_credito(valor: Valor, parcelas: Parcelas,
                    taxa_mensal: Taxa = 0.0199) -> dict:
    """Calcule prestações constantes com uma taxa informada.

    Simulação matemática, sem contratação, IOF, tarifas ou seguros.
    O total é a parcela arredondada multiplicada pelo prazo.
    """
    principal = Decimal(str(valor))
    taxa = Decimal(str(taxa_mensal))
    if taxa == 0:
        parcela = principal / parcelas
    else:
        fator = (1 + taxa) ** parcelas
        parcela = principal * taxa * fator / (fator - 1)
    parcela = parcela.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = parcela * parcelas
    return {
        "valor_solicitado": float(principal), "parcelas": parcelas,
        "taxa_mensal": float(taxa), "valor_parcela": float(parcela),
        "total_estimado": float(total), "juros_estimados": float(total-principal),
        "premissas": "Taxa informada; sem tributos, seguros, tarifas e ajuste residual. Não é oferta nem CET.",
    }


# 4. Outras capacidades: cada ferramenta tem uma finalidade diferente.
@mcp.tool
def simular_encargo_parametrizado(
    valor: Valor,
    dias: Annotated[int, Field(ge=1, le=3650, strict=True)],
    taxa_diaria: Taxa,
    taxa_adicional: Taxa,
) -> dict:
    """Calcule um encargo sobre base constante usando taxas fornecidas.

    Fórmula: valor * (taxa_diaria * dias + taxa_adicional).
    Exercício parametrizado; não calcula IOF devido nem consulta alíquotas.
    """
    encargo = Decimal(str(valor)) * (
        Decimal(str(taxa_diaria))*dias + Decimal(str(taxa_adicional))
    )
    return {"encargo": float(encargo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "dias": dias, "premissas": "Base constante e taxas fornecidas. Não é cálculo tributário."}


@mcp.tool
def anualizar_taxa_mensal(taxa_mensal: Taxa) -> dict:
    """Converta uma taxa mensal em anual equivalente por capitalização composta.

    Fórmula: (1 + taxa_mensal)**12 - 1. Não calcula CET de um fluxo financeiro.
    """
    anual = (1 + Decimal(str(taxa_mensal)))**12 - 1
    return {"taxa_mensal": taxa_mensal, "taxa_anual_equivalente": float(anual),
            "premissas": "Equivalência matemática de taxas; não inclui outros custos."}


# 5. Resource e prompt: dados e instruções também têm contratos próprios.
@mcp.resource("credito://premissas", mime_type="application/json")
def premissas() -> str:
    """Informe as condições de interpretação das ferramentas do laboratório."""
    return json.dumps({"moeda": "BRL", "taxas": "fornecidas pelo usuário ou padrão ilustrativo",
                       "exclui": ["tributos", "seguros", "tarifas", "ajuste residual"],
                       "finalidade": "ensino; não contrata crédito"}, ensure_ascii=False)


@mcp.prompt
def explicar_simulacao(publico: str = "aluno iniciante") -> str:
    """Entregue um roteiro de explicação; esta operação não chama um modelo."""
    return (f"Explique ao {publico} o resultado recebido da simulação. "
            "Diferencie principal, parcela, juros e total. Apresente as premissas. "
            "Não invente valores nem trate o resultado como oferta ou CET.")


# 6. Execução: importar o arquivo registra funções; executar inicia o servidor.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport", choices=["http", "stdio"], default="http")
    parser.add_argument("--port", type=int, default=8875)
    args = parser.parse_args()
    if args.transport == "http":
        mcp.run(transport="http", host="127.0.0.1", port=args.port, show_banner=False)
    else:
        mcp.run(transport="stdio", show_banner=False)
