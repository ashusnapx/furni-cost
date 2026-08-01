"""Neo4j integration — skipped when the DB is down (CI/dev without Docker).

Verifies: load counts, catalog read paths, and that KG rollup matches the
in-memory blueprint rollup exactly for every product.
"""

from __future__ import annotations

import pytest
from neo4j import GraphDatabase

from app.config import settings
from app.core.costing.abc import ActivityBasedCostingEngine
from app.core.costing.rollup import rollup
from app.kg.loader import load_catalog
from app.kg.queries import KGQueries
from app.synth.catalog import PRODUCTS
from app.synth.fetcher import CatalogFetcher

ENGINE = ActivityBasedCostingEngine()

EXPECTED_NODES = {"Material": 15, "Machine": 6, "Operation": 15, "Activity": 7, "Component": 9, "Product": 4}
EXPECTED_RELS = {"rel_contains": 10, "rel_uses_material": 32, "rel_requires": 41, "rel_consumes": 46, "rel_performed_on": 11}


@pytest.fixture(scope="module")
def driver():
    from neo4j.exceptions import ServiceUnavailable

    d = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
    try:
        d.verify_connectivity()
    except ServiceUnavailable:
        pytest.skip("Neo4j not reachable — run: docker compose -f infra/docker-compose.yml up -d neo4j")
    yield d
    d.close()


@pytest.fixture(scope="module")
def kg(driver):
    load_catalog(driver, settings.neo4j_database)
    return KGQueries(driver, settings.neo4j_database)


def test_load_counts(driver, kg):
    counts = load_catalog(driver, settings.neo4j_database)
    for node, expected in EXPECTED_NODES.items():
        assert counts[node] == expected, node
    for rel, expected in EXPECTED_RELS.items():
        assert counts[rel] == expected, rel


def test_kg_rollup_matches_catalog(driver, kg):
    for p in PRODUCTS:
        from_graph = rollup(p["product_id"], kg, ENGINE).total
        from_memory = rollup(p["product_id"], CatalogFetcher(), ENGINE).total
        assert from_graph == from_memory, p["product_id"]


def test_list_products(driver, kg):
    products = kg.list_products()
    assert len(products) == 4
    assert all(p["product_id"].startswith("prod-") for p in products)


def test_unknown_node(driver, kg):
    with pytest.raises(KeyError):
        kg.get_node("nope-123")
