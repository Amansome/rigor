# Rigor — LLM Evaluation & Regression Platform

## 1. Problem statement

Teams shipping LLM features have no standard way to know if a prompt change, model swap, or temperature tweak made their system better or worse. "Better" is judged by eyeballing a handful of examples in a notebook, and regressions ship to production unnoticed. Rigor is a self-hostable platform that treats LLM evaluation like software testing: evals live in version control, run on every pull request, and fail the build when a change causes a statistically significant regression on a golden dataset.

Rigor ships with built-in support for code-generation tasks (HumanEval), pluggable metrics (exact match, pass@k via sandboxed execution, semantic similarity, LLM-as-judge), statistically honest comparisons (bootstrap confidence intervals, paired significance tests), and a Next.js dashboard for exploring results across models and prompt versions. The platform runs fully on local models via Ollama by default; hosted adapters for Anthropic and OpenAI are included but gated behind a configuration flag.

## 2. Scope

### Week 1 (this week)
Core infrastructure. By end of week 1, a developer can:
1. Define an eval config in YAML
2. Run it against multiple models via one CLI command
3. See results persisted in Postgres
4. Query past runs via a REST API

No dashboard, no CI integration, no LLM judge, no confidence intervals yet. Just a working eval pipeline with one real task and one real metric.

### Week 2
Evaluation rigor. Metric registry with plugin system. Bootstrap confidence intervals on all metrics. Paired significance tests between models. MLflow integration. LLM-as-judge with seed-variance calibration.

### Week 3
Deploy and showcase. GitHub Actions regression gate. Next.js dashboard (runs list, run detail, model comparison). Public deploy (Fly.io for API, Neon for Postgres, Vercel for dashboard). README with architecture diagram and benchmark results across 3+ models.

## 3. Week 1 data model

Postgres schema. SQLAlchemy 2.0 with sync sessions; `create_all()` on app startup for week 1. Alembic migrations are a week 3 addition once the schema stabilizes.

```
models
  id              uuid primary key
  name            text not null           # "qwen3.5:9b"
  provider        text not null           # "ollama" | "anthropic" | "openai"
  created_at      timestamptz not null default now()

datasets
  id              uuid primary key
  name            text not null unique    # "humaneval-50"
  task_type       text not null           # "code_generation"
  example_count   int  not null
  created_at      timestamptz not null default now()

examples
  id              uuid primary key
  dataset_id      uuid references datasets(id) on delete cascade
  idx             int  not null
  input           jsonb not null
  reference       jsonb not null
  unique (dataset_id, idx)

prompts
  id              uuid primary key
  name            text not null
  version         int  not null
  template        text not null           # Jinja2 template
  created_at      timestamptz not null default now()
  unique (name, version)

runs
  id              uuid primary key
  dataset_id      uuid references datasets(id)
  model_id        uuid references models(id)
  prompt_id       uuid references prompts(id)
  config          jsonb not null
  status          text not null           # "pending" | "running" | "completed" | "failed"
  started_at      timestamptz
  completed_at    timestamptz
  created_at      timestamptz not null default now()

results
  id              uuid primary key
  run_id          uuid references runs(id) on delete cascade
  example_id      uuid references examples(id)
  output          text not null
  latency_ms      int  not null
  input_tokens    int
  output_tokens   int
  cost_usd        numeric(10, 6)
  metrics         jsonb not null
  error           text
  created_at      timestamptz not null default now()
  unique (run_id, example_id)
```

## 4. Week 1 API surface

FastAPI, all endpoints under `/api/v1`. Sync handlers with thread pool for model calls.

```
POST   /runs                         # create and kick off a run
GET    /runs                         # list runs
GET    /runs/{run_id}                # run detail
GET    /runs/{run_id}/results        # paginated results

GET    /datasets
GET    /datasets/{dataset_id}
GET    /models
POST   /prompts
GET    /prompts
GET    /health
```

## 5. Config schema

```yaml
# configs/humaneval_codegen.yaml
dataset: humaneval-50
prompt:
  name: codegen_v1
  version: 1
models:
  - name: qwen3.5:9b
    provider: ollama
  - name: gemma4:e4b
    provider: ollama
  - name: llama3.2:3b
    provider: ollama
sample_params:
  temperature: 0.2
  max_tokens: 1024
  top_p: 1.0
  presence_penalty: 0
metrics:
  - pass_at_1
  - exact_match
```

## 6. Built-in metrics for week 1

Only `exact_match` and `pass_at_1`. The pass_at_1 metric executes generated code in a sandboxed subprocess with 10s timeout, no network, tmpfs workdir.

## 7. Model adapter

Use LiteLLM. Primary target is Ollama local models. Hosted adapters (Anthropic, OpenAI) implemented but gated behind `use_hosted_models=false` flag.

## 8. Week 1 acceptance test

A shell script `scripts/smoke_test.sh` that:
1. Starts Postgres + API via docker compose
2. Initializes DB schema via create_all()
3. Seeds humaneval-50 dataset
4. Registers 3 Ollama models (qwen3.5:9b, gemma4:e4b, llama3.2:3b)
5. Runs the eval config
6. Polls until all 3 runs complete
7. Prints summary table

## 9. Repo structure

```
rigor/
  SPEC.md
  README.md
  pyproject.toml
  docker-compose.yml
  .gitignore
  .env.example
  .github/workflows/ci.yml
  configs/
    humaneval_codegen.yaml
  rigor/
    __init__.py
    api/
      __init__.py
      main.py
      routes/
        __init__.py
        runs.py
        datasets.py
        models.py
        prompts.py
        health.py
      schemas.py
    db/
      __init__.py
      models.py
      session.py
    core/
      __init__.py
      config.py
      runner.py
    metrics/
      __init__.py
      base.py
      registry.py
      builtin/
        __init__.py
        exact_match.py
        pass_at_1.py
    models/
      __init__.py
      litellm_adapter.py
    datasets/
      __init__.py
      loaders.py
    cli.py
  tests/
    __init__.py
    test_api.py
    test_metrics.py
    test_runner.py
  scripts/
    smoke_test.sh
```

## 10. Explicit non-goals for week 1

No auth, no web UI, no MLflow, no CIs, no LLM-as-judge, no CI regression gate, no multi-user, no hyperparameter sweeps, no fine-tuning, no RAG eval.

## 11. Design decisions worth defending in interviews

- Local models (Ollama) as default evaluation target
- Sync FastAPI with thread pool (not async)
- Postgres over SQLite
- LiteLLM over per-provider SDKs
- Verifiable metrics (pass@1) before LLM-as-judge
- Pydantic v2 for all config validation
- Store full resolved config on runs.config for reproducibility
