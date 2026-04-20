"""Metric registry: maps metric names to Metric instances."""

from rigor.metrics.base import Metric

_registry: dict[str, Metric] = {}


def register(metric: Metric) -> None:
    _registry[metric.name] = metric


def get(name: str) -> Metric:
    if name not in _registry:
        raise KeyError(f"Metric '{name}' not registered. Available: {list(_registry)}")
    return _registry[name]


def all_names() -> list[str]:
    return sorted(_registry)
