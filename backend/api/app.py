from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.middleware import MetricsMiddleware
from backend.api.routes import bugs, chat, create_pr, ingest, memory, metrics, patch, repository, review, run_tests
from backend.core.config import get_settings
from backend.core.logging import configure_logging, get_logger
from backend.db.engine import Base, engine

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("startup", app=settings.app_name, env=settings.environment)
    async with engine.begin() as conn:
        from backend.db import orm_models  # noqa: F401 — register models
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("shutdown")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    # Middleware — order matters: CORSMiddleware outermost, MetricsMiddleware innermost
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(MetricsMiddleware)

    app.include_router(ingest.router)
    app.include_router(chat.router)
    app.include_router(patch.router)
    app.include_router(bugs.router)
    app.include_router(metrics.router)
    app.include_router(repository.router)
    app.include_router(review.router)
    app.include_router(create_pr.router)
    app.include_router(run_tests.router)
    app.include_router(memory.router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
