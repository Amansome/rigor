#!/usr/bin/env bash
set -euo pipefail

# TODO Step 1: Start Postgres + API via docker compose
#   docker compose up -d
#   Wait for Postgres to be healthy (poll /health or pg_isready)

# TODO Step 2: Initialize DB schema
#   uv run rigor db init   (calls create_all())

# TODO Step 3: Seed humaneval-50 dataset
#   uv run rigor seed humaneval --count 50

# TODO Step 4: Register 3 Ollama models
#   uv run rigor models register --name qwen3.5:9b  --provider ollama
#   uv run rigor models register --name gemma4:e4b  --provider ollama
#   uv run rigor models register --name llama3.2:3b --provider ollama

# TODO Step 5: Run the eval config
#   uv run rigor run configs/humaneval_codegen.yaml

# TODO Step 6: Poll until all 3 runs complete
#   Poll GET /api/v1/runs every 5s until all runs have status="completed" or "failed"

# TODO Step 7: Print summary table
#   uv run rigor runs summary   (shows model, pass@1, exact_match, avg latency)
