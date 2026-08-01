"""BOMFetcher over Neo4j — read paths used by the rollup and API."""

from __future__ import annotations

from neo4j import Driver
from neo4j.exceptions import AuthError, ConfigurationError, ServiceUnavailable

from app.kg.schema import (
    ACTIVITY,
    COMPONENT,
    CONSUMES,
    CONTAINS,
    MATERIAL,
    OPERATION,
    PRODUCT,
    REQUIRES,
    USES_MATERIAL,
)


class KGQueries:
    """Thin read adapter over a neo4j.Driver implementing BOMFetcher."""

    def __init__(self, driver: Driver, database: str = "neo4j"):
        self._driver = driver
        self._database = database

    # -- helpers ------------------------------------------------------------
    def _match(self, node_id: str) -> str:
        return (
            f"MATCH (n:{PRODUCT}|{COMPONENT}) "
            f"WHERE n.product_id = $node_id OR n.component_id = $node_id"
        )

    # -- BOMFetcher interface -----------------------------------------------
    def get_node(self, node_id: str) -> dict:
        rec = self._driver.execute_query(
            self._match(node_id) + " RETURN n, n.product_id AS pid, n.component_id AS cid",
            node_id=node_id,
            database_=self._database,
        ).records
        if not rec:
            raise KeyError(f"unknown node: {node_id}")
        n = rec[0]["n"]
        return {
            "node_id": node_id,
            "name": n.get("name"),
            "unit": n.get("unit"),
            "type": PRODUCT if rec[0]["pid"] else COMPONENT,
        }

    def get_children(self, node_id: str) -> list[dict]:
        recs = self._driver.execute_query(
            self._match(node_id)
            + f" MATCH (n)-[c:{CONTAINS}]->(child:{COMPONENT}) "
            "RETURN child.component_id AS id, c.quantity AS qty ORDER BY child.component_id",
            node_id=node_id,
            database_=self._database,
        ).records
        return [{"node_id": r["id"], "quantity": r["qty"]} for r in recs]

    def get_materials(self, node_id: str) -> list[dict]:
        recs = self._driver.execute_query(
            self._match(node_id)
            + f" MATCH (n)-[u:{USES_MATERIAL}]->(m:{MATERIAL}) "
            "RETURN m.part_id AS part_id, m.name AS name, m.unit AS unit, "
            "m.unit_price AS unit_price, u.quantity AS quantity "
            "ORDER BY u.sequence",
            node_id=node_id,
            database_=self._database,
        ).records
        return [dict(r) for r in recs]

    def get_operations(self, node_id: str) -> list[dict]:
        recs = self._driver.execute_query(
            self._match(node_id)
            + f" MATCH (n)-[r:{REQUIRES}]->(o:{OPERATION}) "
            "RETURN o.op_id AS op_id, o.name AS name, o.hours AS hours, "
            "o.labor_rate AS labor_rate, o.machine_rate AS machine_rate "
            "ORDER BY r.sequence",
            node_id=node_id,
            database_=self._database,
        ).records
        return [dict(r) for r in recs]

    def get_activities(self, node_id: str) -> list[dict]:
        recs = self._driver.execute_query(
            self._match(node_id)
            + f" MATCH (n)-[c:{CONSUMES}]->(a:{ACTIVITY}) "
            "RETURN a.activity_id AS activity_id, a.name AS name, "
            "a.driver_rate AS driver_rate, c.quantity AS quantity",
            node_id=node_id,
            database_=self._database,
        ).records
        return [dict(r) for r in recs]

    # -- catalog -------------------------------------------------------------
    def list_products(self) -> list[dict]:
        recs = self._driver.execute_query(
            f"MATCH (p:{PRODUCT}) RETURN p.product_id AS product_id, p.name AS name, "
            "p.unit AS unit ORDER BY p.product_id",
            database_=self._database,
        ).records
        return [dict(r) for r in recs]

    def health(self) -> bool:
        try:
            self._driver.execute_query("RETURN 1", database_=self._database)
            return True
        except (ServiceUnavailable, AuthError, ConfigurationError, OSError):
            return False
