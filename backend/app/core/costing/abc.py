"""Activity-Based Costing (ABC) engine — deterministic source of truth.

Cost structure (furniture):
    total = materials + labor + machine + overhead

    materials = Σ BOM qty × unit_price
    labor     = Σ operation time × labor rate
    machine   = Σ operation time × machine rate
    overhead  = Σ activity qty × driver rate   (ABC: cost pools → activities → drivers)

M1 expands: multi-level BOM rollup from Neo4j, Monte Carlo scenario simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal


def _dec(value: str | float | Decimal) -> Decimal:
    """Coerce to Decimal — engine inputs arrive as JSON strings from APIs."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


@dataclass(frozen=True)
class MaterialLine:
    part_id: str
    name: str
    quantity: Decimal
    unit_price: Decimal
    unit: str = "pcs"

    @property
    def amount(self) -> Decimal:
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"), ROUND_HALF_UP)


@dataclass(frozen=True)
class OperationLine:
    op_id: str
    name: str
    hours: Decimal
    labor_rate: Decimal
    machine_rate: Decimal = Decimal(0)

    @property
    def labor_amount(self) -> Decimal:
        return (self.hours * self.labor_rate).quantize(Decimal("0.01"), ROUND_HALF_UP)

    @property
    def machine_amount(self) -> Decimal:
        return (self.hours * self.machine_rate).quantize(Decimal("0.01"), ROUND_HALF_UP)


@dataclass(frozen=True)
class ActivityLine:
    activity_id: str
    name: str
    quantity: Decimal
    driver_rate: Decimal

    @property
    def amount(self) -> Decimal:
        return (self.quantity * self.driver_rate).quantize(Decimal("0.01"), ROUND_HALF_UP)


@dataclass
class CostBreakdown:
    materials: list[MaterialLine] = field(default_factory=list)
    operations: list[OperationLine] = field(default_factory=list)
    activities: list[ActivityLine] = field(default_factory=list)

    @property
    def material_total(self) -> Decimal:
        return sum((l.amount for l in self.materials), Decimal(0))

    @property
    def labor_total(self) -> Decimal:
        return sum((l.labor_amount for l in self.operations), Decimal(0))

    @property
    def machine_total(self) -> Decimal:
        return sum((l.machine_amount for l in self.operations), Decimal(0))

    @property
    def overhead_total(self) -> Decimal:
        return sum((l.amount for l in self.activities), Decimal(0))

    @property
    def total(self) -> Decimal:
        return self.material_total + self.labor_total + self.machine_total + self.overhead_total

    def to_dict(self) -> dict:
        return {
            "materials": [m.__dict__ | {"amount": str(m.amount)} for m in self.materials],
            "operations": [
                o.__dict__
                | {"labor_amount": str(o.labor_amount), "machine_amount": str(o.machine_amount)}
                for o in self.operations
            ],
            "activities": [a.__dict__ | {"amount": str(a.amount)} for a in self.activities],
            "totals": {
                "materials": str(self.material_total),
                "labor": str(self.labor_total),
                "machine": str(self.machine_total),
                "overhead": str(self.overhead_total),
                "total": str(self.total),
            },
        }


class ActivityBasedCostingEngine:
    """Pure function cost engine. No I/O, no LLM — trivially testable."""

    def estimate(
        self,
        materials: list[dict],
        operations: list[dict],
        activities: list[dict] | None = None,
    ) -> CostBreakdown:
        return CostBreakdown(
            materials=[
                MaterialLine(
                    part_id=m["part_id"],
                    name=m["name"],
                    quantity=_dec(m["quantity"]),
                    unit_price=_dec(m["unit_price"]),
                    unit=m.get("unit", "pcs"),
                )
                for m in materials
            ],
            operations=[
                OperationLine(
                    op_id=o["op_id"],
                    name=o["name"],
                    hours=_dec(o["hours"]),
                    labor_rate=_dec(o["labor_rate"]),
                    machine_rate=_dec(o.get("machine_rate", 0)),
                )
                for o in operations
            ],
            activities=[
                ActivityLine(
                    activity_id=a["activity_id"],
                    name=a["name"],
                    quantity=_dec(a["quantity"]),
                    driver_rate=_dec(a["driver_rate"]),
                )
                for a in (activities or [])
            ],
        )
