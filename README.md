# CodeSage

> **AI-powered source code analysis platform** — Submit a GitHub repository, get actionable insights via a RAG (Retrieval-Augmented Generation) pipeline with streaming output.

CodeSage is a full-stack distributed system that clones repositories, parses code into semantic chunks, embeds them into a vector database, and answers natural language questions about the codebase using a local LLM.

---

## Architecture

```
┌──────────────┐     HTTP      ┌──────────────────┐     BullMQ     ┌─────────────────┐
│   Frontend   │ ───────────── │   Backend API    │ ──────────── │  Worker Service  │
│  React+Vite  │               │ Node.js+Express  │    (Redis)    │    Node.js       │
└──────┬───────┘               └────────┬─────────┘               └────────┬─────────┘
       │                                │                                  │
       │ SSE stream                     │ MongoDB                         │ HTTP/Stream
       │                                │                                  │
       │                          ┌─────┴──────┐                   ┌──────┴──────────┐
       │                          │  MongoDB   │                   │   AI Service    │
       │                          │            │                   │ FastAPI+Python  │
       │                          └────────────┘                   └──────┬──────────┘
       │                                                                  │
       │                                                           ┌──────┴──────────┐
       │                                                           │  RAG Pipeline   │
       │                                                           │                 │
       │                                                           │ Clone → Parse → │
       │                                                           │ Embed → Store → │
       │                                                           │ Retrieve → LLM  │
       │                                                           └──────┬──────────┘
       │                                                                  │
       │                                                    ┌─────────────┼────────────┐
       │                                                    │             │            │
       │                                              ┌─────┴───┐  ┌─────┴───┐  ┌─────┴────┐
       │                                              │  Redis  │  │ Qdrant  │  │ Local    │
       │                                              │ (Queue/ │  │ (Vector │  │ LLM      │
       │                                              │  Cache) │  │   DB)   │  │ (Mistral)│
       │                                              └─────────┘  └─────────┘  └──────────┘
```

### Service Overview

| Service | Tech Stack | Port | Description |
|---------|-----------|------|-------------|
| **Frontend** | React 19, Vite 8, React Router 7 | 5173 | Dashboard, auth, analysis viewer |
| **Backend API** | Express 5, Mongoose 9, BullMQ | 5000 | REST API, auth, job orchestration |
| **AI Service** | FastAPI, Celery, sentence-transformers, Qdrant | 8000 | RAG pipeline, code indexing, LLM queries |
| **Workers** | Node.js, BullMQ Worker | — | Async job processing |

### Data Stores

| Store | Purpose |
|-------|---------|
| **MongoDB** | Users, repositories, jobs, analysis results |
| **Redis** | BullMQ job queue, Celery broker, rate limiting, job state cache |
| **Qdrant** | Vector embeddings for semantic code search |

---

## Core Flow

```
User → Login → Add Repo → Click "Analyze"
  → Backend creates Job (pending) → Enqueues to BullMQ
    → Worker picks up job → Calls AI Service
      → AI Service runs RAG Pipeline:
        1. Clone repo (shallow, with timeout + size limits)
        2. Parse code with Tree-sitter (semantic chunks)
        3. Generate embeddings (BGE-base-en-v1.5)
        4. Store vectors in Qdrant
        5. Ready for queries → Retrieve context → LLM generates answer
      → Worker updates job status → Stores result
    → Backend streams output to Frontend via SSE
  → UI displays live analysis + persists result
```

---

## Project Structure

```
codeSage/
├── frontend/                    # React + Vite frontend
│   ├── src/
│   │   ├── api/                 # API layer (auth, repos)
│   │   ├── components/          # Navbar, Layout, ProtectedRoute
│   │   ├── context/             # AuthContext (user, theme, axios)
│   │   ├── hooks/               # useAuth hook
│   │   ├── pages/               # Dashboard, Login, Register, Analysis, etc.
│   │   ├── App.jsx              # Root component
│   │   └── app.routes.jsx       # React Router config
│   └── package.json
│
├── backend/                     # Node.js + Express API
│   ├── src/
│   │   ├── controllers/         # Auth, Repo, Job controllers
│   │   ├── models/              # Mongoose schemas (User, Repo, Job)
│   │   ├── routes/              # Express route definitions
│   │   ├── middlewares/         # JWT auth, input validation, correlation IDs
│   │   ├── queue/               # BullMQ queue + Redis connection
│   │   ├── db/                  # MongoDB connection
│   │   ├── utils/               # JWT token generation
│   │   └── app.js               # Express app setup
│   ├── server.js                # Entry point
│   └── package.json
│
├── ai-service/                  # Python FastAPI AI microservice
│   ├── app/
│   │   ├── api/                 # Health, indexing, query endpoints
│   │   ├── core/                # Config, logger, Redis utils, security
│   │   ├── llm/                 # LLM client + GGUF generator (Mistral 7B)
│   │   ├── rag/
│   │   │   ├── parser/          # Repo loader, Tree-sitter parser, chunker
│   │   │   ├── embeddings/      # Encoder, embedder, vector store, Qdrant adapter
│   │   │   └── pipeline/        # End-to-end RAG pipeline
│   │   ├── tasks/               # Celery background tasks (indexing)
│   │   ├── celery_app.py        # Celery configuration
│   │   └── main.py              # FastAPI entry point
│   ├── docker-compose.yml       # Redis + Qdrant + API + Worker
│   └── requirements.txt
│
├── workers/                     # Node.js BullMQ worker service
│   ├── src/
│   │   ├── jobs/                # Job handler (analyze.job.js)
│   │   ├── processors/          # Analysis processor (streams AI response)
│   │   ├── services/            # AI service HTTP client
│   │   └── utils/               # Structured logger
│   └── worker.js                # Worker entry point
│
├── .gitignore
├── project_plan.txt             # Detailed 15-day build plan
└── README.md                    # ← You are here
```

---

## API Reference

### Backend API (Port 5000)

#### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | — | Register with username, email, password |
| POST | `/api/auth/login` | — | Login, returns JWT cookies |
| POST | `/api/auth/refresh` | — | Rotate access + refresh tokens |
| POST | `/api/auth/logout` | JWT | Clear tokens, invalidate refresh |

#### Repositories
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/repos/create` | JWT | Add a repository |
| GET | `/api/repos` | JWT | List user's repositories |
| GET | `/api/repos/:repoId` | JWT | Get single repo details |
| DELETE | `/api/repos/:repoId` | JWT | Delete repository |
| POST | `/api/repos/:repoId/rerun` | JWT | Re-run analysis (placeholder) |

#### Jobs
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/jobs/analyze` | JWT | Enqueue analysis job |
| GET | `/api/jobs/:jobId` | JWT | Get job status |

#### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness check |

### AI Service API (Port 8000)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | — | Health check (Redis, Qdrant, LLM status) |
| POST | `/v1/index` | `X-API-Key` | Submit repo indexing job → Celery |
| GET | `/v1/index/{job_id}/status` | — | Poll indexing progress |
| DELETE | `/v1/index/{job_id}` | `X-API-Key` | Cancel indexing job |
| POST | `/v1/query` | `X-API-Key` | RAG query: retrieve + generate answer |

---

## RAG Pipeline

The AI service implements a production-grade RAG pipeline:

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Clone  │───▶│  Parse   │───▶│  Embed   │───▶│  Store   │───▶│  Query   │
│  Repo   │    │ (chunks) │    │ (vectors)│    │ (Qdrant) │    │  (LLM)   │
└─────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │              │               │               │               │
  GitPython     Tree-sitter    BGE-base-en      Qdrant         Mistral 7B
  shallow       semantic       v1.5             vector          GGUF Q4
  clone         chunking       768-dim          similarity      local
```

**Pipeline stages:**

1. **Clone** — Shallow clone via GitPython with timeout guards, size limits (100MB default), and private repo token support
2. **Parse** — Tree-sitter-based semantic extraction (functions, classes) with adaptive fallback chunking (60-line windows, 12-line overlap)
3. **Embed** — BGE-base-en-v1.5 sentence-transformer, 768-dimensional vectors, batch encoding
4. **Store** — Qdrant vector database with cosine similarity, collection-per-repo namespace
5. **Query** — Embed question → top-k retrieval → context assembly → Mistral 7B GGUF local inference

**Supported languages:** Python, JavaScript, TypeScript, Go, Java, Markdown

---

## Setup & Running

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **Docker** (for Redis + Qdrant)
- **MongoDB** (local or Atlas)

### 1. Clone the repository

```bash
git clone https://github.com/AkshatVerma087/codeSage.git
cd codeSage
```

### 2. Start infrastructure (Redis + Qdrant)

```bash
cd ai-service
docker-compose up redis qdrant -d
```

### 3. Backend API

```bash
cd backend
cp .env_example .env    # Configure MONGO_URI, REDIS_URL, JWT_SECRET
npm install
node server.js
```

### 4. AI Service

```bash
cd ai-service
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

In a separate terminal, start the Celery worker:

```bash
cd ai-service
.\venv\Scripts\activate  # or source venv/bin/activate
celery -A app.celery_app.celery_app worker -l info --pool=solo  # --pool=solo is Windows-only
```

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 6. Worker Service

```bash
cd workers
# Configure .env with MONGO_URI, REDIS_URL, AI_SERVICE_URL
node worker.js
```

---

## Environment Variables

### Backend (`.env`)
```
PORT=5000
MONGO_URI=mongodb://localhost:27017/codesage
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
```

### AI Service (`.env`)
```
SECRET_KEY=your-api-key
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
LLM_MODEL_PATH=./models/mistral-7b-instruct-v0.3.Q4_K_M.gguf
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Worker (`.env`)
```
MONGO_URI=mongodb://localhost:27017/codesage
REDIS_URL=redis://localhost:6379
AI_SERVICE_URL=http://localhost:8000
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Dual JWT tokens** | Short-lived access (15m) + long-lived refresh (7d) with rotation for security |
| **httpOnly cookies** | Prevents XSS token theft vs localStorage approach |
| **Idempotency keys** | Prevents duplicate job submissions on network retries |
| **Correlation IDs** | End-to-end distributed tracing across all services |
| **Local GGUF LLM** | Zero-cost inference, no API key dependencies, full data privacy |
| **Qdrant over ChromaDB** | Better async support, production-grade vector DB |
| **Celery for AI tasks** | Heavy indexing runs in background workers, not in FastAPI event loop |
| **Semantic chunking** | Tree-sitter function/class extraction > naive fixed-size splitting |
| **BullMQ + Redis** | Battle-tested job queue with retry, backoff, dead letter support |

---

## Implementation Status

### ✅ Complete

- [x] JWT auth system (register, login, refresh, logout, token rotation)
- [x] User, Repository, Job Mongoose models
- [x] Repository CRUD with ownership validation
- [x] BullMQ async job queue with idempotency
- [x] Correlation ID middleware (end-to-end tracing)
- [x] Worker service with job lifecycle management
- [x] FastAPI AI service with health checks, CORS, Redis
- [x] Full RAG pipeline (clone → parse → embed → store)
- [x] Tree-sitter semantic code parsing + adaptive chunker
- [x] BGE-base-en-v1.5 embedding encoder (768-dim)
- [x] Qdrant vector store integration with async support
- [x] Celery background indexing with progress tracking
- [x] RAG query endpoint (retrieve → LLM generate → return with sources)
- [x] Local Mistral 7B GGUF inference (llama-cpp-python)
- [x] API key auth + rate limiting on AI service
- [x] Repo locking to prevent concurrent indexing
- [x] Frontend: React app with routing, auth context, theme toggle
- [x] Frontend: Dashboard with repo list, search, add-repo form
- [x] Frontend: Analysis page mockup with streaming output UI
- [x] Frontend: Login, Register, About pages

### ⏳ In Progress / Needs Work

- [ ] **Login/Register forms** — UI built but form submission not fully wired
- [ ] **Dashboard "Add repo" button** — No onClick handler yet
- [ ] **Analysis page** — Hardcoded mockup, needs real data integration
- [ ] **Repo rerun endpoint** — Placeholder, doesn't enqueue actual jobs

### ❌ Not Yet Built

- [ ] SSE streaming endpoint (`GET /api/jobs/:jobId/stream`)
- [ ] `useStreaming` hook for frontend SSE consumption
- [ ] `StreamingOutput` component for live results
- [ ] `AnalysisResult` Mongoose model for persistent results
- [ ] Global error handler middleware (Express)
- [ ] Backend rate limiting
- [ ] Root `docker-compose.yml` for full-stack deployment
- [ ] Prometheus/Grafana observability
- [ ] Comprehensive test suite

---

## Testing the AI Service (Postman)

### Prerequisites
1. Redis + Qdrant running (`docker-compose up redis qdrant -d`)
2. FastAPI server running (`uvicorn app.main:app --port 8000`)
3. Celery worker running (`celery -A app.celery_app.celery_app worker -l info --pool=solo`)

### 1. Health Check
```
GET http://localhost:8000/health
```

### 2. Index a Repository
```
POST http://localhost:8000/v1/index
Header: X-API-Key: <your SECRET_KEY from .env>
Body: { "repo_url": "https://github.com/pallets/markupsafe", "repo_id": "markupsafe-test" }
```

### 3. Poll Job Status
```
GET http://localhost:8000/v1/index/{job_id}/status
```
Stages: `queued → cloning → parsing → encoding → upserting → completed`

### 4. Query the Codebase (requires LLM model)
```
POST http://localhost:8000/v1/query
Header: X-API-Key: <your SECRET_KEY from .env>
Body: { "repo_id": "markupsafe-test", "question": "How does the escape function work?", "top_k": 5 }
```

---

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite 8, React Router 7, Axios |
| Backend | Node.js, Express 5, Mongoose 9, BullMQ |
| AI Service | Python, FastAPI, Celery, sentence-transformers |
| LLM | Mistral 7B (GGUF Q4, llama-cpp-python) |
| Embeddings | BAAI/bge-base-en-v1.5 (768-dim) |
| Vector DB | Qdrant |
| Database | MongoDB |
| Queue | BullMQ + Redis |
| Auth | JWT (dual token), bcrypt |
| Deployment | Docker, docker-compose |

---

## License

ISC

---

*Built by [Akshat Verma](https://github.com/AkshatVerma087)*
