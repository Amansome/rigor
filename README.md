# Rigor

A self-hostable LLM evaluation platform that treats evals like software tests: version-controlled, CI-gated, and statistically honest.

## Why

LLM changes ship to production without rigor. Prompt edits, model swaps, and temperature tweaks get merged based on spot-checking a handful of examples in a notebook. Rigor makes evaluation a first-class part of the development loop: define evals in YAML, run them on every pull request, fail builds when a change causes a statistically significant regression on a golden dataset.

## Status

Week 1 in progress. See [SPEC.md](./SPEC.md) for scope and design decisions.

## Stack

Python 3.12, FastAPI, Postgres, SQLAlchemy 2.0, LiteLLM, Ollama (local-first), Next.js dashboard (week 3).

## Local development

Requires Ollama running locally with models pulled: `qwen3.5:9b`, `gemma4:e4b`, `llama3.2:3b`.

```bash
uv sync
docker compose up -d
uv run rigor --help
```
