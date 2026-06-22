"""FastAPI dependency injection."""
from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.orchestrator import build_graph
from backend.db.engine import get_session
from backend.memory.store import MemoryStore  # stateless — session passed per call
from backend.rag.compressor import ContextCompressor
from backend.rag.embedder import OpenAIEmbedder
from backend.rag.pipeline import RAGPipeline
from backend.rag.query_rewriter import QueryRewriter
from backend.rag.reranker import PassthroughReranker
from backend.rag.retriever import HybridRetriever
from backend.rag.vector_store import QdrantVectorStore
from backend.services.ingestion.pipeline import IngestionPipeline
from backend.services.repository.service import RepositoryService


@lru_cache
def get_embedder() -> OpenAIEmbedder:
    return OpenAIEmbedder()


@lru_cache
def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore()


@lru_cache
def get_retriever() -> HybridRetriever:
    return HybridRetriever(get_embedder(), get_vector_store())


def get_memory_store() -> MemoryStore:
    # Stateless object — DB session is passed into each method at call time
    return MemoryStore()


@lru_cache
def get_ingestion_pipeline() -> IngestionPipeline:
    return IngestionPipeline(get_embedder(), get_vector_store())


@lru_cache
def get_rag_pipeline() -> RAGPipeline:
    return RAGPipeline(
        retriever=get_retriever(),
        reranker=PassthroughReranker(),
        rewriter=QueryRewriter(),
        compressor=ContextCompressor(),
    )


def get_agent_graph():
    return build_graph(get_rag_pipeline())


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


async def get_repo_service(session: AsyncSession = None) -> RepositoryService:
    # Used directly in routes via Depends(get_db_session)
    return RepositoryService(session)
