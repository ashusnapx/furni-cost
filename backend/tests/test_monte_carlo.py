"""Monte Carlo — reproducibility, sanity bounds, centered median."""

from __future__ import annotations

from app.core.costing.abc import ActivityBasedCostingEngine
from app.core.costing.monte_carlo import SimParams, scaled_totals, simulate
from app.core.costing.rollup import rollup
from app.synth.fetcher import CatalogFetcher

BREAKDOWN = rollup("prod-dining-chair", CatalogFetcher(), ActivityBasedCostingEngine()).per_unit
POINT = float(BREAKDOWN.total)


def test_seeded_reproducibility():
    a = simulate(BREAKDOWN, runs=2000, seed=7)
    b = simulate(BREAKDOWN, runs=2000, seed=7)
    assert a == b


def test_different_seeds_differ():
    a = simulate(BREAKDOWN, runs=2000, seed=7)
    b = simulate(BREAKDOWN, runs=2000, seed=99)
    assert a["distribution"] != b["distribution"]


def test_percentile_ordering():
    dist = simulate(BREAKDOWN, runs=5000, seed=42)["distribution"]
    assert dist["p10"] <= dist["p50"] <= dist["p90"]
    assert dist["min"] <= dist["p10"]
    assert dist["p90"] <= dist["max"]


def test_median_near_point_estimate():
    dist = simulate(BREAKDOWN, runs=10000, seed=42)["distribution"]
    assert abs(dist["p50"] - POINT) / POINT < 0.02


def test_all_positive():
    dist = simulate(BREAKDOWN, runs=5000, seed=42)
    for key in ("distribution", "components"):
        stats = dist[key]
        if key == "components":
            stats = dist["components"]["materials"]
        for stat_key, val in stats.items():
            if stat_key == "std":
                continue
            assert val > 0


def test_bounds_within_perturbation():
    params = SimParams(material_price_pct=0.08, op_hours_pct=0.12, activity_qty_pct=0.15)
    dist = simulate(BREAKDOWN, runs=20000, seed=42, params=params)["distribution"]
    assert dist["min"] >= POINT * 0.85
    assert dist["max"] <= POINT * 1.15


def test_components_distribution_shape():
    dist = simulate(BREAKDOWN, runs=5000, seed=42)
    comps = dist["components"]
    assert set(comps) == {"materials", "labor", "machine", "overhead"}
    assert comps["materials"]["p50"] + comps["labor"]["p50"] + comps["machine"]["p50"] + comps["overhead"]["p50"] > 0


def test_histogram_shape():
    hist = simulate(BREAKDOWN, runs=5000, seed=42)["histogram"]
    assert len(hist) == 20
    assert sum(b["count"] for b in hist) == 5000
    assert all(b["low"] <= b["high"] for b in hist)


def test_scaled_totals():
    dist = simulate(BREAKDOWN, runs=1000, seed=1)["distribution"]
    scaled = scaled_totals({"distribution": dist}, quantity=4)
    assert scaled["p50"] == round(dist["p50"] * 4, 2)
    assert scaled["p10"] <= scaled["p50"] <= scaled["p90"]


def test_point_estimate_exposed():
    mc = simulate(BREAKDOWN, runs=100, seed=3)
    assert mc["point_estimate"] == round(POINT, 2)
    assert mc["runs"] == 100
    assert mc["seed"] == 3


def test_breakdown_empty_ok():
    from app.core.costing.abc import CostBreakdown

    dist = simulate(CostBreakdown(), runs=100, seed=1)["distribution"]
    assert dist["p50"] == 0.0
