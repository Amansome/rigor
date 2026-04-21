#!/usr/bin/env bash
set -euo pipefail

API="http://localhost:8000/api/v1"
TIMEOUT_MINUTES=45
POLL_INTERVAL=10

# Require jq
if ! command -v jq &>/dev/null; then
  echo "ERROR: jq is required but not installed. Install it with: brew install jq" >&2
  exit 1
fi

# ── Step 1: Ensure docker compose is running ──────────────────────────────────
echo "==> Ensuring Postgres is running..."
docker compose up -d

# Wait for Postgres to be ready
for i in $(seq 1 30); do
  if docker compose exec -T postgres pg_isready -U rigor &>/dev/null; then
    echo "    Postgres ready."
    break
  fi
  if [[ $i -eq 30 ]]; then
    echo "ERROR: Postgres did not become ready in time." >&2
    exit 1
  fi
  sleep 2
done

# ── Step 2: Start API if not already running ──────────────────────────────────
API_PID=""
if curl -sf "${API}/health" &>/dev/null; then
  echo "==> API already running, skipping start."
else
  echo "==> Starting API..."
  uv run uvicorn rigor.api.main:app --port 8000 &
  API_PID=$!
  sleep 3
  if ! curl -sf "${API}/health" &>/dev/null; then
    echo "ERROR: API did not start in time." >&2
    kill "$API_PID" 2>/dev/null || true
    exit 1
  fi
  echo "    API running (PID $API_PID)."
fi

cleanup() {
  if [[ -n "$API_PID" ]]; then
    echo "==> Stopping API (PID $API_PID)..."
    kill "$API_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

# ── Step 3: Seed models and dataset ──────────────────────────────────────────
echo "==> Seeding models..."
uv run python scripts/seed_dev.py

echo "==> Seeding HumanEval-50 dataset..."
uv run python - <<'PYEOF'
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from rigor.db.session import SessionLocal
from rigor.datasets.loaders import load_humaneval
db = SessionLocal()
try:
    ds = load_humaneval(db, limit=50)
    print(f"  Dataset ready: {ds.name} ({ds.example_count} examples)")
finally:
    db.close()
PYEOF

# ── Step 4: Register codegen_v1 prompt ───────────────────────────────────────
echo "==> Registering codegen_v1 prompt..."
PROMPT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${API}/prompts" \
  -H "Content-Type: application/json" \
  -d '{"name":"codegen_v1","version":1,"template":"{{ prompt }}"}')

if [[ "$PROMPT_STATUS" == "201" ]]; then
  echo "    Prompt registered."
elif [[ "$PROMPT_STATUS" == "409" ]]; then
  echo "    Prompt already exists, continuing."
else
  echo "ERROR: Unexpected status $PROMPT_STATUS registering prompt." >&2
  exit 1
fi

# ── Step 5: POST three runs ───────────────────────────────────────────────────
echo "==> Submitting runs..."
MODELS=("qwen3.5:9b" "gemma4:e4b" "llama3.2:3b")
RUN_IDS=()

for MODEL in "${MODELS[@]}"; do
  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API}/runs" \
    -H "Content-Type: application/json" \
    -d "{
      \"dataset_name\": \"humaneval-50\",
      \"model_name\": \"${MODEL}\",
      \"provider\": \"ollama\",
      \"prompt_name\": \"codegen_v1\",
      \"prompt_version\": 1,
      \"sample_params\": {\"temperature\": 0.2, \"max_tokens\": 1024, \"top_p\": 1.0}
    }")
  BODY=$(echo "$RESPONSE" | sed '$d')
  STATUS=$(echo "$RESPONSE" | tail -n 1)

  if [[ "$STATUS" != "202" ]]; then
    echo "ERROR: Failed to create run for $MODEL (HTTP $STATUS): $BODY" >&2
    exit 1
  fi

  RUN_ID=$(echo "$BODY" | jq -r '.id')
  RUN_IDS+=("$RUN_ID")
  echo "    Run $RUN_ID submitted for $MODEL"
done

# ── Step 6: Poll until all runs complete ─────────────────────────────────────
echo "==> Polling runs (timeout: ${TIMEOUT_MINUTES}m, interval: ${POLL_INTERVAL}s)..."
MAX_POLLS=$(( TIMEOUT_MINUTES * 60 / POLL_INTERVAL ))

for i in $(seq 1 $MAX_POLLS); do
  ALL_DONE=true
  for RUN_ID in "${RUN_IDS[@]}"; do
    RUN_STATUS=$(curl -s "${API}/runs/${RUN_ID}" | jq -r '.status')
    if [[ "$RUN_STATUS" != "completed" && "$RUN_STATUS" != "failed" ]]; then
      ALL_DONE=false
      break
    fi
  done

  if $ALL_DONE; then
    echo "    All runs finished."
    break
  fi

  if [[ $i -eq $MAX_POLLS ]]; then
    echo "ERROR: Timed out waiting for runs to complete." >&2
    exit 1
  fi

  echo "    [$(date +%H:%M:%S)] Still running... (poll $i/$MAX_POLLS)"
  sleep $POLL_INTERVAL
done

# ── Step 7: Print summary table ───────────────────────────────────────────────
echo ""
echo "==> Results"
printf "%-20s %-30s %-30s %-5s\n" "model" "pass@1" "exact_match" "n"
printf "%-20s %-30s %-30s %-5s\n" "-----" "------" "-----------" "-"

for idx in "${!RUN_IDS[@]}"; do
  RUN_ID="${RUN_IDS[$idx]}"
  MODEL="${MODELS[$idx]}"
  SUMMARY=$(curl -s "${API}/runs/${RUN_ID}/summary")
  N=$(echo "$SUMMARY" | jq -r '.n_results')

  fmt_ci() {
    local metric="$1"
    local mean ci_low ci_high
    mean=$(echo "$SUMMARY" | jq -r ".metrics.${metric}.mean // \"n/a\"")
    if [[ "$mean" == "n/a" ]]; then
      echo "n/a"
      return
    fi
    ci_low=$(echo "$SUMMARY" | jq -r ".metrics.${metric}.ci_low")
    ci_high=$(echo "$SUMMARY" | jq -r ".metrics.${metric}.ci_high")
    printf "%.2f [%.2f, %.2f]" "$mean" "$ci_low" "$ci_high"
  }

  PASS=$(fmt_ci "pass_at_1")
  EXACT=$(fmt_ci "exact_match")
  printf "%-20s %-30s %-30s %-5s\n" "$MODEL" "$PASS" "$EXACT" "$N"
done

echo ""
echo "Done."
