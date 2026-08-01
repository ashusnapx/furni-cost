"""Load the synthetic catalog into Neo4j (idempotent: purge + upsert)."""

from __future__ import annotations

from neo4j import Driver

from app.kg.schema import (
    ACTIVITY,
    COMPONENT,
    CONSUMES,
    CONTAINS,
    MACHINE,
    MATERIAL,
    OPERATION,
    PERFORMED_ON,
    PRODUCT,
    REQUIRES,
    USES_MATERIAL,
)
from app.synth.catalog import (
    ACTIVITIES,
    COMPONENTS,
    MACHINES,
    MATERIALS,
    OPERATION_LINES,
    PRODUCTS,
)

CONSTRAINT_QUERIES = [
    f"CREATE CONSTRAINT {label.lower()}_id IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
    for label, prop in [
        (MATERIAL, "part_id"),
        (MACHINE, "machine_id"),
        (OPERATION, "op_id"),
        (ACTIVITY, "activity_id"),
        (COMPONENT, "component_id"),
        (PRODUCT, "product_id"),
    ]
]


def _batch(rows: list[dict], size: int = 100) -> list[list[dict]]:
    rows = list(rows)
    return [rows[i : i + size] for i in range(0, len(rows), size)]


def _scalar(row: dict) -> dict:
    """Neo4j property values must be primitives — drop nested (ops/materials...)."""
    primitives = (str, int, float, bool)
    return {k: v for k, v in row.items() if v is None or isinstance(v, primitives)}


def purge(driver: Driver, database: str) -> None:
    driver.execute_query(
        f"MATCH (n:{MATERIAL}|{MACHINE}|{OPERATION}|{ACTIVITY}|{COMPONENT}|{PRODUCT}) "
        "DETACH DELETE n",
        database_=database,
    )


def load_catalog(driver: Driver, database: str) -> dict[str, int]:
    """Purge and load the synthetic catalog. Returns node/rel counts."""
    for q in CONSTRAINT_QUERIES:
        driver.execute_query(q, database_=database)
    purge(driver, database)

    with driver.session(database=database) as session:
        # --- nodes ---------------------------------------------------------
        def upsert(rows: list[dict], label: str) -> None:
            id_prop = _id_prop(label)
            for chunk in _batch(rows):
                session.run(
                    f"UNWIND $rows AS r MERGE (n:{label} {{{id_prop}: r.{id_prop}}}) SET n = r",
                    rows=[_scalar(r) for r in chunk],
                ).consume()

        upsert(MATERIALS, MATERIAL)
        upsert(MACHINES, MACHINE)
        upsert(ACTIVITIES, ACTIVITY)
        upsert(OPERATION_LINES.values(), OPERATION)
        upsert([{**c, "type": COMPONENT} for c in COMPONENTS], COMPONENT)
        upsert([{**p, "type": PRODUCT} for p in PRODUCTS], PRODUCT)

        # --- relationships -------------------------------------------------
        def rel_batch(query: str, rows: list[dict]) -> None:
            for chunk in _batch(rows):
                session.run(query, rows=chunk).consume()

        # CONTAINS (product/component → component)
        contains = []
        for p in PRODUCTS:
            for c in p["components"]:
                contains.append(
                    {"parent": p["product_id"], "child": c["component_id"], "quantity": c["quantity"]}
                )
        rel_batch(
            "UNWIND $rows AS r "
            f"MATCH (p:{PRODUCT}|{COMPONENT}) "
            "WHERE (p:Product AND p.product_id = r.parent) OR (p:Component AND p.component_id = r.parent) "
            f"MATCH (c:{COMPONENT}) WHERE c.component_id = r.child "
            f"MERGE (p)-[:{CONTAINS} {{quantity: r.quantity}}]->(c)",
            contains,
        )

        # USES_MATERIAL (product/component → material)
        uses = []
        for p in PRODUCTS + COMPONENTS:
            nid_key = "product_id" if p.get("product_id") else "component_id"
            nid = p[nid_key]
            for i, m in enumerate(p["materials"]):
                uses.append({"parent": nid, "part": m["part_id"], "quantity": m["quantity"], "seq": i})
        rel_batch(
            "UNWIND $rows AS r "
            f"MATCH (p:{PRODUCT}|{COMPONENT}) "
            "WHERE (p:Product AND p.product_id = r.parent) OR (p:Component AND p.component_id = r.parent) "
            f"MATCH (m:{MATERIAL}) WHERE m.part_id = r.part "
            f"MERGE (p)-[:{USES_MATERIAL} {{quantity: r.quantity, sequence: r.seq}}]->(m)",
            uses,
        )

        # REQUIRES (product/component → operation)
        requires = []
        for p in PRODUCTS + COMPONENTS:
            nid_key = "product_id" if p.get("product_id") else "component_id"
            nid = p[nid_key]
            for i, op in enumerate(p["operations"]):
                requires.append({"parent": nid, "op": op["op_id"], "seq": i})
        rel_batch(
            "UNWIND $rows AS r "
            f"MATCH (p:{PRODUCT}|{COMPONENT}) "
            "WHERE (p:Product AND p.product_id = r.parent) OR (p:Component AND p.component_id = r.parent) "
            f"MATCH (o:{OPERATION}) WHERE o.op_id = r.op "
            f"MERGE (p)-[:{REQUIRES} {{sequence: r.seq}}]->(o)",
            requires,
        )

        # CONSUMES (product/component → activity)
        consumes = []
        for p in PRODUCTS + COMPONENTS:
            nid_key = "product_id" if p.get("product_id") else "component_id"
            nid = p[nid_key]
            for a in p["activities"]:
                consumes.append({"parent": nid, "act": a["activity_id"], "quantity": a["quantity"]})
        rel_batch(
            "UNWIND $rows AS r "
            f"MATCH (p:{PRODUCT}|{COMPONENT}) "
            "WHERE (p:Product AND p.product_id = r.parent) OR (p:Component AND p.component_id = r.parent) "
            f"MATCH (a:{ACTIVITY}) WHERE a.activity_id = r.act "
            f"MERGE (p)-[:{CONSUMES} {{quantity: r.quantity}}]->(a)",
            consumes,
        )

        # PERFORMED_ON (operation → machine)
        performed_on = []
        for op in OPERATION_LINES.values():
            machine = _machine_for(op)
            if machine:
                performed_on.append({"op": op["op_id"], "machine": machine})
        rel_batch(
            "UNWIND $rows AS r "
            f"MATCH (o:{OPERATION}) WHERE o.op_id = r.op "
            f"MATCH (m:{MACHINE}) WHERE m.machine_id = r.machine "
            f"MERGE (o)-[:{PERFORMED_ON}]->(m)",
            performed_on,
        )

    counts = _counts(driver, database)
    return counts


def _id_prop(label: str) -> str:
    from app.kg.schema import ID_PROPERTY

    return ID_PROPERTY[label]


def _machine_for(op: dict) -> str | None:
    """Reverse-lookup machine for an operation via catalog machine rates."""
    machine_rate = op.get("machine_rate", "0.00")
    if machine_rate == "0.00":
        return None
    from app.synth.catalog import MACHINES

    for m in MACHINES:
        if m["hourly_rate"] == machine_rate:
            return m["machine_id"]
    return None


def _counts(driver: Driver, database: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for label in (MATERIAL, MACHINE, OPERATION, ACTIVITY, COMPONENT, PRODUCT):
        rec = driver.execute_query(
            f"MATCH (n:{label}) RETURN count(n) AS c", database_=database
        ).records[0]
        counts[label] = int(rec["c"])
    for rel, nodes in [
        (CONTAINS, (f"{PRODUCT}|{COMPONENT}", f"{COMPONENT}")),
        (USES_MATERIAL, (f"{PRODUCT}|{COMPONENT}", MATERIAL)),
        (REQUIRES, (f"{PRODUCT}|{COMPONENT}", OPERATION)),
        (CONSUMES, (f"{PRODUCT}|{COMPONENT}", ACTIVITY)),
        (PERFORMED_ON, (OPERATION, MACHINE)),
    ]:
        rec = driver.execute_query(
            f"MATCH (:{nodes[0]})-[r:{rel}]->(:{nodes[1]}) RETURN count(r) AS c",
            database_=database,
        ).records[0]
        counts[f"rel_{rel.lower()}"] = int(rec["c"])
    return counts
