"""Verificações de integração: processos, clientes e ferramentas reais."""
import asyncio
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
import psutil
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def endpoint():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        porta = sock.getsockname()[1]
    with tempfile.TemporaryFile() as log:
        proc = subprocess.Popen(
            [sys.executable, "-B", str(ROOT / "servidor_mcp_bv.py"), "--port", str(porta)],
            stdout=log, stderr=log,
        )
        try:
            for _ in range(100):
                if proc.poll() is not None:
                    raise RuntimeError("Servidor de teste encerrou antes de conectar.")
                with socket.socket() as sock:
                    if sock.connect_ex(("127.0.0.1", porta)) == 0:
                        break
                time.sleep(0.1)
            else:
                raise TimeoutError("Servidor não abriu a porta.")
            yield f"http://127.0.0.1:{porta}/mcp"
        finally:
            try:
                filhos = psutil.Process(proc.pid).children(recursive=True)
            except psutil.NoSuchProcess:
                filhos = []
            for filho in reversed(filhos):
                try:
                    filho.terminate()
                except psutil.NoSuchProcess:
                    pass
            proc.terminate()
            proc.wait(timeout=10)
            _, restantes = psutil.wait_procs(filhos, timeout=5)
            for filho in restantes:
                filho.kill()
            with socket.socket() as sock:
                assert sock.connect_ex(("127.0.0.1", porta)) != 0


def test_descoberta_e_tres_calculos(endpoint):
    async def verificar():
        async with Client(endpoint) as client:
            tools = await client.list_tools()
            assert {t.name for t in tools} == {
                "simular_credito", "simular_encargo_parametrizado", "anualizar_taxa_mensal"
            }
            contrato = next(t for t in tools if t.name == "simular_credito")
            assert contrato.input_schema["properties"]["parcelas"]["minimum"] == 1
            r = await client.call_tool("simular_credito", {"valor": 10000.0, "parcelas": 12})
            assert r.structured_content["valor_parcela"] == 945.02
            assert r.structured_content["total_estimado"] == 11340.24
            r = await client.call_tool("simular_encargo_parametrizado", {
                "valor": 1000.0, "dias": 10, "taxa_diaria": .001, "taxa_adicional": .01
            })
            assert r.structured_content["encargo"] == 20
            r = await client.call_tool("anualizar_taxa_mensal", {"taxa_mensal": .02})
            assert r.structured_content["taxa_anual_equivalente"] == pytest.approx(1.02**12-1)
    asyncio.run(verificar())


@pytest.mark.parametrize("argumentos", [
    {"valor": 1000.0, "parcelas": 0},
    {"valor": -1.0, "parcelas": 12},
    {"valor": 1000.0, "parcelas": 1.5},
    {"valor": 1000.0, "parcelas": True},
    {"valor": 1000.0, "parcelas": 361},
    {"valor": 1000.0, "parcelas": 12, "taxa_mensal": -0.1},
])
def test_argumentos_invalidos(endpoint, argumentos):
    async def verificar():
        async with Client(endpoint) as client:
            r = await client.call_tool("simular_credito", argumentos, raise_on_error=False)
            assert r.is_error
    asyncio.run(verificar())


def test_zero_juros_resource_prompt(endpoint):
    async def verificar():
        async with Client(endpoint) as client:
            r = await client.call_tool("simular_credito", {"valor": 1200.0, "parcelas": 12, "taxa_mensal": 0})
            assert r.structured_content["valor_parcela"] == 100
            assert r.structured_content["juros_estimados"] == 0
            r = await client.read_resource("credito://premissas")
            assert "BRL" in r[0].text
            p = await client.get_prompt("explicar_simulacao", {"publico": "turma"})
            assert "turma" in p.messages[0].content.text
    asyncio.run(verificar())


def test_stdio_mesmo_servidor():
    async def verificar():
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as log:
            transport = StdioTransport(command=sys.executable,
                args=["-B", str(ROOT / "servidor_mcp_bv.py"), "--transport", "stdio"], log_file=log)
            async with Client(transport) as client:
                r = await client.call_tool("simular_credito", {"valor": 1200.0, "parcelas": 12, "taxa_mensal": 0})
                assert r.structured_content["valor_parcela"] == 100
    asyncio.run(verificar())


def test_servidor_indisponivel():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        porta = sock.getsockname()[1]
        async def verificar():
            with pytest.raises(Exception):
                async with Client(f"http://127.0.0.1:{porta}/mcp", timeout=2) as client:
                    await client.list_tools()
        asyncio.run(verificar())
