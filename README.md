# Rigor

A self-hostable LLM evaluation platform that treats evals like software tests: version-controlled, CI-gated, and statistically honest.

## Why

LLM changes ship to production without rigor. Prompt edits, model swaps, and temperature tweaks get merged based on spot-checking a handful of examples in a notebook. Rigor makes evaluation a first-class part of the development loop: define evals in YAML, run them on every pull request, fail builds when a change causes a statistically significant regression on a golden dataset.

## Benchmark results (week 1)

HumanEval, first 50 problems, codegen_v1 prompt, temperature=0.2.

| Model | pass@1 | exact_match | avg_latency_s |
|---|---|---|---|
| llama3.2:3b | 0.78 | 0.00 | 2.8 |
| gemma4:e4b | 0.76 | 0.11 | 9.7 |
| qwen3.5:9b | 0.46 | 0.05 | 10.8 |

### Measurement caveats

1. One-shot greedy sampling (temperature=0.2, single sample), not the multi-sample variant used in Meta's/OpenAI's published numbers.
2. First 50 HumanEval problems only (not full 164). These skew easier than the full set.
3. Permissive code extraction: we accept plain code, fenced markdown, or mixed output.

### Known model-specific failure modes

**Qwen 3.5 9B** scored 46% pass@1, substantially below Gemma 4 E4B (76%) and Llama 3.2 3B (78%). Investigation showed Qwen interprets HumanEval prompts as completion targets and emits only the function body, omitting the `def <name>(...):` signature. When the sandbox appends the test harness and calls `check(<entry_point>)`, the function is undefined and the test raises NameError. This is a prompt-format sensitivity, not a model capability gap — verifying it would require either a signature-preserving prompt template or an extraction layer that splices the prompt's signature back onto the output. Neither change was made in week 1 to preserve the integrity of the initial measurement.

## Status

Week 1 in progress. See [SPEC.md](./SPEC.md) for scope and design decisions.

## Stack

Python 3.12, FastAPI, Postgres, SQLAlchemy 2.0, LiteLLM, Ollama (local-first), Next.js dashboard (week 3).

## Local development

Requires Ollama running locally with models pulled: `qwen3.5:9b`, `gemma4:e4b`, `llama3.2:3b`.

```bash
uv sync
docker compose up -d
uv run rigor --help
```
