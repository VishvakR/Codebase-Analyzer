# Codebase Investigator — README

**RAG-powered Developer Assistant & Auto-PR Generator**

A developer tool that ingests a codebase (source, docs, commits, issues), builds a retrieval index (LangChain + HuggingFace embeddings + Chroma), and uses RAG to answer developer questions and propose draft PRs. Includes a FastAPI backend and a minimal React frontend demo (ChatGPT-like chat with fixed bottom input, code/diff viewer, Download).

This README will help you set up, run, and extend the project.

---

## Table of contents

1. [Project overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Prerequisites](#prerequisites)
5. [Getting started (local dev)](#getting-started-local-dev)

   * [Environment variables](#environment-variables)
   * [Backend setup (FastAPI)](#backend-setup-fastapi)
   * [Frontend setup (React)](#frontend-setup-react)
7. [Prompt templates (system + user + parsing rules)](#prompt-templates-system--user--parsing-rules)
8. [Indexing strategies & vector DB management](#indexing-strategies--vector-db-management)
9. [PR generation flow & safety checks](#pr-generation-flow--safety-checks)
10. [Troubleshooting (Chroma readonly, permissions)](#troubleshooting-chroma-readonly-permissions)
11. [License & credits](#license--credits)

---

## Project overview

**Goal:** build a RAG-enabled assistant that can answer questions about a repository, show exact evidence (file:path@commit chunks), and propose code patches (unified diffs) along with tests. The app demonstrates systems thinking across retrieval, LLM prompting, Git integration.

**Stack (recommended / used in examples):**

* Backend: Python + FastAPI
* RAG: LangChain
* Embeddings: `HuggingFaceEmbeddings` (e.g., `all-MiniLM-L6-v2` / `all-mpnet-base-v2`)
* Vector DB: Chroma (local persistent DB)
* Repo management: GitPython
* Frontend: React + Tailwind (minimal demo)
* Optional: Docker for sandboxed test runs, GitHub Actions for CI

---

## Features

* Clone & ingest repositories (source files, README, docs, tests).
* Chunking (RecursiveCharacterTextSplitter) and embedding (HuggingFace).
* Persistent Chroma vector store with clear / incremental update modes.
* RAG pipeline: retrieve top-k contexts and call LLM (OpenAI or local).
* Chat UI (ChatGPT-style) to ask questions — returns explanation + citations + optional `diff`.
* Safety checks: patch size limit, allowed-files checks, test run hooks, linting.

---

## Architecture

```
[Frontend React] -> [FastAPI Backend]
                   - Ingest (git clone) -> Snapshot Manager
                   - Indexer (chunk -> embeddings -> Chroma)
                   - Retriever + Prompt Assembly -> LLM (RAG)
                   - PR Generator (apply diff -> push branch -> open PR)
                   - Test runner (Docker / GitHub Actions)
Vector DB: Chroma (persisted on disk or cloud)
Embeddings: HuggingFace models (local) or OpenAI embeddings (optional)
```

---

## Prerequisites

* Python 3.10+
* Node.js 18+ (for frontend dev)
* Git
* Optional: Docker (for sandboxed test runs)

Python packages (example `requirements.txt`):

```
fastapi
uvicorn
gitpython
langchain
chromadb
transformers
sentence-transformers
langchain-huggingface
langchain-chroma
python-dotenv
```

Install in a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Getting started (local dev)

### Environment variables

Create a `.env` file in the backend folder:

```
WORK_DIR=/tmp/code_investigator
CHROMA_DIR=./data/chroma_vector_db
HF_EMBED_MODEL=all-mpnet-base-v2
OPENAI_API_KEY=    # optional if using OpenAI
```

Load with `python-dotenv` or your deployment tool.

---

### Backend setup (FastAPI)

Example layout in `app/` (based on earlier conversation):

```
app/
  main.py                # FastAPI app (ingest, query, generate_pr, history, diff, download)
  ingestion_pipeline.py             # clone & index repo; chunking & Chroma upsert
  retriever_pipeline.py           # RAG: retrieve chunks + assemble prompt + call LLM
  utils/
    file_loader.py       # load files as langchain Documents (for chunking)
    display_code.py
    file_loader.py
    file_ext.py
```

Run server:

```bash
python3 main.py
```

**Important**: the backend must have write permission to `CHROMA_DIR`. If you see `attempt to write a readonly database`, check permissions (see troubleshooting below).

---

### Frontend setup (React)

Minimal React component already prepared (single file). Typical steps:

1. `npm create vite@latest` (or your setup)
2. Add Tailwind.
3. Start:

```bash
cd frontend
npm install
npm run dev
```

Frontend talks to backend routes:

* POST `/ingest` — clone & index repo
* GET `/history/{repo_name}` — list snapshots
* GET `/diff/{repo}/{old}/{new}?path=...` — get diff
* POST `/query` — ask assistant (RAG + LLM)
* POST `/generate_pr` — apply diff & open PR
* GET `/download/{repo_name}` — download repo zip (optional)

---

## Prompt templates (system + user + parsing rules)

**System prompt**

````
System: You are a careful senior software engineer assistant that answers questions about a single indexed repository. Use ONLY the provided EVIDENCE blocks (file path + commit + code chunk). Do NOT invent commit IDs, file names, or line numbers. Be conservative. 
Output format:
1) SUMMARY:
2) EVIDENCE:
file:path@commit — rationale
3) FIX:
```diff
<unified diff>
````

4. TESTS:
   (code fences or 'No tests provided')
5. METADATA:

```json
{ "confidence": "low|medium|high", "modified_files": ["..."], "patch_size_bytes": 123 }
```

```

**User prompt template** (frontend fills):
```

User:
repo_name: {repo_name}
snapshot_commit: {snapshot_commit}
selected_files: {files}
file_contexts:
// file: path@commit <code chunk>

QUESTION:
{question}

CONSTRAINTS:

* allowed_files: {allowed_files}
* max_patch_bytes: {max_patch_bytes}

````

**Frontend parsing rules**
- Extract `SUMMARY` (first non-empty line after `SUMMARY:`).
- Extract `EVIDENCE` lines matching `file:path@commit[:line-range]`.
- Extract first ```diff``` block via `const diffMatch = text.match(/```diff([\s\S]*?)```/);`.
- Extract `TESTS` fenced blocks.
- Parse `METADATA` JSON block.
- Validate patch size and allowed files before enabling PR creation.

---

## Indexing strategies & vector DB management

**Two modes:**
- **Reset on ingest (simple)** — remove previous collection and recreate from scratch.
- **Incremental updates (recommended for large repos)** — compute file hash / commit id for each file and only upsert changed chunks.

**Reset approach (safe)**
```python
vector_store = Chroma(collection_name="collections",
                      embedding_function=embedding,
                      persist_directory="data/chroma_vector_db")
if os.path.exists("data/chroma_vector_db"):
    vector_store.delete_collection()
    vector_store = Chroma(...persist_directory="data/chroma_vector_db")
vector_store.add_documents(chunks, ids=ids)
vector_store.persist()
````

**Incremental approach (recommended in production)**

* Compute fingerprint per file (sha1 of content).
* Store metadata `{"path": "...", "commit": "...", "file_hash": "..."}` per chunk.
* Query DB for existing chunk ids/metadata. Upsert only new/changed chunks; optionally delete removed ones.

**Metadata to store per chunk**

```
{
  "path": "src/foo.py",
  "commit": "abc123",
  "file_hash": "sha1...",
  "chunk_id": 0
}
```

---

## PR generation flow & safety checks

1. LLM returns a patch in unified diff format in `FIX` section.
2. Frontend extracts diff & metadata; validate:

   * `len(diff_bytes) <= max_patch_bytes`
   * `metadata.modified_files` ⊆ `allowed_files` (if provided)
   * `confidence` not `low` (optional UX gating)
3. Backend (`pr_generator`) flow:

   * Create a new branch in a fork or in local checkout.
   * Apply patch via `git apply` or by editing files programmatically.
   * Run test suite in sandbox (Docker) or submit to GitHub Actions.
   * Run linters/static analysis (bandit, mypy).
   * If tests pass, open a **draft PR** via PyGithub with evidence & metadata.
4. Always require human review before merging.

---

## Testing

* Unit tests for chunking, id generation, and metadata extraction (pytest).
* Integration tests:

  * Ingest a small public repo and validate snapshot list.
  * Run `POST /query` with a known question and expect evidence in response.
  * Simulate PR generation (apply diff in a temp clone) and run tests in Docker.
* Example:

```bash
pytest tests/
```

---

## Deployment notes

* Run FastAPI behind a process manager (gunicorn/uvicorn) and reverse proxy (nginx).
* Persist `CHROMA_DIR` on a volume with sufficient IOPS.
* Secrets: store `GITHUB_TOKEN`, `OPENAI_API_KEY` in secret manager or environment variables.
* Scale:

  * Use Qdrant for larger workloads (vector search clustering, persistence).
  * Use a queue (Redis + RQ / Celery) for ingestion & long-running tasks.

---

## Roadmap / future work

* Add AST-aware chunker (function/class boundaries).
* Add reranker (BM25 + embedding similarity).
* Add RLHF/feedback loop: track accepted/rejected PRs to fine-tune prompt ranks.
* Add CI sandboxing via Docker & GitHub Actions templates.
* Add team dashboards and metrics: PR acceptance rates, retrieval precision@k.
* Add multi-repo enterprise mode + access control + audit logs.

---

## Contribution guide

* Open an issue describing the feature/bug.
* Create a branch `feat/<short-desc>` or `fix/<short-desc>`.
* Add tests for new functionality.
* Open a draft PR and link the issue.

---

## Contact & Credits

Created by — Vishvak, LinkedIn : https://www.linkedin.com/in/vishvak-r/

---