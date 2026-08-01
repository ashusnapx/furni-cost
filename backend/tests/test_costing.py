from decimal import Decimal

from app.core.costing.abc import ActivityBasedCostingEngine

ENGINE = ActivityBasedCostingEngine()


def test_material_total() -> None:
    bd = ENGINE.estimate(
        materials=[
            {"part_id": "P1", "name": "MDF 18mm sheet", "quantity": 2, "unit_price": "42.50"},
            {"part_id": "P2", "name": "Beech dowel set", "quantity": 8, "unit_price": "0.75"},
        ],
        operations=[],
    )
    assert bd.material_total == Decimal("91.00")


def test_labor_and_machine() -> None:
    bd = ENGINE.estimate(
        materials=[],
        operations=[
            {
                "op_id": "O1",
                "name": "CNC panel cut",
                "hours": "1.5",
                "labor_rate": "28.00",
                "machine_rate": "45.00",
            }
        ],
    )
    assert bd.labor_total == Decimal("42.00")
    assert bd.machine_total == Decimal("67.50")


def test_overhead_abc() -> None:
    bd = ENGINE.estimate(
        materials=[],
        operations=[],
        activities=[
            {"activity_id": "A1", "name": "Machine setups", "quantity": 3, "driver_rate": "120.00"},
        ],
    )
    assert bd.overhead_total == Decimal("360.00")


def test_total_rollup() -> None:
    bd = ENGINE.estimate(
        materials=[{"part_id": "P1", "name": "MDF", "quantity": 2, "unit_price": "42.50"}],
        operations=[
            {"op_id": "O1", "name": "CNC", "hours": "1.5", "labor_rate": "28.00", "machine_rate": "45.00"}
        ],
        activities=[{"activity_id": "A1", "name": "Setups", "quantity": 3, "driver_rate": "120.00"}],
    )
    assert bd.total == Decimal("554.50")


def test_to_dict_shape() -> None:
    bd = ENGINE.estimate(
        materials=[{"part_id": "P1", "name": "MDF", "quantity": 1, "unit_price": "10.00"}],
        operations=[],
    )
    d = bd.to_dict()
    assert d["totals"]["total"] == "10.00"
    assert len(d["materials"]) == 1
