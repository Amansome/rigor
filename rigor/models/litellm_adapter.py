"""LiteLLM adapter for Ollama (primary) and hosted providers."""

import logging
import time
from dataclasses import dataclass
from decimal import Decimal

import litellm

litellm.suppress_debug_info = True
litellm.drop_params = True  # silently drop provider-unsupported params (e.g. presence_penalty on Ollama)

from rigor.core.config import get_settings

logger = logging.getLogger(__name__)


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

    # Log which params are being sent and which will be silently dropped by litellm.
    # We compute the dropped set before the call so we have a record even on failure.
    # TODO (week 2): persist dropped_params into runs.config for a full per-run audit trail.
    if sample_params:
        supported = set(litellm.get_supported_openai_params(model=model) or [])
        sent = [k for k in sample_params if k in supported]
        dropped = [k for k in sample_params if k not in supported]
        logger.info("model=%s  sending params: %s", model, sent)
        if dropped:
            logger.info("model=%s  dropping unsupported params: %s", model, dropped)

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
