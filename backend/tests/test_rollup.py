"""Multi-level rollup — golden totals + flat-expansion reference check."""

from __future__ import annotations

from decimal import Decimal

from app.core.costing.abc import ActivityBasedCostingEngine
from app.core.costing.rollup import rollup
from app.synth.catalog import (
    ACTIVITY_RATES,
    COMPONENTS,
    MATERIAL_PRICES,
    OPERATION_LINES,
    PRODUCTS,
)
from app.synth.fetcher import CatalogFetcher

ENGINE = ActivityBasedCostingEngine()
FETCHER = CatalogFetcher()

# Golden values computed by hand from catalog constants (EUR).
CHAIR_UNIT_TOTAL = Decimal("303.77")


def _flat_reference(product_id: str) -> Decimal:
    """Independent reference: expand every component ×qty into flat engine lines.

    Mirrors rollup's costing policy: each component's fully-laden per-unit cost
    is quantized to cent before quantity scaling (batch rounding).
    """
    from decimal import ROUND_HALF_UP

    product = next(p for p in PRODUCTS if p["product_id"] == product_id)
    mats, ops, acts = [], [], []
    for c in product["components"]:
        comp = next(x for x in COMPONENTS if x["component_id"] == c["component_id"])
        comp_mats = [dict(m) | {"name": m["part_id"], "unit_price": MATERIAL_PRICES[m["part_id"]]} for m in comp["materials"]]
        comp_ops = [dict(OPERATION_LINES[o["op_id"]]) for o in comp["operations"]]
        comp_acts = [dict(a) | {"name": a["activity_id"], "driver_rate": ACTIVITY_RATES[a["activity_id"]]} for a in comp["activities"]]
        unit_cost = ENGINE.estimate(comp_mats, comp_ops, comp_acts).total
        unit_cost = unit_cost.quantize(Decimal("0.01"), ROUND_HALF_UP)
        mats.append({"part_id": comp["component_id"], "name": comp["name"],
                     "quantity": c["quantity"], "unit_price": str(unit_cost)})
    for m in product["materials"]:
        mats.append({"part_id": m["part_id"], "name": m["part_id"], "quantity": m["quantity"],
                     "unit_price": MATERIAL_PRICES[m["part_id"]]})
    for o in product["operations"]:
        line = OPERATION_LINES[o["op_id"]]
        ops.append({"op_id": line["op_id"], "name": line["name"], "hours": line["hours"],
                    "labor_rate": line["labor_rate"], "machine_rate": line["machine_rate"]})
    for a in product["activities"]:
        acts.append({"activity_id": a["activity_id"], "name": a["activity_id"], "quantity": a["quantity"],
                     "driver_rate": ACTIVITY_RATES[a["activity_id"]]})
    return ENGINE.estimate(mats, ops, acts).total


def test_chair_golden_total():
    result = rollup("prod-dining-chair", FETCHER, ENGINE)
    assert result.total == CHAIR_UNIT_TOTAL


def test_chair_matches_flat_reference():
    assert _flat_reference("prod-dining-chair") == CHAIR_UNIT_TOTAL
    assert rollup("prod-dining-chair", FETCHER, ENGINE).total == _flat_reference("prod-dining-chair")


def test_all_products_match_flat_reference():
    for p in PRODUCTS:
        assert rollup(p["product_id"], FETCHER, ENGINE).total == _flat_reference(p["product_id"]), p["product_id"]


def test_leg_quantity_multiplied():
    root = rollup("prod-dining-chair", FETCHER, ENGINE).root
    leg_line = next(m for m in root.breakdown.materials if m.part_id == "comp-chair-leg")
    assert leg_line.quantity == Decimal(4)
    assert leg_line.amount == Decimal("94.24")  # 4 × 23.56


def test_child_unit_costs_become_parent_material_lines():
    root = rollup("prod-dining-chair", FETCHER, ENGINE).root
    parts = {m.part_id: m for m in root.breakdown.materials}
    assert parts["comp-chair-frame"].unit_price == Decimal("120.44")
    assert parts["comp-chair-seat"].unit_price == Decimal("66.50")


def test_sofa_costlier_than_chair():
    assert rollup("prod-sofa-3seat", FETCHER, ENGINE).total > rollup("prod-dining-chair", FETCHER, ENGINE).total


def test_quantity_scaling():
    result = rollup("prod-dining-chair", FETCHER, ENGINE)
    payload = result.to_dict(quantity=3)
    assert payload["for_quantity"]["totals"]["total"] == str(CHAIR_UNIT_TOTAL * 3)
    assert payload["per_unit"]["totals"]["total"] == str(CHAIR_UNIT_TOTAL)


def test_tree_shape():
    root = rollup("prod-wardrobe", FETCHER, ENGINE).root
    assert len(root.children) == 2
    assert {c.node_id for c in root.children} == {"comp-cabinet-side", "comp-cabinet-door"}
    side = next(c for c in root.children if c.node_id == "comp-cabinet-side")
    assert side.quantity == Decimal(2)
