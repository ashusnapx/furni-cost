# FurniCost — AI-Driven Manufacturing Cost Estimation Assistant

Interactive web tool for the furniture industry: users input product/process details, receive AI-generated itemized cost estimates (materials, labor, machine, overhead) with natural-language justification, run what-if scenario simulations, and export reports.

## Stack (researched Aug 2026)

| Layer | Tech |
|---|---|
| Frontend | Next.js 16.2.12 (Turbopack, React 19.2) · Tailwind v4 · shadcn/ui · GSAP · Framer Motion |
| Backend | Python 3.12 · FastAPI 0.141 (native SSE) · uvicorn |
| Agents | LangGraph 1.2 (supervisor + specialist agents) · LangChain 1.3 |
| LLM | Gemini (free tier, Flash-class only — Pro is paid-only since Apr 2026) |
| Knowledge | Neo4j 2026.06 (AuraDB-free-compatible schema) |
| Retrieval | PageIndex vectorless RAG (tree index + LLM reasoning, no embeddings/vector DB) |
| Tools | MCP server (read-only ERP tools) |
| Observability | Langfuse (traces, prompt mgmt, evals) |
| Infra | Docker Compose · Postgres 17 (LangGraph checkpointer) |

## Architecture rules

1. **LLMs never compute numbers.** Deterministic Activity-Based Costing (ABC) engine is the source of truth; Gemini only explains/narrates from sanitized context. Kills hallucination, audit, and privacy issues at once.
2. **No raw financial data on free-tier Gemini keys** (free tier: prompts may be used for training). All demo data is synthetic.
3. Cost structure: `total = materials + labor + machine + overhead(ABC)`. Monte Carlo scenario simulation on rate/qty distributions.

## Repo layout

```
frontend/   Next.js 16 app (app router, shadcn, gsap, framer-motion)
backend/    FastAPI (uv) — app/{api,core,graph,kg,rag,mcp,synth,obs}
infra/      docker-compose: neo4j, postgres, redis, langfuse
```

## Quickstart

```bash
# infra
docker compose -f infra/docker-compose.yml up -d neo4j postgres redis

# backend
cd backend
cp .env.example .env          # fill GEMINI_API_KEY
uv sync
uv run uvicorn app.main:app --reload --port 8000

# frontend
cd frontend
npm install
npm run dev                   # http://localhost:3000
```

## Milestones

- M0 ✅ scaffold: frontend + backend + infra, ABC engine core, health API
- M1 ✅ synthetic factory catalog, Neo4j KG load (42 nodes / 140 rels), multi-level BOM rollup, Monte Carlo, catalog + estimates API
- M2 MCP server, LangGraph supervisor, SSE streaming, Langfuse tracing
- M3 PageIndex vectorless RAG for spec sheets
- M4 cockpit UI: BOM configurator, cost breakdown, scenario lab
- M5 AI explainer chat, report export, accuracy eval loop
