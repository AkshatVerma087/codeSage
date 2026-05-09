<p align="center">
  <h1 align="center">🧠 CodeSage</h1>
  <p align="center">
    <strong>AI-Powered Source Code Analysis Platform</strong>
  </p>
  <p align="center">
    Submit a GitHub repo → Get intelligent code insights powered by RAG + Local LLM
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react" alt="React" />
  <img src="https://img.shields.io/badge/Node.js-Express_5-339933?logo=node.js" alt="Node.js" />
  <img src="https://img.shields.io/badge/Python-FastAPI-009688?logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/LLM-Mistral_7B-FF6F00" alt="Mistral" />
  <img src="https://img.shields.io/badge/Vector_DB-Qdrant-DC382D" alt="Qdrant" />
  <img src="https://img.shields.io/badge/Queue-BullMQ-D92D2A" alt="BullMQ" />
</p>

---

## What is CodeSage?

CodeSage is a **distributed microservices platform** that analyzes source code repositories using a RAG (Retrieval-Augmented Generation) pipeline. It clones repositories, parses code into semantic chunks using Tree-sitter, generates vector embeddings, stores them in Qdrant, and answers natural language questions about the codebase using a locally-running Mistral 7B LLM.

**Key highlights:**
- 🔒 **Zero API costs** — runs Mistral 7B locally via GGUF, no OpenAI keys needed
- 🧩 **Semantic code parsing** — Tree-sitter extracts functions, classes, not just text blocks
- ⚡ **Async job pipeline** — BullMQ + Celery for non-blocking analysis
- 🔍 **RAG with sources** — every answer includes file paths, line numbers, and similarity scores
- 🔐 **Production auth** — JWT dual-token with httpOnly cookies, refresh rotation
- 📊 **Observability** — correlation IDs traced across all 4 services

---

## Architecture

```mermaid
graph TB
    subgraph Client
        FE["🖥️ Frontend<br/>React 19 + Vite"]
    end

    subgraph Backend
        API["⚙️ Backend API<br/>Express 5"]
        MONGO[("🗄️ MongoDB")]
        QUEUE["📬 BullMQ Queue"]
    end

    subgraph Workers
        W["🔧 Worker Service<br/>Node.js"]
    end

    subgraph AI["AI Service"]
        FAST["🐍 FastAPI"]
        CELERY["🌿 Celery Worker"]
        RAG["🧠 RAG Pipeline"]
    end

    subgraph Storage
        REDIS[("🔴 Redis")]
        QDRANT[("📐 Qdrant<br/>Vector DB")]
        LLM["🤖 Mistral 7B<br/>GGUF Local"]
    end

    FE -->|"HTTP + Cookies"| API
    API --> MONGO
    API -->|"Enqueue Job"| QUEUE
    QUEUE -->|"Redis"| REDIS
    W -->|"Consume Jobs"| QUEUE
    W -->|"HTTP"| FAST
    FAST -->|"Dispatch"| CELERY
    CELERY --> RAG
    RAG -->|"Store Vectors"| QDRANT
    RAG -->|"Generate Answer"| LLM
    FAST -->|"Job State"| REDIS
    W --> MONGO

    style FE fill:#61DAFB,color:#000
    style API fill:#339933,color:#fff
    style FAST fill:#009688,color:#fff
    style RAG fill:#FF6F00,color:#fff
    style LLM fill:#7C3AED,color:#fff
    style REDIS fill:#DC382D,color:#fff
    style QDRANT fill:#24B47E,color:#fff
    style MONGO fill:#47A248,color:#fff
```

### Services at a Glance

| Service | Stack | Port | Responsibility |
|---------|-------|------|---------------|
| **Frontend** | React 19, Vite 8, React Router 7, Axios | `5173` | User interface — auth, repo management, analysis viewer |
| **Backend API** | Express 5, Mongoose 9, BullMQ, JWT | `5000` | REST API — authentication, CRUD, job orchestration |
| **AI Service** | FastAPI, Celery, sentence-transformers, Qdrant | `8000` | RAG pipeline — code parsing, embedding, vector search, LLM |
| **Workers** | Node.js, BullMQ Worker, Axios | — | Async job consumer — bridges backend to AI service |

---

## RAG Pipeline

The core intelligence of CodeSage — how it turns raw code into searchable knowledge:

```mermaid
graph LR
    A["📥 Clone Repo<br/><small>GitPython, shallow</small>"] --> B["🔍 Parse Code<br/><small>Tree-sitter, semantic</small>"]
    B --> C["🧮 Embed Chunks<br/><small>BGE-base-en-v1.5</small>"]
    C --> D["💾 Store Vectors<br/><small>Qdrant, cosine</small>"]
    D --> E["❓ Query<br/><small>Top-k retrieval</small>"]
    E --> F["🤖 Generate Answer<br/><small>Mistral 7B GGUF</small>"]

    style A fill:#6366f1,color:#fff
    style B fill:#8b5cf6,color:#fff
    style C fill:#a78bfa,color:#fff
    style D fill:#c4b5fd,color:#000
    style E fill:#f59e0b,color:#000
    style F fill:#10b981,color:#fff
```

| Stage | Technology | Details |
|-------|-----------|---------|
| **Clone** | GitPython | Shallow clone (`depth=1`), token auth for private repos, 100MB size limit, timeout enforcement |
| **Parse** | Tree-sitter + regex chunker | Semantic extraction of functions/classes, 60-line windows with 12-line overlap, supports `.py`, `.js`, `.ts`, `.go`, `.java` |
| **Embed** | `BAAI/bge-base-en-v1.5` | 768-dimensional vectors, batch encoding, L2-normalized, code-specific prefix prompts |
| **Store** | Qdrant | Cosine similarity, collection-per-repo, UUID5 point IDs, rich payload (file path, line numbers, symbol name) |
| **Query** | Vector search + LLM | Top-k retrieval → context assembly → Mistral 7B generates answer with file citations |

---

## API Reference

### Backend API (`localhost:5000`)

<details>
<summary><strong>🔐 Authentication</strong></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | — | Register with username, email, password |
| `POST` | `/api/auth/login` | — | Login → sets httpOnly JWT cookies |
| `POST` | `/api/auth/refresh` | — | Rotate access + refresh tokens |
| `POST` | `/api/auth/logout` | JWT | Clear cookies, invalidate refresh token |

</details>

<details>
<summary><strong>📁 Repositories</strong></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/repos/create` | JWT | Add a repository (URL, provider, visibility) |
| `GET` | `/api/repos` | JWT | List user's repositories |
| `GET` | `/api/repos/:repoId` | JWT | Get single repository details |
| `DELETE` | `/api/repos/:repoId` | JWT | Delete repository (ownership check) |
| `POST` | `/api/repos/:repoId/rerun` | JWT | Re-run analysis (placeholder) |

</details>

<details>
<summary><strong>📊 Jobs</strong></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/jobs/analyze` | JWT | Enqueue analysis job (idempotency supported) |
| `GET` | `/api/jobs/:jobId` | JWT | Get job status + details |

</details>

### AI Service API (`localhost:8000`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | — | Health check (Redis, Qdrant, LLM model status) |
| `POST` | `/v1/index` | `X-API-Key` | Submit repo for indexing → Celery background task |
| `GET` | `/v1/index/{job_id}/status` | — | Poll indexing progress (stage + percentage) |
| `DELETE` | `/v1/index/{job_id}` | `X-API-Key` | Cancel an indexing job |
| `POST` | `/v1/query` | `X-API-Key` | Ask a question about indexed code (RAG) |

---

## Project Structure

```
codeSage/
├── frontend/                          # React + Vite SPA
│   └── src/
│       ├── api/                       # auth.api.js, repos.api.js
│       ├── components/                # Navbar, Layout, ProtectedRoute
│       ├── context/                   # AuthContext (user state, axios, theme)
│       ├── hooks/                     # useAuth (login/register/logout)
│       ├── pages/                     # Dashboard, Login, Register, Analysis, etc.
│       ├── App.jsx                    # Root with AuthProvider + Router
│       └── app.routes.jsx             # Route definitions
│
├── backend/                           # Express API server
│   └── src/
│       ├── controllers/               # auth, repo, job controllers
│       ├── models/                    # User, Repo, Job Mongoose schemas
│       ├── middlewares/               # JWT auth, correlation IDs, validation
│       ├── routes/                    # Route registrations
│       ├── queue/                     # BullMQ queue + Redis connection
│       └── app.js                     # Express app configuration
│
├── ai-service/                        # FastAPI AI microservice
│   └── app/
│       ├── api/                       # health, indexing, query endpoints
│       ├── core/                      # config, logger, redis utils, security
│       ├── llm/                       # LLM generator + client (Mistral 7B)
│       ├── rag/
│       │   ├── parser/                # repo_loader, tree_sitter, chunker
│       │   ├── embeddings/            # encoder, embedder, vector_store, qdrant
│       │   └── pipeline/              # End-to-end RAG orchestrator
│       ├── tasks/                     # Celery background indexing task
│       └── main.py                    # FastAPI entry point
│
├── workers/                           # BullMQ job consumer
│   └── src/
│       ├── jobs/                      # analyze.job.js (job handler)
│       ├── processors/                # analysis.processor.js
│       ├── services/                  # aiClient.js (HTTP to AI service)
│       └── utils/                     # Structured logger
│
└── README.md
```

---

## Detailed File-by-File Reference

### Backend API Service — `backend/`

<details>
<summary><strong>📌 Entry Points</strong></summary>

| File | Description |
|------|-------------|
| `server.js` | Loads environment, connects to MongoDB via Mongoose, starts Express on `PORT` (default 5000) |
| `src/app.js` | Express app configuration — CORS, JSON body parsing, cookie-parser, correlation ID middleware, mounts all route groups under `/api/auth`, `/api/repos`, `/api/jobs` |

</details>

<details>
<summary><strong>📦 Models</strong> — <code>src/models/</code></summary>

| File | Schema | Key Fields |
|------|--------|------------|
| `auth.model.js` | **User** | `username`, `email`, `password` (bcrypt hashed), `refreshToken`, timestamps |
| `repo.model.js` | **Repository** | `ownerUserId` (ref → User), `provider` (github/gitlab), `url`, `defaultBranch`, `visibilityHint` (public/private), `credentialRef`, timestamps |
| `job.model.js` | **Job** | `ownerUserId`, `repoId` (ref → Repo), `type` (analysis), `status` (pending → running → success → failed), `attempts`, `queueJobId`, `correlationId`, `idempotencyKey`, `errorMessage`, `errorCode`, timestamps |

</details>

<details>
<summary><strong>🎮 Controllers</strong> — <code>src/controllers/</code></summary>

| File | Endpoints | What It Does |
|------|-----------|-------------|
| `auth.controller.js` | `register`, `login`, `refresh`, `logout` | Hashes passwords with bcrypt. Generates dual JWT tokens: short-lived access token (15min) + long-lived refresh token (7 days). Stores tokens in httpOnly secure cookies. Supports token rotation on refresh. Nullifies refresh token on logout. |
| `repo.controller.js` | `create`, `list`, `getById`, `delete`, `rerun` | Full CRUD with ownership validation (checks `ownerUserId` matches JWT user). Input validation for required fields. Duplicate URL checking. Delete cascade. `rerun` is currently a placeholder. |
| `job.controller.js` | `triggerAnalysis`, `getStatus` | Creates a Job document in MongoDB with status `pending`, then enqueues an `analysis` job into BullMQ/Redis. Supports `idempotencyKey` to prevent duplicate submissions. Returns queueJobId for tracking. |

</details>

<details>
<summary><strong>🛡️ Middlewares & Queue</strong> — <code>src/middlewares/</code>, <code>src/queue/</code></summary>

| File | What It Does |
|------|-------------|
| `auth.middleware.js` | **JWT verification** — extracts token from httpOnly cookies or `Authorization: Bearer` header. Verifies with `jsonwebtoken`. Attaches `req.user`. Also contains **input validation** for register/login payloads. |
| `correlation.middleware.js` | **Distributed tracing** — generates UUID `X-Correlation-Id` per request. Attaches to `req.correlationId` and response header. |
| `queue/connection.js` | IORedis connection from `REDIS_URL`. Shared by Queue and Worker. |
| `queue/analysisQueue.js` | BullMQ `Queue` named `"analysis"`. Used by `job.controller.js` to enqueue jobs. |

</details>

### Frontend Application — `frontend/`

<details>
<summary><strong>📌 Entry Points & State</strong></summary>

| File | Description |
|------|-------------|
| `src/main.jsx` | React root render — mounts `<App />` into DOM |
| `src/App.jsx` | Wraps app in `AuthProvider` context + `RouterProvider` for React Router |
| `src/app.routes.jsx` | Route definitions — Login, Register, Dashboard, Analysis, ResultPage, About, RepoPage |
| `src/context/AuthContext.jsx` | **Central state manager** — provides `user`, `axiosInstance` (baseURL: localhost:5000, withCredentials: true), `darkMode` toggle |
| `src/hooks/useAuth.js` | Custom hook: `login()`, `register()`, `logout()` — wraps API calls + updates context |

</details>

<details>
<summary><strong>🧱 Components</strong> — <code>src/components/</code></summary>

| File | What It Does |
|------|-------------|
| `Navbar.jsx` | Navigation bar with Dashboard/Analysis/About links, auth-aware buttons, theme toggle |
| `Layout.jsx` | Page wrapper — `<Navbar />` + `<Outlet>` |
| `ProtectedRoute.jsx` | Route guard — redirects to `/login` if unauthenticated, has `devMode` bypass |

</details>

<details>
<summary><strong>📄 Pages</strong> — <code>src/pages/</code></summary>

| File | What It Does |
|------|-------------|
| `Dashboard.jsx` | **Main hub** — fetches repos, stat cards, search/filter, "Add Repository" form, repo cards with View/Rerun/Delete. Falls back to sample data. |
| `Login.jsx` | Login form with glassmorphism styling. **Note:** inputs currently uncontrolled. |
| `Register.jsx` | Registration form with username, email, password, confirm password + validation |
| `Analysis.jsx` | **Full mockup** — sidebar with repo stats, query textarea, streaming output, code citations, analysis history. **All hardcoded demo data.** |
| `ResultPage.jsx` | Displays analysis results with formatted output |
| `RepoPage.jsx` | Single repo detail page (placeholder) |
| `About.jsx` | Platform description, features, tech stack |

</details>

### AI Service — `ai-service/`

<details>
<summary><strong>📌 Entry Points</strong></summary>

| File | Description |
|------|-------------|
| `app/main.py` | FastAPI app — Redis async client in lifespan, CORS, registers `health`, `indexing`, `query` routers |
| `app/celery_app.py` | Celery config — Redis broker + result backend, JSON serialization, 1-hour timeout, late ack, auto-discovers `app/tasks/` |

</details>

<details>
<summary><strong>🌐 API Endpoints</strong> — <code>app/api/</code></summary>

| File | Endpoints | What It Does |
|------|-----------|-------------|
| `health.py` | `GET /health` | Redis ping, Qdrant status, LLM model existence, timestamp |
| `indexing.py` | `POST /v1/index`, `GET /v1/index/{job_id}/status`, `DELETE /v1/index/{job_id}` | Submit indexing (acquires repo lock → Celery task), poll progress, cancel job. API key + rate limited. |
| `query.py` | `POST /v1/query` | RAG query: embed question → Qdrant top-k search → LLM generates answer. Returns answer + sources + latency. |
| `routes.py` | `POST /analyze`, `POST /generate` | Legacy endpoints (not registered). Synchronous indexing + direct LLM generation. |

</details>

<details>
<summary><strong>⚙️ Core</strong> — <code>app/core/</code></summary>

| File | What It Does |
|------|-------------|
| `config.py` | Pydantic `BaseSettings` — Redis, Qdrant, embeddings, LLM, security, repo constraints config from `.env` |
| `logger.py` | Structured JSON logging — `{timestamp, service, level, message, correlation_id, job_id}` |
| `redis_utils.py` | Async helpers: `set_job_state()`, `get_job_state()`, `set_job_progress()`, `cache_json()`, `acquire_repo_lock()`, `release_repo_lock()` |
| `security.py` | API key verification (constant-time), rate limiting (Redis INCR), repo locking (SET NX), cache utils |

</details>

<details>
<summary><strong>🔍 RAG Parser</strong> — <code>app/rag/parser/</code></summary>

| File | What It Does |
|------|-------------|
| `repo_loader.py` | **RepoLoader** — GitPython shallow clone, token auth for private repos, timeout + size limits (100MB), cleanup |
| `tree_sitter_parser.py` | **TreeSitterParser** — walks directory, filters `.py/.js/.ts/.go/.java`, skips hidden/node_modules/venv, delegates to Chunker |
| `chunker.py` | **Chunker** — regex boundary detection for functions/classes across 5 languages, 60-line windows with 12-line overlap, produces `ChunkWindow` dataclasses |
| `parser.py` | Base parser interface |

</details>

<details>
<summary><strong>📐 RAG Embeddings</strong> — <code>app/rag/embeddings/</code></summary>

| File | What It Does |
|------|-------------|
| `encoder.py` | **Encoder** (singleton) — loads `BAAI/bge-base-en-v1.5`, 768-dim vectors, batch encode with normalization, code/query prefix prompts |
| `embedder.py` | **Embedder** — wrapper with `encode()`, `encode_chunks()`, `similarity()`, exposes `embedding_dim` |
| `vector_store.py` | **VectorStore** — async/sync Qdrant interface. Sync methods use `_run_sync()` for nested event loop safety |
| `qdrant_adapter.py` | **QdrantAdapter** — creates collections (cosine distance), UUID5 point IDs, rich payload storage, configurable top-k search |

</details>

<details>
<summary><strong>🤖 LLM & Tasks</strong> — <code>app/llm/</code>, <code>app/tasks/</code></summary>

| File | What It Does |
|------|-------------|
| `llm/generator.py` | **LLMGenerator** (singleton) — lazy-loads GGUF model via `llama-cpp-python`, builds context-aware prompts, chat completion with fallback |
| `llm/client.py` | **LLMClient** — validates backend selection (`local`/`llama-cpp`/`gguf`), delegates to generator |
| `tasks/indexing.py` | **Celery task** — full indexing pipeline with progress: cloning(5%) → parsing(20%) → encoding(50%) → upserting(80-99%) → completed(100%). Failure handling + repo lock release |
| `rag/pipeline/pipeline.py` | **RAGPipeline** — orchestrates clone → parse → embed → upsert, returns stats, handles cleanup |

</details>

### Worker Service — `workers/`

<details>
<summary><strong>📋 All Files</strong></summary>

| File | What It Does |
|------|-------------|
| `worker.js` | Entry point — connects MongoDB, BullMQ Worker on `"analysis"` queue |
| `src/jobs/analyze.job.js` | Job handler — marks Job as `running`, calls processor, marks `success`/`failed` |
| `src/processors/analysis.processor.js` | Calls `aiClient.analyze()`, streams response, returns results |
| `src/services/aiClient.js` | Axios client to AI service `/analyze` endpoint with correlation ID |
| `src/queue/connection.js` | IORedis connection for BullMQ |
| `src/models/job.model.js` | Shared Job Mongoose schema |
| `src/utils/logger.js` | Structured logger with correlation ID |

</details>

---

## Data Flow Diagrams

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as MongoDB

    U->>F: Enter email + password
    F->>B: POST /api/auth/login
    B->>DB: Find user by email
    DB-->>B: User document
    B->>B: bcrypt.compare(password, hash)
    B->>B: Sign JWT access (15m) + refresh (7d)
    B->>DB: Store refreshToken
    B-->>F: Set httpOnly cookies
    F-->>U: Redirect to Dashboard
```

### Job Analysis Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend API
    participant Q as BullMQ/Redis
    participant W as Worker
    participant AI as AI Service
    participant C as Celery
    participant QD as Qdrant

    U->>F: Click Analyze
    F->>B: POST /api/jobs/analyze
    B->>B: Create Job status pending
    B->>Q: Enqueue analysis job
    B-->>F: 201 jobId

    Q->>W: Worker picks up job
    W->>W: Mark Job as running
    W->>AI: POST /v1/index
    AI->>AI: Acquire repo lock
    AI->>C: Dispatch Celery task

    C->>C: Clone repo
    C->>C: Parse code
    C->>C: Generate embeddings
    C->>QD: Upsert vectors
    C->>AI: Task complete

    AI-->>W: 202 job_id status
    W->>W: Mark Job as success
```

### RAG Query Flow

```mermaid
sequenceDiagram
    participant U as User
    participant AI as AI Service
    participant E as Embedder
    participant QD as Qdrant
    participant LLM as Local LLM

    U->>AI: POST /v1/query
    AI->>E: Encode question
    E-->>AI: Query vector 768-dim
    AI->>QD: Search top-k similar chunks
    QD-->>AI: Scored code chunks
    AI->>AI: Assemble context from chunks
    AI->>LLM: Generate answer
    LLM-->>AI: Generated text
    AI-->>U: answer + sources + latency
```

### Indexing Progress Stages

```mermaid
graph LR
    A["queued 0%"] --> B["cloning 5%"]
    B --> C["parsing 20%"]
    C --> D["encoding 50%"]
    D --> E["upserting 80-99%"]
    E --> F["completed 100%"]

    style A fill:#6366f1,color:#fff
    style B fill:#8b5cf6,color:#fff
    style C fill:#a78bfa,color:#fff
    style D fill:#c4b5fd,color:#000
    style E fill:#ddd6fe,color:#000
    style F fill:#10b981,color:#fff
```

---

## Quick Start

### Prerequisites

- **Node.js** ≥ 18, **Python** ≥ 3.10, **Docker**
- **MongoDB** (local or [Atlas](https://cloud.mongodb.com/))

### 1. Infrastructure (Redis + Qdrant)

```bash
cd ai-service
docker-compose up redis qdrant -d
```

### 2. Backend API

```bash
cd backend
cp .env_example .env   # Set MONGO_URI, REDIS_URL, JWT_SECRET
npm install && node server.js
```

### 3. AI Service + Celery Worker

```bash
cd ai-service
python -m venv venv && .\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload

# In a separate terminal:
celery -A app.celery_app.celery_app worker -l info --pool=solo
```

### 4. Frontend

```bash
cd frontend
npm install && npm run dev
```

### 5. Worker Service

```bash
cd workers
node worker.js
```

---

## Environment Variables

<details>
<summary><strong>Backend</strong> <code>.env</code></summary>

```env
PORT=5000
MONGO_URI=mongodb://localhost:27017/codesage
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
```
</details>

<details>
<summary><strong>AI Service</strong> <code>.env</code></summary>

```env
SECRET_KEY=your-api-key-here
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
LLM_MODEL_PATH=./models/mistral-7b-instruct-v0.3.Q4_K_M.gguf
LLM_N_CTX=4096
LLM_N_GPU_LAYERS=0
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```
</details>

<details>
<summary><strong>Workers</strong> <code>.env</code></summary>

```env
MONGO_URI=mongodb://localhost:27017/codesage
REDIS_URL=redis://localhost:6379
AI_SERVICE_URL=http://localhost:8000
```
</details>

---

## Testing the AI Service

Verified working flow in Postman:

```bash
# 1. Health check
GET http://localhost:8000/health

# 2. Index a repository
POST http://localhost:8000/v1/index
Headers: X-API-Key: <SECRET_KEY>, Content-Type: application/json
Body: {"repo_url": "https://github.com/pallets/markupsafe", "repo_id": "markupsafe-test"}

# 3. Poll status (use job_id from step 2)
GET http://localhost:8000/v1/index/{job_id}/status
# Stages: queued → cloning → parsing → encoding → upserting → completed

# 4. Query the code (requires GGUF model)
POST http://localhost:8000/v1/query
Headers: X-API-Key: <SECRET_KEY>, Content-Type: application/json
Body: {"repo_id": "markupsafe-test", "question": "How does the escape function work?", "top_k": 5}
```

---

## Design Decisions

| Decision | Why |
|----------|-----|
| **Dual JWT (access + refresh)** | 15-min access token limits exposure; 7-day refresh enables smooth UX with rotation |
| **httpOnly cookies** | Immune to XSS token theft unlike localStorage |
| **Idempotency keys on jobs** | Prevents duplicate submissions from network retries |
| **Correlation IDs everywhere** | One UUID traces a request across Frontend → Backend → Queue → Worker → AI Service |
| **Local GGUF LLM** | Zero API costs, full data privacy, works offline |
| **Qdrant over ChromaDB** | Native async support, production-grade, better scaling |
| **Celery for heavy tasks** | Keeps FastAPI event loop free; indexing can take minutes |
| **Semantic chunking** | Tree-sitter function/class extraction produces better retrieval than naive splitting |
| **BullMQ** | Battle-tested Redis queue with retry, backoff, dead-letter, priority support |

---

## Implementation Status

### ✅ Complete

- JWT auth system with token rotation and httpOnly cookies
- User, Repository, Job data models with Mongoose
- Repository CRUD with ownership validation
- BullMQ async job queue with idempotency support
- Correlation ID middleware for distributed tracing
- Worker service with job lifecycle management
- FastAPI AI service with health, indexing, query endpoints
- Full RAG pipeline: clone → parse → embed → store → query
- Tree-sitter semantic parser + adaptive regex chunker
- BGE-base-en-v1.5 embedding encoder (768-dim)
- Qdrant vector store with async/sync dual interface
- Celery background indexing with progress tracking
- Local Mistral 7B GGUF inference
- API key auth + rate limiting on AI service
- Frontend: Dashboard, Login, Register, Analysis, About pages
- Docker Compose for infrastructure

### 🔲 Remaining

- [ ] Wire up frontend login/register form submissions
- [ ] Connect Dashboard "Add repo" button to API
- [ ] Replace Analysis page mockup with real data
- [ ] SSE streaming endpoint for live analysis output
- [ ] `useStreaming` React hook + StreamingOutput component
- [ ] AnalysisResult Mongoose model for persistent results
- [ ] Global Express error handling middleware
- [ ] Root docker-compose for full-stack deployment
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19, Vite 8, React Router 7, Axios |
| **Backend** | Node.js, Express 5, Mongoose 9, BullMQ |
| **AI Service** | Python 3.13, FastAPI, Celery |
| **Embeddings** | BAAI/bge-base-en-v1.5 (768-dim) |
| **LLM** | Mistral 7B Instruct (GGUF Q4_K_M, llama-cpp-python) |
| **Vector DB** | Qdrant |
| **Database** | MongoDB |
| **Queue** | BullMQ + Redis |
| **Auth** | JWT (dual token), bcrypt, httpOnly cookies |
| **Infra** | Docker, Docker Compose |

---

## License

ISC

---

<p align="center">
  Built by <a href="https://github.com/AkshatVerma087">Akshat Verma</a>
</p>
