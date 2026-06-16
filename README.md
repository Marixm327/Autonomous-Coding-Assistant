# AI Software Engineer

A production-quality autonomous coding assistant that understands, navigates, and modifies entire codebases. Comparable in architecture to Devin, Cursor Agent, and Claude Code — built with Python, FastAPI, LangGraph, and Qdrant.

---

## What it does

- **Ingests** any GitHub repository (or local folder) — clones, parses, chunks, and embeds the entire codebase
- **Answers** technical questions about code with cited sources (file + line number)
- **Finds bugs** — dead code, race conditions, null checks, security vulnerabilities
- **Generates patches** — writes production-quality code diffs in the repo's own style
- **Reviews code** — correctness, security, edge cases, style consistency against the existing codebase
- **Runs tests** — pytest, npm test, mvn test with structured pass/fail output
- **Opens Pull Requests** — full end-to-end: generate → test → push branch → open GitHub PR
- **Remembers** — per-repository conversation history and auto-learned coding conventions

---

## Architecture

```
User Request
    ↓
FastAPI Gateway  (18 REST endpoints)
    ↓
LangGraph Orchestrator
    ↓
┌─────────────┬──────────────┬─────────────┬──────────────┐
│   Planner   │   Research   │    Coding   │   Reviewer   │
│  (subtasks) │  (RAG + KG)  │  (patches)  │  (PASS/FAIL) │
└─────────────┴──────────────┴─────────────┴──────────────┘
    ↓                ↓
Tool Layer       RAG Pipeline
(git, tests,     (rewrite → hybrid search
 GitHub API,      → rerank → compress → cite)
 filesystem)
    ↓                ↓
PostgreSQL      Qdrant Vector DB
(metadata,      (embeddings,
 memory,         per-repo collections)
 metrics)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Agents | LangGraph |
| LLM | OpenAI GPT-4o |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | Qdrant |
| Relational DB | PostgreSQL (via SQLAlchemy async) |
| Parsing | Tree-sitter (Python, JS, TS + fallback) |
| Retrieval | Hybrid BM25 + Vector with reranking |
| Migrations | Alembic |
| Logging | structlog (JSON) |
| Observability | Prometheus + Grafana |
| Deployment | Docker + Docker Compose |

---

## Project Structure

```
ai-software-engineer/
├── .env                        # Your secrets (gitignored)
├── .env.example                # Template — copy to .env
├── .gitignore
├── README.md
├── CLAUDE.md                   # Developer onboarding guide
│
├── backend/
│   ├── requirements.txt
│   ├── pyproject.toml          # pytest + ruff + mypy config
│   │
│   ├── agents/                 # LangGraph multi-agent nodes
│   │   ├── orchestrator.py     # Graph assembly + conditional edges
│   │   ├── state.py            # Shared GraphState (Pydantic)
│   │   ├── planner/            # Breaks tasks into subtasks
│   │   ├── research/           # RAG-powered code retrieval
│   │   ├── coding/             # Patch and code generation
│   │   └── reviewer/           # PASS/FAIL code review
│   │
│   ├── api/                    # FastAPI application
│   │   ├── app.py              # App factory + lifespan + middleware
│   │   ├── deps.py             # Dependency injection (embedder, RAG, DB)
│   │   ├── middleware.py       # Request timing + metrics recording
│   │   └── routes/
│   │       ├── ingest.py       # POST /ingest
│   │       ├── chat.py         # POST /chat
│   │       ├── review.py       # POST /review
│   │       ├── patch.py        # POST /generate-patch
│   │       ├── bugs.py         # POST /bug-report
│   │       ├── create_pr.py    # POST /create-pr
│   │       ├── run_tests.py    # POST /run-tests
│   │       ├── repository.py   # GET/DELETE /repository-status
│   │       ├── memory.py       # GET/POST /memory/*
│   │       └── metrics.py      # GET /metrics + /metrics/prometheus
│   │
│   ├── core/                   # Shared infrastructure
│   │   ├── config.py           # Pydantic settings (reads .env)
│   │   ├── exceptions.py       # Custom exception hierarchy
│   │   └── logging.py          # structlog configuration
│   │
│   ├── db/                     # Database layer
│   │   ├── engine.py           # Async SQLAlchemy engine + session factory
│   │   ├── orm_models.py       # All ORM table definitions
│   │   └── migrations/         # Alembic migrations
│   │       └── versions/
│   │           ├── 0001_initial_schema.py
│   │           ├── 0002_memory_tables.py
│   │           └── 0003_metrics_tables.py
│   │
│   ├── evaluation/             # Offline quality measurement
│   │   └── recall.py           # Retrieval recall evaluator
│   │
│   ├── graph/                  # Knowledge graph
│   │   └── builder.py          # Extracts import/call/inheritance edges
│   │
│   ├── memory/                 # Per-repository memory
│   │   ├── store.py            # PostgreSQL-backed preferences + history
│   │   └── convention_learner.py  # Auto-extracts coding conventions
│   │
│   ├── models/                 # Pydantic domain models (not ORM)
│   │   ├── repository.py
│   │   ├── chunk.py
│   │   ├── agent.py
│   │   └── knowledge_graph.py
│   │
│   ├── rag/                    # Full RAG pipeline
│   │   ├── pipeline.py         # Orchestrates all RAG stages
│   │   ├── embedder.py         # OpenAI embeddings (abstract interface)
│   │   ├── retriever.py        # Hybrid BM25 + vector search
│   │   ├── reranker.py         # CrossEncoder + passthrough reranker
│   │   ├── query_rewriter.py   # Expands query into 3 variants
│   │   ├── compressor.py       # Token-budget context trimming
│   │   ├── citations.py        # [N] citation markers + CitedAnswer
│   │   └── vector_store.py     # Qdrant async client wrapper
│   │
│   ├── services/
│   │   ├── connectors/         # DataSource interface + implementations
│   │   │   ├── base.py         # Abstract DataSource + FetchedFile
│   │   │   ├── github.py       # GitHub clone connector
│   │   │   ├── local.py        # Local folder connector
│   │   │   └── registry.py     # URL → connector resolver
│   │   │
│   │   ├── ingestion/
│   │   │   └── pipeline.py     # fetch → parse → embed → store → graph
│   │   │
│   │   ├── metrics/
│   │   │   ├── collector.py    # Write-side: record events
│   │   │   └── queries.py      # Read-side: aggregations + breakdowns
│   │   │
│   │   ├── parsing/            # Tree-sitter parsers
│   │   │   ├── base.py         # Abstract BaseParser
│   │   │   ├── dispatcher.py   # Routes files to correct parser
│   │   │   ├── python_parser.py
│   │   │   ├── javascript_parser.py  # JS + TS + TSX
│   │   │   └── text_fallback_parser.py  # Sliding-window for everything else
│   │   │
│   │   ├── pr/                 # Pull request workflow
│   │   │   ├── workflow.py     # End-to-end: plan→code→test→push→PR
│   │   │   └── patch_applier.py  # Parses + applies <file> blocks
│   │   │
│   │   └── repository/
│   │       └── service.py      # PostgreSQL CRUD for all entities
│   │
│   ├── tools/                  # Standalone callable tools
│   │   ├── file_tools.py       # read_file, write_file, list_directory
│   │   ├── git_tools.py        # git_diff, git_apply_patch
│   │   ├── github_tools.py     # create_pull_request (GitHub API)
│   │   ├── search_tools.py     # search_repo, grep
│   │   ├── terminal_tools.py   # execute_terminal (allowlisted)
│   │   └── test_tools.py       # run_tests (pytest/npm/mvn)
│   │
│   └── tests/
│       ├── unit/               # Fast tests, no infrastructure
│       │   ├── test_parsing.py
│       │   ├── test_js_parser.py
│       │   ├── test_connectors.py
│       │   ├── test_rag.py
│       │   ├── test_memory.py
│       │   ├── test_patch_applier.py
│       │   └── test_metrics.py
│       └── integration/        # Requires live Postgres + Qdrant
│           └── test_ingestion_pipeline.py
│
└── docker/
    ├── Dockerfile
    ├── docker-compose.yml      # api + qdrant + postgres + prometheus + grafana
    ├── prometheus.yml          # Scrape config for /metrics/prometheus
    └── grafana/
        └── provisioning/
            └── datasources/
                └── prometheus.yml
```

---

## Quick Start

### Prerequisites
- Python 3.12+
- Docker Desktop
- Git

### 1. Clone and set up environment

```bash
git clone https://github.com/your-username/ai-software-engineer
cd ai-software-engineer

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r backend/requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your keys:
#   OPENAI_API_KEY=sk-proj-...
#   GITHUB_TOKEN=ghp_...
```

### 3. Start infrastructure

```bash
docker compose -f docker/docker-compose.yml up qdrant postgres -d
```

### 4. Run the API

```bash
# Windows (PowerShell):
$env:PYTHONPATH = (Get-Location).Path
uvicorn backend.api.app:app --reload

# macOS/Linux:
PYTHONPATH=. uvicorn backend.api.app:app --reload
```

API is live at **http://localhost:8000**
Interactive docs at **http://localhost:8000/docs**

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ingest` | Ingest a GitHub repo or local folder |
| GET | `/repository-status` | List all repositories |
| GET | `/repository-status/{id}` | Get ingestion status + language stats |
| DELETE | `/repository-status/{id}` | Delete repo from DB and Qdrant |
| POST | `/chat` | Ask a technical question about a repo |
| POST | `/review` | Review a code patch against repo patterns |
| POST | `/generate-patch` | Generate a code patch for a described change |
| POST | `/bug-report` | Run automated bug scan |
| POST | `/create-pr` | Full PR workflow: code → test → push → PR |
| POST | `/run-tests` | Run the repo's test suite |
| GET | `/memory/{id}/preferences` | Read learned coding conventions |
| POST | `/memory/{id}/preferences` | Set a convention manually |
| POST | `/memory/{id}/learn-conventions` | Trigger auto convention learning |
| GET | `/memory/{id}/history` | Conversation history |
| DELETE | `/memory/{id}/history` | Clear history |
| GET | `/metrics` | System metrics (JSON) |
| GET | `/metrics/prometheus` | Prometheus scrape endpoint |
| GET | `/health` | Liveness probe |

---

## Example Usage

### Ingest a repository
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"source": "https://github.com/tiangolo/fastapi"}'
```

### Chat with the codebase
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": "your-repo-id-here",
    "message": "How does dependency injection work in this codebase?"
  }'
```

### Generate and open a Pull Request
```bash
curl -X POST http://localhost:8000/create-pr \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": "your-repo-id-here",
    "issue_description": "Add rate limiting to the /login endpoint",
    "open_pr": true
  }'
```

---

## Running Tests

```bash
# Unit tests only (no Docker needed)
cd backend
pytest tests/unit -v

# All tests (requires running Postgres + Qdrant)
pytest -v
```

---

## Observability

| Service | URL | Credentials |
|---|---|---|
| API Docs | http://localhost:8000/docs | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / admin |

Start the full observability stack:
```bash
docker compose -f docker/docker-compose.yml up -d
```

---

## Extending the System

| What to add | Interface to implement | Location |
|---|---|---|
| New code source (GitLab, S3) | `DataSource` | `services/connectors/base.py` |
| New language parser | `BaseParser` | `services/parsing/base.py` |
| Different embedding model | `Embedder` | `rag/embedder.py` |
| Different vector database | `VectorStore` | `rag/vector_store.py` |
| Different reranker | `Reranker` | `rag/reranker.py` |

All interfaces are abstract — swap implementations without touching business logic.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | ✅ | — | OpenAI API key |
| `OPENAI_CHAT_MODEL` | No | `gpt-4o` | LLM model for agents |
| `OPENAI_EMBEDDING_MODEL` | No | `text-embedding-3-small` | Embedding model |
| `GITHUB_TOKEN` | For PRs | — | GitHub personal access token (`repo` scope) |
| `QDRANT_HOST` | No | `localhost` | Qdrant host |
| `QDRANT_PORT` | No | `6333` | Qdrant port |
| `POSTGRES_DSN` | No | local default | Async PostgreSQL connection string |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING` |
| `ENVIRONMENT` | No | `development` | `development`, `staging`, `production` |

---

## License

MIT
