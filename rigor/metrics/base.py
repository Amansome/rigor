"""Metric protocol."""

from typing import Protocol


class Metric(Protocol):
    name: str

    def compute(self, output: str, reference: dict, input: dict) -> float:
        ...
