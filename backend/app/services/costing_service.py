"""Bridges rollup engine ↔ data source (Neo4j, or in-memory catalog fallback)."""

from __future__ import annotations

import logging
from functools import lru_cache

from neo4j import GraphDatabase

from app.config import settings
from app.core.costing.abc import ActivityBasedCostingEngine
from app.core.costing.monte_carlo import scaled_totals, simulate
from app.core.costing.rollup import BOMFetcher, rollup
from app.kg.queries import KGQueries
from app.synth.fetcher import CatalogFetcher

logger = logging.getLogger(__name__)


@lru_cache
def get_fetcher() -> tuple[KGQueries | None, CatalogFetcher]:
    """Prefer Neo4j; fall back to the in-memory catalog when the DB is down."""
    from neo4j.exceptions import AuthError, ConfigurationError, ServiceUnavailable

    try:
        driver = GraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
        )
        driver.verify_connectivity()
        kg = KGQueries(driver, settings.neo4j_database)
        if kg.health():
            return kg, CatalogFetcher()
    except (ServiceUnavailable, AuthError, ConfigurationError, OSError) as exc:
        logger.debug("Neo4j unavailable (%s) — using in-memory catalog", exc)
    return None, CatalogFetcher()


def active_fetcher() -> BOMFetcher:
    kg, mem = get_fetcher()
    return kg if kg is not None else mem


def using_graph() -> bool:
    return get_fetcher()[0] is not None


class CostingService:
    def __init__(self, fetcher: BOMFetcher | None = None, engine: ActivityBasedCostingEngine | None = None):
        self.fetcher = fetcher or active_fetcher()
        self.engine = engine or ActivityBasedCostingEngine()

    def estimate(self, product_id: str, quantity: int = 1, mc_runs: int = 0, seed: int = 42) -> dict:
        result = rollup(product_id, self.fetcher, self.engine)
        payload = result.to_dict(quantity)
        payload["source"] = "neo4j" if using_graph() else "catalog"
        if mc_runs > 0:
            mc = simulate(result.per_unit, runs=mc_runs, seed=seed)
            payload["monte_carlo"] = {
                **mc,
                "total_for_quantity": scaled_totals(mc, quantity),
            }
        else:
            payload["monte_carlo"] = None
        return payload

    def list_products(self) -> list[dict]:
        return self.fetcher.list_products()


@lru_cache
def get_service() -> CostingService:
    return CostingService()
