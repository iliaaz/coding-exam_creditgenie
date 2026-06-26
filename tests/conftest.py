"""Shared pytest fixtures."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from order_history import (
    OrderQuery,
    Requester,
    RequesterRole,
    create_app,
    init_database,
)
from order_history.seed_data import orders_for_customer

CUSTOMER_ID = "cust_42"
OTHER_CUSTOMER_ID = "cust_99"


@pytest.fixture
def seeded_target_customer_orders() -> list[dict[str, object]]:
    orders = orders_for_customer(CUSTOMER_ID)
    assert orders, f"seed data must include orders for {CUSTOMER_ID}"
    return orders


@pytest.fixture
def seeded_other_customer_orders() -> list[dict[str, object]]:
    orders = orders_for_customer(OTHER_CUSTOMER_ID)
    assert orders, f"seed data must include orders for {OTHER_CUSTOMER_ID}"
    return orders


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "orders.db"
    init_database(path)
    return path


@pytest.fixture
def customer_requester() -> Requester:
    return Requester(
        id="user_42",
        role=RequesterRole.CUSTOMER,
        customer_id=CUSTOMER_ID,
    )


@pytest.fixture
def other_customer_requester() -> Requester:
    return Requester(
        id="user_99",
        role=RequesterRole.CUSTOMER,
        customer_id=OTHER_CUSTOMER_ID,
    )


@pytest.fixture
def support_requester() -> Requester:
    return Requester(id="agent_1", role=RequesterRole.SUPPORT_AGENT)


@pytest.fixture
def base_query() -> OrderQuery:
    return OrderQuery(customer_id=CUSTOMER_ID)


@pytest.fixture
def api_client(db_path: Path) -> Iterator[TestClient]:
    app = create_app(db_path=db_path)
    with TestClient(app) as client:
        yield client


def customer_headers(customer_id: str = CUSTOMER_ID) -> dict[str, str]:
    return {
        "X-Requester-Profile": RequesterRole.CUSTOMER,
        "X-Requester-Customer-Id": customer_id,
        "X-Requester-Id": f"user_{customer_id.removeprefix('cust_')}",
    }


def support_headers() -> dict[str, str]:
    return {
        "X-Requester-Profile": RequesterRole.SUPPORT_AGENT,
        "X-Requester-Id": "agent_1",
    }
