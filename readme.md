# Codebase Investigator — README

**RAG-powered Developer Assistant**

A developer tool that ingests a codebase (source, docs, commits, issues), builds a retrieval index (LangChain + HuggingFace embeddings + Chroma), and uses RAG to answer developer questions and propose draft PRs. Includes a FastAPI backend and a minimal React frontend demo (ChatGPT-like chat with fixed bottom input, code/diff viewer, Download).

This README will help you set up, run, and extend the project.

---

# Shapshort of the projects:

<img width="2940" height="1670" alt="image" src="https://github.com/user-attachments/assets/2c84020a-25cb-4a5e-b6a1-0de0c7c548ff" />


## Table of contents

1. [Project overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Prerequisites](#prerequisites)
5. [Getting started (local dev)](#getting-started-local-dev)

   * [Environment variables](#environment-variables)
   * [Backend setup (FastAPI)](#backend-setup-fastapi)
   * [Frontend setup (React)](#frontend-setup-react)

6. [License & credits](#license--credits)

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
