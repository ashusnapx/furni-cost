"""Monte Carlo simulation over a CostBreakdown.

Perturbation model (per line, independent, uniform in ±pct):
    material unit price  ±8%
    operation hours      ±12%
    activity driver qty  ±15%

Float math internally (sampling), 2dp rounding on output. The deterministic
ABC result stays the source of truth — MC only reports a distribution around it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.core.costing.abc import CostBreakdown


@dataclass(frozen=True)
class SimParams:
    material_price_pct: float = 0.08
    op_hours_pct: float = 0.12
    activity_qty_pct: float = 0.15


_PERCENTILES = (10.0, 50.0, 90.0)


def _round2(x: float) -> float:
    return round(float(x), 2)


def _percentile_stats(samples: np.ndarray) -> dict:
    p10, p50, p90 = np.percentile(samples, _PERCENTILES)
    return {
        "p10": _round2(p10),
        "p50": _round2(p50),
        "p90": _round2(p90),
        "mean": _round2(samples.mean()),
        "std": _round2(samples.std()),
        "min": _round2(samples.min()),
        "max": _round2(samples.max()),
    }


def simulate(
    breakdown: CostBreakdown,
    runs: int = 5000,
    seed: int = 42,
    params: SimParams | None = None,
) -> dict:
    """Returns distribution dict; deterministic for a given (runs, seed)."""
    params = params or SimParams()
    rng = np.random.default_rng(seed)

    mat_price = np.array([float(m.unit_price) for m in breakdown.materials])
    op_hours = np.array([float(o.hours) for o in breakdown.operations])
    act_qty = np.array([float(a.quantity) for a in breakdown.activities])
    labor_rate = np.array([float(o.labor_rate) for o in breakdown.operations])
    machine_rate = np.array([float(o.machine_rate) for o in breakdown.operations])

    n_mat, n_op, n_act = len(mat_price), len(op_hours), len(act_qty)

    def mult(n: int, pct: float) -> np.ndarray:
        return 1.0 + rng.uniform(-pct, pct, size=(runs, n))

    mat_mult = mult(n_mat, params.material_price_pct) if n_mat else None
    op_mult = mult(n_op, params.op_hours_pct) if n_op else None
    act_mult = mult(n_act, params.activity_qty_pct) if n_act else None

    mat_amounts = np.array([float(m.amount) for m in breakdown.materials])
    mat_totals = (mat_amounts * mat_mult).sum(axis=1) if mat_mult is not None else np.zeros(runs)

    labor_totals = (op_hours * labor_rate * op_mult).sum(axis=1) if op_mult is not None else np.zeros(runs)
    machine_totals = (op_hours * machine_rate * op_mult).sum(axis=1) if op_mult is not None else np.zeros(runs)

    act_amounts = np.array([float(a.amount) for a in breakdown.activities])
    overhead_totals = (act_amounts * act_mult).sum(axis=1) if act_mult is not None else np.zeros(runs)

    totals = mat_totals + labor_totals + machine_totals + overhead_totals

    hist_counts, hist_edges = np.histogram(totals, bins=20)
    bins = [
        {"low": _round2(hist_edges[i]), "high": _round2(hist_edges[i + 1]), "count": int(c)}
        for i, c in enumerate(hist_counts)
    ]

    return {
        "runs": runs,
        "seed": seed,
        "params": {
            "material_price_pct": params.material_price_pct,
            "op_hours_pct": params.op_hours_pct,
            "activity_qty_pct": params.activity_qty_pct,
        },
        "point_estimate": _round2(float(breakdown.total)),
        "distribution": _percentile_stats(totals),
        "components": {
            "materials": _percentile_stats(mat_totals),
            "labor": _percentile_stats(labor_totals),
            "machine": _percentile_stats(machine_totals),
            "overhead": _percentile_stats(overhead_totals),
        },
        "histogram": bins,
    }


def scaled_totals(distribution: dict, quantity: int) -> dict:
    """Multiply distribution stats by order quantity (mean/std scale linearly)."""
    scaled = dict(distribution["distribution"])
    for key in ("p10", "p50", "p90", "mean", "min", "max"):
        scaled[key] = _round2(scaled[key] * quantity)
    scaled["std"] = _round2(scaled["std"] * quantity)
    return scaled
