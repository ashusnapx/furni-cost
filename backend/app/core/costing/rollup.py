"""Multi-level BOM rollup — walks the product tree, costing each node with the
deterministic ABC engine. Child unit costs become material lines of the parent.

Pure domain logic: no I/O. Data access happens through a BOMFetcher so the same
rollup works against Neo4j (prod) or the synthetic blueprint (tests/dev).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

from app.core.costing.abc import (
    ActivityBasedCostingEngine,
    CostBreakdown,
    MaterialLine,
    _dec,
)


class BOMFetcher(Protocol):
    """Data access for one cost node. Implementations: Neo4j queries, in-memory catalog."""

    def get_node(self, node_id: str) -> dict:
        """{node_id, name, unit, type} — raises KeyError when unknown."""

    def get_children(self, node_id: str) -> list[dict]:
        """[{node_id, quantity}] nested components of node."""

    def get_materials(self, node_id: str) -> list[dict]:
        """[{part_id, name, unit, unit_price, quantity}] resolved material lines."""

    def get_operations(self, node_id: str) -> list[dict]:
        """[{op_id, name, hours, labor_rate, machine_rate}] in routing order."""

    def get_activities(self, node_id: str) -> list[dict]:
        """[{activity_id, name, driver_rate, quantity}]."""


@dataclass
class CostNode:
    node_id: str
    name: str
    unit: str
    quantity: Decimal
    node_type: str
    breakdown: CostBreakdown = field(default_factory=CostBreakdown)
    children: list[CostNode] = field(default_factory=list)

    @property
    def total(self) -> Decimal:
        return self.breakdown.total

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "unit": self.unit,
            "quantity": str(self.quantity),
            "type": self.node_type,
            "total": str(self.total),
            "children": [c.to_dict() for c in self.children],
        }


class RollupResult:
    """Cost tree + aggregated per-unit breakdown for a product."""

    def __init__(self, root: CostNode):
        self.root = root
        self.per_unit = root.breakdown

    @property
    def total(self) -> Decimal:
        return self.root.total

    def scaled(self, quantity: int | Decimal) -> CostBreakdown:
        """Breakdown × order quantity — hours & driver qty scale too (rates don't)."""
        q = _dec(quantity)
        bd = self.per_unit
        scaled = CostBreakdown()
        scaled.materials = [
            type(m)(
                part_id=m.part_id,
                name=m.name,
                quantity=m.quantity * q,
                unit_price=m.unit_price,
                unit=m.unit,
            )
            for m in bd.materials
        ]
        scaled.operations = [
            type(o)(
                op_id=o.op_id,
                name=o.name,
                hours=o.hours * q,
                labor_rate=o.labor_rate,
                machine_rate=o.machine_rate,
            )
            for o in bd.operations
        ]
        scaled.activities = [
            type(a)(
                activity_id=a.activity_id,
                name=a.name,
                quantity=a.quantity * q,
                driver_rate=a.driver_rate,
            )
            for a in bd.activities
        ]
        return scaled

    def to_dict(self, quantity: int = 1) -> dict:
        q = _dec(quantity)
        scaled = self.scaled(q)
        return {
            "product_id": self.root.node_id,
            "name": self.root.name,
            "unit": self.root.unit,
            "quantity": str(q),
            "per_unit": self.per_unit.to_dict(),
            "for_quantity": scaled.to_dict(),
            "tree": self.root.to_dict(),
        }


def _line_total(breakdown: CostBreakdown) -> Decimal:
    return breakdown.total


def _own_breakdown(fetcher: BOMFetcher, node_id: str, engine: ActivityBasedCostingEngine) -> CostBreakdown:
    """Cost of a node's own materials/operations/activities (no children)."""
    return engine.estimate(
        materials=fetcher.get_materials(node_id),
        operations=fetcher.get_operations(node_id),
        activities=fetcher.get_activities(node_id),
    )


def rollup(
    root_id: str,
    fetcher: BOMFetcher,
    engine: ActivityBasedCostingEngine | None = None,
) -> RollupResult:
    """Recursively cost a product tree. Root quantity is 1 per-unit."""
    engine = engine or ActivityBasedCostingEngine()

    def walk(node_id: str, quantity: Decimal, depth: int = 0) -> CostNode:
        node = fetcher.get_node(node_id)
        breakdown = _own_breakdown(fetcher, node_id, engine)
        cost_node = CostNode(
            node_id=node["node_id"],
            name=node["name"],
            unit=node["unit"],
            quantity=quantity,
            node_type=node["type"],
            breakdown=breakdown,
        )

        for child in fetcher.get_children(node_id):
            child_node = walk(child["node_id"], _dec(child["quantity"]), depth + 1)
            cost_node.children.append(child_node)
            # Child's fully-laden per-unit cost becomes a material line of parent.
            unit_cost = _line_total(child_node.breakdown).quantize(Decimal("0.01"), ROUND_HALF_UP)
            breakdown.materials.append(
                MaterialLine(
                    part_id=child_node.node_id,
                    name=child_node.name,
                    quantity=child_node.quantity,
                    unit_price=unit_cost,
                    unit=child_node.unit,
                )
            )

        return cost_node

    return RollupResult(walk(root_id, Decimal(1)))
