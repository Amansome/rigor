"""Pydantic v2 request/response schemas for the API."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: str

    model_config = {"from_attributes": True}


class ModelResponse(BaseModel):
    id: uuid.UUID
    name: str
    provider: str
    created_at: datetime

    model_config = {"from_attributes": True}
