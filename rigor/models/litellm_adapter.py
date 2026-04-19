"""LiteLLM adapter for Ollama (primary) and hosted providers."""

# TODO: Implement ModelAdapter with a single call() method:
#   call(model_name, provider, prompt, sample_params) -> AdapterResponse
#   - For provider="ollama": prefix model name with "ollama/" for LiteLLM routing,
#     set api_base to OLLAMA_BASE_URL from settings.
#   - For provider="anthropic" or "openai": raise RuntimeError if USE_HOSTED_MODELS=false.
#   - Return output text, latency_ms, input_tokens, output_tokens, cost_usd.
#   Use litellm.completion() (sync) throughout — no async.
