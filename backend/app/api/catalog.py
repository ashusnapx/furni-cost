"""Product catalog endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.costing_service import get_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/products")
def list_products() -> dict:
    return {"products": get_service().list_products()}


@router.get("/products/{product_id}")
def get_product(product_id: str) -> dict:
    service = get_service()
    try:
        return {"product": service.estimate(product_id, quantity=1, mc_runs=0)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
