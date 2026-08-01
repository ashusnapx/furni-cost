"""Catalog integrity — synthetic blueprint must be complete and deterministic."""

from __future__ import annotations

from decimal import Decimal

from app.synth.catalog import (
    ACTIVITIES,
    ACTIVITY_RATES,
    COMPONENTS,
    LABOR,
    MACHINE_RATES,
    MACHINES,
    MATERIAL_PRICES,
    MATERIALS,
    OPERATION_LINES,
    PRODUCTS,
)
from app.synth.fetcher import CatalogFetcher

OPERATION_IDS = set(OPERATION_LINES)
ACTIVITY_IDS = set(ACTIVITY_RATES)
MATERIAL_IDS = set(MATERIAL_PRICES)
MACHINE_IDS = set(MACHINE_RATES)
LABOR_IDS = set(LABOR)
COMPONENT_IDS = {c["component_id"] for c in COMPONENTS}
PRODUCT_IDS = {p["product_id"] for p in PRODUCTS}
NODE_IDS = COMPONENT_IDS | PRODUCT_IDS


def test_money_parses_to_decimal():
    for m in MATERIALS:
        Decimal(m["unit_price"])
        assert Decimal(m["unit_price"]) > 0
    for mac in MACHINES:
        Decimal(mac["hourly_rate"])
    for a in ACTIVITIES:
        Decimal(a["driver_rate"])
    for rate in LABOR.values():
        Decimal(rate)


def test_all_quantities_positive():
    for c in COMPONENTS + PRODUCTS:
        for m in c["materials"]:
            assert Decimal(m["quantity"]) > 0
        for a in c["activities"]:
            assert Decimal(a["quantity"]) > 0
        for o in c["operations"]:
            assert Decimal(o["hours"]) > 0
        for comp in c.get("components", []):
            assert Decimal(comp["quantity"]) > 0


def test_all_references_resolve():
    for c in COMPONENTS + PRODUCTS:
        for m in c["materials"]:
            assert m["part_id"] in MATERIAL_IDS, f"missing material {m['part_id']}"
        for o in c["operations"]:
            assert o["op_id"] in OPERATION_IDS, f"missing operation {o['op_id']}"
            assert o["labor"] in LABOR_IDS, f"missing labor {o['labor']}"
            if o.get("machine"):
                assert o["machine"] in MACHINE_IDS, f"missing machine {o['machine']}"
        for a in c["activities"]:
            assert a["activity_id"] in ACTIVITY_IDS, f"missing activity {a['activity_id']}"
        for comp in c.get("components", []):
            assert comp["component_id"] in COMPONENT_IDS, f"missing component {comp['component_id']}"


def test_products_have_bill_of_materials():
    for p in PRODUCTS:
        assert p["components"] or p["materials"], f"product {p['product_id']} has empty BOM"


def test_fetcher_is_consistent():
    fetcher = CatalogFetcher()
    for node_id in NODE_IDS:
        node = fetcher.get_node(node_id)
        assert node["name"]
        for child in fetcher.get_children(node_id):
            assert child["node_id"] in NODE_IDS
        for m in fetcher.get_materials(node_id):
            assert set(m) == {"part_id", "name", "unit", "unit_price", "quantity"}
            Decimal(m["unit_price"])
        for o in fetcher.get_operations(node_id):
            assert set(o) == {"op_id", "name", "hours", "labor_rate", "machine_rate"}
            Decimal(o["labor_rate"])
            Decimal(o["machine_rate"])
        for a in fetcher.get_activities(node_id):
            assert set(a) == {"activity_id", "name", "driver_rate", "quantity"}
            Decimal(a["driver_rate"])


def test_fetcher_rejects_unknown():
    import pytest

    with pytest.raises(KeyError):
        CatalogFetcher().get_node("does-not-exist")
