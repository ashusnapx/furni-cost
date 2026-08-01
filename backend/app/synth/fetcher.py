"""BOMFetcher over the synthetic catalog — same interface as Neo4j, no I/O.

Lets rollup/tests/API run without a database; matches KG behavior exactly.
"""

from __future__ import annotations

from app.synth.catalog import (
    ACTIVITIES,
    ACTIVITY_RATES,
    COMPONENTS,
    MATERIAL_PRICES,
    OPERATION_LINES,
    PRODUCTS,
)

_BY_ID: dict[str, dict] = {}


def _all_nodes() -> dict[str, dict]:
    if not _BY_ID:
        for c in COMPONENTS:
            _BY_ID[c["component_id"]] = {**c, "type": "Component"}
        for p in PRODUCTS:
            _BY_ID[p["product_id"]] = {**p, "type": "Product"}
    return _BY_ID


class CatalogFetcher:
    """In-memory BOMFetcher backed by the synthetic catalog blueprint."""

    def get_node(self, node_id: str) -> dict:
        node = _all_nodes().get(node_id)
        if node is None:
            raise KeyError(f"unknown node: {node_id}")
        return {
            "node_id": node_id,
            "name": node["name"],
            "unit": node["unit"],
            "type": node["type"],
        }

    def get_children(self, node_id: str) -> list[dict]:
        node = _all_nodes()[node_id]
        return [{"node_id": c["component_id"], "quantity": c["quantity"]} for c in node.get("components", [])]

    def get_materials(self, node_id: str) -> list[dict]:
        node = _all_nodes()[node_id]
        out = []
        for m in node.get("materials", []):
            out.append(
                {
                    "part_id": m["part_id"],
                    "name": _material_name(m["part_id"]),
                    "unit": _material_unit(m["part_id"]),
                    "unit_price": MATERIAL_PRICES[m["part_id"]],
                    "quantity": m["quantity"],
                }
            )
        return out

    def get_operations(self, node_id: str) -> list[dict]:
        node = _all_nodes()[node_id]
        return [dict(OPERATION_LINES[o["op_id"]]) for o in node.get("operations", [])]

    def get_activities(self, node_id: str) -> list[dict]:
        node = _all_nodes()[node_id]
        out = []
        for a in node.get("activities", []):
            out.append(
                {
                    "activity_id": a["activity_id"],
                    "name": _activity_name(a["activity_id"]),
                    "driver_rate": ACTIVITY_RATES[a["activity_id"]],
                    "quantity": a["quantity"],
                }
            )
        return out

    def list_products(self) -> list[dict]:
        return [{"product_id": p["product_id"], "name": p["name"], "unit": p["unit"]} for p in PRODUCTS]


_MATERIALS: dict[str, dict] = {}


def _material_map() -> dict[str, dict]:
    if not _MATERIALS:
        from app.synth.catalog import MATERIALS

        _MATERIALS.update({m["part_id"]: m for m in MATERIALS})
    return _MATERIALS


def _material_name(part_id: str) -> str:
    return _material_map()[part_id]["name"]


def _material_unit(part_id: str) -> str:
    return _material_map()[part_id]["unit"]


_ACTIVITIES: dict[str, dict] = {}


def _activity_name(activity_id: str) -> str:
    if not _ACTIVITIES:
        _ACTIVITIES.update({a["activity_id"]: a for a in ACTIVITIES})
    return _ACTIVITIES[activity_id]["name"]
