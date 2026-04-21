"""Pydantic v2 request/response schemas for the API."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    database: str

    model_config = ConfigDict(from_attributes=True)


class ModelResponse(BaseModel):
    id: uuid.UUID
    name: str
    provider: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetResponse(BaseModel):
    id: uuid.UUID
    name: str
    task_type: str
    example_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptResponse(BaseModel):
    id: uuid.UUID
    name: str
    version: int
    template: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RunResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    model_id: uuid.UUID
    prompt_id: uuid.UUID
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResultResponse(BaseModel):
    id: uuid.UUID
    run_id: uuid.UUID
    example_id: uuid.UUID
    output: str
    latency_ms: int
    input_tokens: int | None
    output_tokens: int | None
    cost_usd: Decimal | None
    metrics: dict
    error: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BootstrapCIResponse(BaseModel):
    mean: float
    ci_low: float
    ci_high: float
    n_samples: int
    confidence: float
    n_iterations: int


class RunSummaryResponse(BaseModel):
    run_id: uuid.UUID
    status: str
    n_results: int
    n_errors: int
    metrics: dict[str, BootstrapCIResponse]


class PairedTestResultResponse(BaseModel):
    test_name: str
    n_pairs: int
    mean_difference: float
    p_value: float
    significant_at_0_05: bool


class CompareResponse(BaseModel):
    run_a: uuid.UUID
    run_b: uuid.UUID
    metric: str
    n_pairs: int
    mean_a: float
    mean_b: float
    mean_difference: float
    tests: dict[str, PairedTestResultResponse]


class CreateRunRequest(BaseModel):
    dataset_name: str
    model_name: str
    provider: str = "ollama"
    prompt_name: str
    prompt_version: int
    sample_params: dict = {}


class CreatePromptRequest(BaseModel):
    name: str
    version: int
    template: str
