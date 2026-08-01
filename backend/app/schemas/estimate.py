"""API request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EstimateRequest(BaseModel):
    product_id: str = Field(min_length=1)
    quantity: int = Field(default=1, ge=1, le=100000)
    monte_carlo_runs: int = Field(default=5000, ge=0, le=100000)
    seed: int = Field(default=42, ge=0)
