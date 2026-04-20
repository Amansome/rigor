"""LiteLLM adapter for Ollama (primary) and hosted providers."""

import time
from dataclasses import dataclass
from decimal import Decimal

import litellm

litellm.suppress_debug_info = True

from rigor.core.config import get_settings


@dataclass(frozen=True)
class GenerationResult:
    output: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_usd: Decimal
    model: str
    finish_reason: str | None


def generate(
    model: str,
    prompt: str,
    sample_params: dict | None = None,
) -> GenerationResult:
    settings = get_settings()

    if not settings.use_hosted_models and not model.startswith("ollama/"):
        raise ValueError(
            "Hosted models are disabled. Set USE_HOSTED_MODELS=true to enable."
        )

    kwargs: dict = {}

    if model.startswith("ollama/"):
        kwargs["api_base"] = settings.ollama_base_url
        # Qwen3-family models run in extended thinking mode by default, which
        # routes all tokens into a hidden reasoning field and leaves content
        # empty. think=False disables thinking; it's a no-op for other models.
        kwargs["think"] = False
    elif model.startswith("anthropic/") and settings.anthropic_api_key:
        kwargs["api_key"] = settings.anthropic_api_key
    elif model.startswith("openai/") and settings.openai_api_key:
        kwargs["api_key"] = settings.openai_api_key

    if sample_params:
        kwargs.update(sample_params)

    t0 = time.perf_counter()
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        **kwargs,
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)

    try:
        cost = Decimal(str(litellm.completion_cost(response)))
    except Exception:
        cost = Decimal("0")

    return GenerationResult(
        output=response.choices[0].message.content,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        latency_ms=latency_ms,
        cost_usd=cost,
        model=model,
        finish_reason=response.choices[0].finish_reason,
    )
