"""Unit tests for pass_at_1 metric."""

import pytest
from rigor.metrics.builtin.pass_at_1 import PassAt1, _extract_code

FIB_PROMPT = "def fibonacci(n):\n"

FIB_REFERENCE = {
    "canonical_solution": "    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n",
    "test": (
        "def check(candidate):\n"
        "    assert candidate(0) == 0\n"
        "    assert candidate(1) == 1\n"
        "    assert candidate(7) == 13\n"
    ),
}

FIB_INPUT = {"prompt": FIB_PROMPT, "entry_point": "fibonacci"}


@pytest.fixture
def metric():
    return PassAt1()


def test_correct_solution(metric):
    output = FIB_REFERENCE["canonical_solution"]
    assert metric.compute(output, FIB_REFERENCE, FIB_INPUT) == 1.0


def test_wrong_solution(metric):
    output = "    return 0\n"
    assert metric.compute(output, FIB_REFERENCE, FIB_INPUT) == 0.0


def test_timeout(metric):
    output = "    while True: pass\n"
    result = metric.compute(output, FIB_REFERENCE, FIB_INPUT)
    assert result == 0.0


def test_syntax_error(metric):
    output = "    return\n  return"
    assert metric.compute(output, FIB_REFERENCE, FIB_INPUT) == 0.0


def test_extraction_from_markdown():
    output = "```python\ndef fibonacci(n): return 0\n```"
    assert _extract_code(output, "fibonacci") == "def fibonacci(n): return 0"


def test_extraction_plain():
    output = "\ndef fibonacci(n): return 0\n"
    assert _extract_code(output, "fibonacci") == "def fibonacci(n): return 0"
