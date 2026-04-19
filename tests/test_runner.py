"""Tests for the eval runner."""

# TODO: Add integration tests for core/runner.py using a real (test) Postgres DB and a mock LiteLLM adapter:
#   - Run completes and persists Result rows
#   - Run transitions status: pending -> running -> completed
#   - Run status set to "failed" on adapter error
