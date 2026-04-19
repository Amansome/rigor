"""Metric registry: maps metric names to BaseMetric instances."""

# TODO: Implement MetricRegistry with:
#   - register(metric: BaseMetric) — add a metric by name
#   - get(name: str) -> BaseMetric — lookup or raise KeyError
#   - default_registry() — returns registry pre-loaded with exact_match and pass_at_1
#   This registry is the extension point for the week 2 plugin system.
