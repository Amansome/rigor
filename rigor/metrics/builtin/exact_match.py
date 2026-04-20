"""Exact-match metric: 1.0 if output equals canonical_solution, else 0.0."""

from rigor.metrics import registry


class ExactMatch:
    name = "exact_match"

    def compute(self, output: str, reference: dict, input: dict) -> float:
        return 1.0 if output.strip() == reference["canonical_solution"].strip() else 0.0


registry.register(ExactMatch())
