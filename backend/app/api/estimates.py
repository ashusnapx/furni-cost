"""Cost estimate endpoint — deterministic ABC + optional Monte Carlo."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.estimate import EstimateRequest
from app.services.costing_service import get_service

router = APIRouter(prefix="/estimates", tags=["estimates"])


@router.post("")
def create_estimate(req: EstimateRequest) -> dict:
    try:
        return get_service().estimate(
            req.product_id,
            quantity=req.quantity,
            mc_runs=req.monte_carlo_runs,
            seed=req.seed,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
