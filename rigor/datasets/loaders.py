"""Dataset loaders: seed datasets into Postgres from source files."""

# TODO: Implement load_humaneval(session, n=50) for the humaneval-50 dataset:
#   - Read HumanEval JSONL (bundled or downloaded from openai/human-eval)
#   - Upsert a Dataset row with name="humaneval-50", task_type="code_generation"
#   - Upsert Example rows with input={"prompt": ...} and reference={"canonical_solution": ..., "test": ...}
#   - Called by the CLI seed command and smoke_test.sh step 3.
