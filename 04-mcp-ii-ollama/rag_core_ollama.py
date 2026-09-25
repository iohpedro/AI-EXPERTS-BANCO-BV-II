"""
rag_core_ollama.py

Capacidade especialista de RAG local usando Ollama.

Arquitetura:
    PDF -> chunks -> OllamaEmbeddings -> ChromaDB -> retriever -> ChatOllama -> resposta estruturada
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class FonteConsulta(BaseModel):
    documento: Optional[str] = Field(default=None)
    pagina: Optional[int] = Field(default=None)
    trecho: str


class RespostaRAGOllama(BaseModel):
    pergunta: str
    resposta: str
    fontes: list[FonteConsulta]
    paginas_consultadas: list[int]
    confianca: Literal["alta", "media", "baixa"]
    observacao: str


class RAGLocalOllama:
    def __init__(
        self,
        pdf_path: str,
        persist_directory: str = "vectorstore/chroma_kncr_ollama",
        collection_name: str = "regulamento_kncr_ollama",
        ollama_base_url: str = "http://localhost:11434",
        embedding_model: str = "nomic-embed-text",
        chat_model: str = "llama3.2:3b",
        chunk_size: int = 900,
        chunk_overlap: int = 140,
        k: int = 5,
        recriar_indice: bool = False,
    ):
        self.pdf_path = Path(pdf_path)
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.ollama_base_url = ollama_base_url
        self.embedding_model_name = embedding_model
        self.chat_model_name = chat_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.k = k
        self.recriar_indice = recriar_indice

        self.persist_directory.parent.mkdir(parents=True, exist_ok=True)

        self.embeddings = OllamaEmbeddings(
            model=self.embedding_model_name,
            base_url=self.ollama_base_url,
        )
        self.llm = ChatOllama(
            model=self.chat_model_name,
            base_url=self.ollama_base_url,
            temperature=0,
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
Você é um especialista em análise de regulamentos financeiros.

Responda usando APENAS o contexto fornecido.
Se a resposta não estiver no contexto, diga claramente que não encontrou a informação no documento.
Sempre que possível, cite fonte e página.
Não invente números, cláusulas, taxas ou regras.

Contexto:
{context}
"""),
            ("human", "{question}"),
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()
        self.vector_store = self._preparar_vector_store()

    def _preparar_vector_store(self) -> Chroma:
        if self.recriar_indice and self.persist_directory.exists():
            shutil.rmtree(self.persist_directory)

        vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory),
        )

        try:
            quantidade = vector_store._collection.count()
        except Exception:
            quantidade = 0

        if quantidade == 0:
            if not self.pdf_path.exists():
                raise FileNotFoundError(f"PDF não encontrado: {self.pdf_path}")
            paginas = PyPDFLoader(str(self.pdf_path)).load()
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            chunks = splitter.split_documents(paginas)
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                persist_directory=str(self.persist_directory),
            )

        return vector_store

    @staticmethod
    def _pagina_humana(doc) -> Optional[int]:
        pagina = doc.metadata.get("page")
        if isinstance(pagina, int):
            return pagina + 1
        return None

    def _formatar_documentos(self, docs) -> str:
        partes = []
        for doc in docs:
            fonte = doc.metadata.get("source", "documento")
            pagina = self._pagina_humana(doc)
            partes.append(f"[Fonte: {fonte} | Página: {pagina}]\n{doc.page_content}")
        return "\n\n---\n\n".join(partes)

    def _fontes(self, docs) -> tuple[list[FonteConsulta], list[int]]:
        fontes: list[FonteConsulta] = []
        paginas: list[int] = []
        for doc in docs:
            pagina = self._pagina_humana(doc)
            if pagina is not None:
                paginas.append(pagina)
            fontes.append(FonteConsulta(
                documento=doc.metadata.get("source"),
                pagina=pagina,
                trecho=doc.page_content[:700],
            ))
        return fontes, sorted(set(paginas))

    @staticmethod
    def _inferir_confianca(docs) -> Literal["alta", "media", "baixa"]:
        if len(docs) >= 4:
            return "alta"
        if len(docs) >= 2:
            return "media"
        return "baixa"

    def buscar_trechos(self, pergunta: str, k: Optional[int] = None) -> dict:
        k_final = k or self.k
        docs = self.vector_store.similarity_search(pergunta, k=k_final)
        fontes, paginas = self._fontes(docs)
        return {
            "pergunta": pergunta,
            "k": k_final,
            "paginas_consultadas": paginas,
            "fontes": [fonte.model_dump() for fonte in fontes],
        }

    def consultar(self, pergunta: str, k: Optional[int] = None) -> dict:
        k_final = k or self.k
        docs = self.vector_store.similarity_search(pergunta, k=k_final)
        contexto = self._formatar_documentos(docs)
        resposta_texto = self.chain.invoke({"context": contexto, "question": pergunta})
        fontes, paginas = self._fontes(docs)
        resposta = RespostaRAGOllama(
            pergunta=pergunta,
            resposta=resposta_texto,
            fontes=fontes,
            paginas_consultadas=paginas,
            confianca=self._inferir_confianca(docs),
            observacao="Resposta gerada localmente com Ollama a partir dos trechos recuperados pelo RAG.",
        )
        return resposta.model_dump()
