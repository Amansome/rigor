"""pass@1 metric: executes generated code in sandboxed subprocess."""

# TODO: Implement PassAtOne(BaseMetric) with name = "pass_at_1":
#   score(output, reference) — write generated code + test harness to a tmpfs workdir,
#   execute in a subprocess with 10s timeout, no network access (resource limits via
#   subprocess env). Return 1.0 if exit code 0, else 0.0.
#   Reference dict contains the HumanEval test field to append after the generated function.
