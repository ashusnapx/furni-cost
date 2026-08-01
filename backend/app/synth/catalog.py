"""Deterministic synthetic furniture factory blueprint (EUR).

Every price/rate is a plain string — money enters the engine as Decimal.
No randomness here: variance belongs to Monte Carlo, not the catalog.
All data is fictional; nothing here is real financial data (Gemini free-tier rule).
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Materials  (part_id, name, unit, unit_price EUR)
# --------------------------------------------------------------------------
MATERIALS: list[dict] = [
    {"part_id": "mat-oak-lumber", "name": "European oak lumber", "unit": "m3", "unit_price": "1250.00"},
    {"part_id": "mat-oak-veneer", "name": "Oak veneer sheet", "unit": "m2", "unit_price": "18.50"},
    {"part_id": "mat-plywood", "name": "Birch plywood 18mm", "unit": "sheet", "unit_price": "42.00"},
    {"part_id": "mat-mdf", "name": "MDF panel 16mm", "unit": "sheet", "unit_price": "31.50"},
    {"part_id": "mat-foam-hr", "name": "High-resilience foam", "unit": "m3", "unit_price": "980.00"},
    {"part_id": "mat-foam-lr", "name": "Low-resilience foam", "unit": "m3", "unit_price": "640.00"},
    {"part_id": "mat-fabric", "name": "Upholstery fabric", "unit": "m", "unit_price": "24.00"},
    {"part_id": "mat-leather", "name": "Aniline leather", "unit": "m2", "unit_price": "85.00"},
    {"part_id": "mat-wood-glue", "name": "PVA wood glue", "unit": "kg", "unit_price": "6.80"},
    {"part_id": "mat-oil-finish", "name": "Hardwax oil finish", "unit": "L", "unit_price": "38.00"},
    {"part_id": "mat-varnish", "name": "PU varnish", "unit": "L", "unit_price": "26.00"},
    {"part_id": "mat-hinge", "name": "Concealed hinge", "unit": "pcs", "unit_price": "3.20"},
    {"part_id": "mat-drawer-slide", "name": "Drawer slide 450mm", "unit": "pcs", "unit_price": "7.50"},
    {"part_id": "mat-screw-kit", "name": "Screw & dowel kit", "unit": "kit", "unit_price": "1.10"},
    {"part_id": "mat-packaging", "name": "Corner-protected carton", "unit": "pcs", "unit_price": "4.60"},
]

# --------------------------------------------------------------------------
# Machines  (machine_id, name, hourly machine rate EUR)
# --------------------------------------------------------------------------
MACHINES: list[dict] = [
    {"machine_id": "mac-cnc", "name": "5-axis CNC router", "hourly_rate": "85.00"},
    {"machine_id": "mac-panel-saw", "name": "Panel saw", "hourly_rate": "70.00"},
    {"machine_id": "mac-edge-bander", "name": "Edge bander", "hourly_rate": "60.00"},
    {"machine_id": "mac-spray-booth", "name": "Spray booth", "hourly_rate": "75.00"},
    {"machine_id": "mac-sewing", "name": "Industrial sewing", "hourly_rate": "30.00"},
    {"machine_id": "mac-sanding", "name": "Wide-belt sander", "hourly_rate": "55.00"},
]

# --------------------------------------------------------------------------
# Labor skill classes (rate EUR/h)
# --------------------------------------------------------------------------
LABOR: dict[str, str] = {
    "machinist": "38.00",
    "assembler": "32.00",
    "upholsterer": "35.00",
    "finisher": "36.00",
    "packer": "26.00",
    "sewer": "28.00",
}

# --------------------------------------------------------------------------
# ABC overhead cost pools → activities (driver unit, driver rate EUR)
# --------------------------------------------------------------------------
ACTIVITIES: list[dict] = [
    {"activity_id": "act-setup", "name": "Machine setup", "driver": "setup event", "driver_rate": "45.00"},
    {"activity_id": "act-qc", "name": "Quality inspection", "driver": "inspection", "driver_rate": "2.40"},
    {"activity_id": "act-energy", "name": "Energy consumption", "driver": "kWh", "driver_rate": "0.14"},
    {"activity_id": "act-warehouse", "name": "Warehousing", "driver": "unit-day", "driver_rate": "0.32"},
    {"activity_id": "act-maintenance", "name": "Machine maintenance", "driver": "machine-hour", "driver_rate": "6.50"},
    {"activity_id": "act-waste", "name": "Waste & scrap disposal", "driver": "kg", "driver_rate": "0.38"},
    {"activity_id": "act-procurement", "name": "Procurement & inbound", "driver": "purchase order", "driver_rate": "18.00"},
]

# --------------------------------------------------------------------------
# Operations (op_id, name, hours, labor class, optional machine)
# --------------------------------------------------------------------------
OPS_CUT = {"op_id": "op-cut", "name": "Cross-cut & rip", "hours": "0.09", "labor": "machinist", "machine": "mac-panel-saw"}
OPS_CNC = {"op_id": "op-cnc", "name": "CNC shaping", "hours": "0.12", "labor": "machinist", "machine": "mac-cnc"}
OPS_SAND = {"op_id": "op-sand", "name": "Sand & prep", "hours": "0.07", "labor": "finisher", "machine": "mac-sanding"}
OPS_EDGE = {"op_id": "op-edge", "name": "Edge banding", "hours": "0.05", "labor": "machinist", "machine": "mac-edge-bander"}
OPS_FINISH = {"op_id": "op-finish", "name": "Spray finish", "hours": "0.10", "labor": "finisher", "machine": "mac-spray-booth"}
OPS_CNC_TURN = {"op_id": "op-cnc-turn", "name": "CNC turning", "hours": "0.08", "labor": "machinist", "machine": "mac-cnc"}
OPS_CUT_FABRIC = {"op_id": "op-cut-fabric", "name": "Fabric cutting", "hours": "0.05", "labor": "sewer", "machine": "mac-sewing"}
OPS_SEW = {"op_id": "op-sew", "name": "Sewing & piping", "hours": "0.20", "labor": "sewer", "machine": "mac-sewing"}
OPS_FOAM = {"op_id": "op-foam", "name": "Foam shaping", "hours": "0.10", "labor": "upholsterer"}
OPS_ASSEMBLE = {"op_id": "op-assemble", "name": "Assembly", "hours": "0.25", "labor": "assembler"}
OPS_PACK = {"op_id": "op-pack", "name": "Pack & crate", "hours": "0.06", "labor": "packer"}
OPS_UPHOLSTER = {"op_id": "op-upholster", "name": "Upholstering", "hours": "0.45", "labor": "upholsterer"}
OPS_BORING = {"op_id": "op-boring", "name": "Boring & dowel drill", "hours": "0.04", "labor": "machinist", "machine": "mac-cnc"}
OPS_EDGE_2 = {"op_id": "op-edge-2", "name": "Edge banding (2 edges)", "hours": "0.07", "labor": "machinist", "machine": "mac-edge-bander"}
OPS_SPRAY_PANEL = {"op_id": "op-spray-panel", "name": "Panel spray", "hours": "0.08", "labor": "finisher", "machine": "mac-spray-booth"}

# --------------------------------------------------------------------------
# Standard activities consumed per component/assembly
#   (activity_id, quantity) — driver qty
# --------------------------------------------------------------------------
ACT_SETUP_1 = {"activity_id": "act-setup", "quantity": "1"}
ACT_QC_1 = {"activity_id": "act-qc", "quantity": "1"}
ACT_QC_2 = {"activity_id": "act-qc", "quantity": "2"}
ACT_ENERGY_1 = {"activity_id": "act-energy", "quantity": "1.5"}
ACT_ENERGY_2 = {"activity_id": "act-energy", "quantity": "3.0"}
ACT_MAINT_1 = {"activity_id": "act-maintenance", "quantity": "0.4"}
ACT_WAREHOUSE_1 = {"activity_id": "act-warehouse", "quantity": "1"}
ACT_WASTE_1 = {"activity_id": "act-waste", "quantity": "0.6"}
ACT_PROC_1 = {"activity_id": "act-procurement", "quantity": "0.5"}

# --------------------------------------------------------------------------
# Components (component_id, name, unit, materials, operations, activities)
# --------------------------------------------------------------------------
COMPONENTS: list[dict] = [
    {
        "component_id": "comp-chair-frame",
        "name": "Chair frame",
        "unit": "pcs",
        "materials": [
            {"part_id": "mat-oak-lumber", "quantity": "0.022"},
            {"part_id": "mat-wood-glue", "quantity": "0.05"},
        ],
        "operations": [OPS_CUT, OPS_CNC, OPS_SAND, OPS_FINISH],
        "activities": [ACT_SETUP_1, ACT_QC_1, ACT_ENERGY_2, ACT_MAINT_1, ACT_WASTE_1],
    },
    {
        "component_id": "comp-chair-leg",
        "name": "Chair leg (turned)",
        "unit": "pcs",
        "materials": [
            {"part_id": "mat-oak-lumber", "quantity": "0.003"},
            {"part_id": "mat-oil-finish", "quantity": "0.02"},
        ],
        "operations": [OPS_CNC_TURN, OPS_SAND],
        "activities": [ACT_QC_1, ACT_ENERGY_1, ACT_WASTE_1],
    },
    {
        "component_id": "comp-chair-seat",
        "name": "Chair seat (moulded)",
        "unit": "pcs",
        "materials": [
            {"part_id": "mat-plywood", "quantity": "0.5"},
            {"part_id": "mat-foam-lr", "quantity": "0.004"},
            {"part_id": "mat-fabric", "quantity": "0.35"},
        ],
        "operations": [OPS_CUT, OPS_EDGE, OPS_CUT_FABRIC, OPS_SEW],
        "activities": [ACT_QC_1, ACT_ENERGY_2, ACT_MAINT_1],
    },
    {
        "component_id": "comp-sofa-frame",
        "name": "Sofa frame (3-seat)",
        "unit": "pcs",
        "materials": [
            {"part_id": "mat-oak-lumber", "quantity": "0.09"},
            {"part_id": "mat-plywood", "quantity": "1.5"},
            {"part_id": "mat-wood-glue", "quantity": "0.15"},
        ],
        "operations": [OPS_CUT, OPS_CNC, OPS_BORING, OPS_SAND, OPS_EDGE_2],
        "activities": [ACT_SETUP_1, ACT_QC_2, ACT_ENERGY_2, ACT_MAINT_1, ACT_WASTE_1],
    },
    {
        "component_id": "comp-sofa-cushion",
        "name": "Sofa seat cushion",
        "unit": "pcs",
        "materials": [
            {"part_id": "mat-foam-hr", "quantity": "0.03"},
            {"part_id": "mat-fabric", "quantity": "0.8"},
        ],
        "operations": [OPS_FOAM, OPS_CUT_FABRIC, OPS_SEW],
        "activities": [ACT_QC_1, ACT_ENERGY_1],
    },
    {
        "component_id": "comp-sofa-back",
        "name": "Sofa backrest",
        "unit": "pcs",
        "materials": [
            {"part_id": "mat-foam-hr", "quantity": "0.022"},
            {"part_id": "mat-fabric", "quantity": "0.9"},
        ],
        "operations": [OPS_FOAM, OPS_CUT_FABRIC, OPS_SEW],
        "activities": [ACT_QC_1, ACT_ENERGY_1],
    },
    {
        "component_id": "comp-table-top",
        "name": "Coffee table top",
        "unit": "pcs",
        "materials": [
            {"part_id": "mat-oak-lumber", "quantity": "0.035"},
            {"part_id": "mat-oak-veneer", "quantity": "0.8"},
            {"part_id": "mat-oil-finish", "quantity": "0.06"},
        ],
        "operations": [OPS_CUT, OPS_CNC, OPS_SAND, OPS_FINISH],
        "activities": [ACT_SETUP_1, ACT_QC_2, ACT_ENERGY_2, ACT_MAINT_1, ACT_WASTE_1],
    },
    {
        "component_id": "comp-cabinet-side",
        "name": "Wardrobe side panel",
        "unit": "pcs",
        "materials": [
            {"part_id": "mat-mdf", "quantity": "0.5"},
            {"part_id": "mat-oak-veneer", "quantity": "1.1"},
            {"part_id": "mat-wood-glue", "quantity": "0.08"},
        ],
        "operations": [OPS_CUT, OPS_EDGE_2, OPS_SPRAY_PANEL],
        "activities": [ACT_QC_1, ACT_ENERGY_1, ACT_WASTE_1],
    },
    {
        "component_id": "comp-cabinet-door",
        "name": "Wardrobe door",
        "unit": "pcs",
        "materials": [
            {"part_id": "mat-mdf", "quantity": "0.4"},
            {"part_id": "mat-oak-veneer", "quantity": "0.9"},
            {"part_id": "mat-hinge", "quantity": "2"},
            {"part_id": "mat-wood-glue", "quantity": "0.06"},
        ],
        "operations": [OPS_CUT, OPS_BORING, OPS_EDGE_2, OPS_SPRAY_PANEL],
        "activities": [ACT_QC_1, ACT_ENERGY_2],
    },
]

# --------------------------------------------------------------------------
# Products: (product_id, name, unit, components w/ qty, own materials/ops/activities)
# --------------------------------------------------------------------------
PRODUCTS: list[dict] = [
    {
        "product_id": "prod-dining-chair",
        "name": "Dining chair Oslo",
        "unit": "pcs",
        "components": [
            {"component_id": "comp-chair-frame", "quantity": "1"},
            {"component_id": "comp-chair-seat", "quantity": "1"},
            {"component_id": "comp-chair-leg", "quantity": "4"},
        ],
        "materials": [{"part_id": "mat-screw-kit", "quantity": "1"}],
        "operations": [OPS_ASSEMBLE, OPS_PACK],
        "activities": [ACT_QC_1, ACT_ENERGY_1, ACT_WAREHOUSE_1, ACT_PROC_1],
    },
    {
        "product_id": "prod-sofa-3seat",
        "name": "3-seat sofa Malmö",
        "unit": "pcs",
        "components": [
            {"component_id": "comp-sofa-frame", "quantity": "1"},
            {"component_id": "comp-sofa-cushion", "quantity": "2"},
            {"component_id": "comp-sofa-back", "quantity": "2"},
        ],
        "materials": [
            {"part_id": "mat-screw-kit", "quantity": "2"},
            {"part_id": "mat-fabric", "quantity": "1.2"},
        ],
        "operations": [OPS_UPHOLSTER, OPS_ASSEMBLE, OPS_PACK],
        "activities": [ACT_QC_2, ACT_ENERGY_2, ACT_WAREHOUSE_1, ACT_PROC_1],
    },
    {
        "product_id": "prod-coffee-table",
        "name": "Coffee table Åre",
        "unit": "pcs",
        "components": [
            {"component_id": "comp-table-top", "quantity": "1"},
            {"component_id": "comp-chair-leg", "quantity": "4"},
        ],
        "materials": [{"part_id": "mat-screw-kit", "quantity": "1"}],
        "operations": [OPS_ASSEMBLE, OPS_PACK],
        "activities": [ACT_QC_1, ACT_ENERGY_1, ACT_WAREHOUSE_1, ACT_PROC_1],
    },
    {
        "product_id": "prod-wardrobe",
        "name": "Wardrobe Fjäll 2-door",
        "unit": "pcs",
        "components": [
            {"component_id": "comp-cabinet-side", "quantity": "2"},
            {"component_id": "comp-cabinet-door", "quantity": "2"},
        ],
        "materials": [
            {"part_id": "mat-mdf", "quantity": "2"},
            {"part_id": "mat-oak-veneer", "quantity": "2.5"},
            {"part_id": "mat-drawer-slide", "quantity": "2"},
            {"part_id": "mat-screw-kit", "quantity": "3"},
        ],
        "operations": [OPS_ASSEMBLE, OPS_PACK],
        "activities": [ACT_QC_2, ACT_ENERGY_2, ACT_WAREHOUSE_1, ACT_PROC_1],
    },
]


def labor_rate(skill: str) -> str:
    return LABOR[skill]


def resolve_operation(op: dict) -> dict:
    """Expand an operation definition into engine-ready line (labor + machine rates)."""
    return {
        "op_id": op["op_id"],
        "name": op["name"],
        "hours": op["hours"],
        "labor_rate": labor_rate(op["labor"]),
        "machine_rate": MACHINE_RATES.get(op.get("machine", ""), "0.00"),
    }


MACHINE_RATES: dict[str, str] = {m["machine_id"]: m["hourly_rate"] for m in MACHINES}

# Convenience: operation lines resolved to engine shape.
OPERATION_LINES: dict[str, dict] = {
    key: resolve_operation(op)
    for key, op in {
        **{o["op_id"]: o for o in [OPS_CUT, OPS_CNC, OPS_SAND, OPS_EDGE, OPS_FINISH, OPS_CNC_TURN,
                                   OPS_CUT_FABRIC, OPS_SEW, OPS_FOAM, OPS_ASSEMBLE, OPS_PACK,
                                   OPS_UPHOLSTER, OPS_BORING, OPS_EDGE_2, OPS_SPRAY_PANEL]},
    }.items()
}

ACTIVITY_RATES: dict[str, str] = {a["activity_id"]: a["driver_rate"] for a in ACTIVITIES}
MATERIAL_PRICES: dict[str, str] = {m["part_id"]: m["unit_price"] for m in MATERIALS}
