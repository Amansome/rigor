"""SQLAlchemy ORM models for the week 1 schema."""

# TODO: Define SQLAlchemy 2.0 mapped classes for all six tables (section 3 of SPEC.md):
#   - Model (id uuid pk, name, provider, created_at)
#   - Dataset (id uuid pk, name unique, task_type, example_count, created_at)
#   - Example (id uuid pk, dataset_id fk, idx, input jsonb, reference jsonb, unique(dataset_id, idx))
#   - Prompt (id uuid pk, name, version, template, created_at, unique(name, version))
#   - Run (id uuid pk, dataset_id fk, model_id fk, prompt_id fk, config jsonb, status, started_at, completed_at, created_at)
#   - Result (id uuid pk, run_id fk, example_id fk, output, latency_ms, input_tokens, output_tokens, cost_usd, metrics jsonb, error, created_at, unique(run_id, example_id))
