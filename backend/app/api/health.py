from fastapi import APIRouter

from app import __version__

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "app": "furnicost-api"}


@router.get("/version")
def version() -> dict:
    return {"version": __version__}
