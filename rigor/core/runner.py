"""Eval runner: orchestrates a single Run end-to-end."""

# TODO: Implement run_eval(run_id, session) (section 2 week 1 / section 8 of SPEC.md):
#   1. Load Run + Dataset + Examples + Prompt from DB
#   2. Render each example through the Jinja2 prompt template
#   3. Call LiteLLM adapter for each example (sync, thread pool at call site)
#   4. Evaluate output with each configured metric via the metric registry
#   5. Persist Result rows with output, latency_ms, token counts, cost_usd, metrics jsonb
#   6. Update Run.status to "completed" or "failed"
