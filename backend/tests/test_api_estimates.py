"""API endpoints — estimates + catalog (in-memory fetcher; KG optional)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_catalog_lists_products():
    r = client.get("/api/v1/catalog/products")
    assert r.status_code == 200
    products = r.json()["products"]
    assert len(products) == 4
    assert {p["product_id"] for p in products} == {"prod-dining-chair", "prod-sofa-3seat", "prod-coffee-table", "prod-wardrobe"}


def test_estimate_chair():
    r = client.post("/api/v1/estimates", json={"product_id": "prod-dining-chair"})
    assert r.status_code == 200
    data = r.json()
    assert data["per_unit"]["totals"]["total"] == data["for_quantity"]["totals"]["total"]
    assert data["per_unit"]["totals"]["total"] == "303.77"


def test_estimate_with_quantity_and_monte_carlo():
    r = client.post(
        "/api/v1/estimates",
        json={"product_id": "prod-dining-chair", "quantity": 3, "monte_carlo_runs": 2000, "seed": 1},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["for_quantity"]["totals"]["total"] == "911.31"
    mc = data["monte_carlo"]
    assert mc["runs"] == 2000
    assert mc["point_estimate"] == 303.77
    assert mc["distribution"]["p10"] <= mc["distribution"]["p50"] <= mc["distribution"]["p90"]
    assert mc["total_for_quantity"]["p50"] == round(mc["distribution"]["p50"] * 3, 2)
    assert len(mc["histogram"]) == 20


def test_estimate_monte_carlo_off():
    r = client.post("/api/v1/estimates", json={"product_id": "prod-dining-chair", "monte_carlo_runs": 0})
    assert r.status_code == 200
    assert r.json()["monte_carlo"] is None


def test_estimate_unknown_product():
    r = client.post("/api/v1/estimates", json={"product_id": "nope"})
    assert r.status_code == 404


def test_estimate_invalid_quantity():
    r = client.post("/api/v1/estimates", json={"product_id": "prod-dining-chair", "quantity": 0})
    assert r.status_code == 422


def test_catalog_product_detail():
    r = client.get("/api/v1/catalog/products/prod-coffee-table")
    assert r.status_code == 200
    tree = r.json()["product"]["tree"]
    assert tree["node_id"] == "prod-coffee-table"
    assert {c["node_id"] for c in tree["children"]} == {"comp-table-top", "comp-chair-leg"}
