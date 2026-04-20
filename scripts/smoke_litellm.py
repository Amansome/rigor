"""Smoke test for the LiteLLM adapter against local Ollama models."""

import traceback

from rigor.models.litellm_adapter import generate

MODELS = [
    "ollama/qwen3.5:9b",
    "ollama/gemma4:e4b",
    "ollama/llama3.2:3b",
]

PROMPT = "Write a Python function that returns the nth Fibonacci number. Return only the code, no explanation."

SAMPLE_PARAMS = {"temperature": 0.2, "max_tokens": 512}

SEPARATOR = "-" * 60

for model in MODELS:
    print(SEPARATOR)
    print(f"Model     : {model}")
    try:
        result = generate(model, PROMPT, SAMPLE_PARAMS)
        print(f"Latency   : {result.latency_ms} ms")
        print(f"Tokens    : {result.input_tokens} in / {result.output_tokens} out")
        print(f"Output    : {result.output[:80]!r}")
    except Exception:
        print("ERROR:")
        traceback.print_exc()

print(SEPARATOR)
