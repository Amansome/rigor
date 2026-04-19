"""Routes for /api/v1/runs."""

# TODO: Implement the four runs endpoints (section 4 of SPEC.md):
#   - POST /runs   — validate config, create Run rows (one per model), enqueue runner in thread pool
#   - GET  /runs   — list all runs, ordered by created_at desc
#   - GET  /runs/{run_id}         — single run detail
#   - GET  /runs/{run_id}/results — paginated results for a run
