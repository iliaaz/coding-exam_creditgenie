"""Integration tests — critical flows crossing HTTP and database boundaries."""

import pytest
from fastapi.testclient import TestClient

from order_history import CUSTOMER_VISIBLE_FIELDS, SUPPORT_ONLY_FIELDS
from tests.conftest import (
    CUSTOMER_ID,
    OTHER_CUSTOMER_ID,
    customer_headers,
    support_headers,
)


@pytest.mark.integration
def test_http_customer_happy_path_returns_own_orders(api_client: TestClient) -> None:
    """GIVEN a valid customer HTTP request WHEN GET /orders THEN return own data."""
    response = api_client.get(
        "/orders",
        params={"customer_id": CUSTOMER_ID},
        headers=customer_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_orders_for_customer"] > 0
    assert len(body["orders"]) > 0
    assert "total_pages" in body
    assert "next_page_token" in body
    assert "previous_page_token" in body
    for order in body["orders"]:
        assert set(order) == set(CUSTOMER_VISIBLE_FIELDS)


@pytest.mark.integration
def test_http_customer_forbidden_for_other_customer(
    api_client: TestClient,
    seeded_target_customer_orders: list[dict[str, object]],
    seeded_other_customer_orders: list[dict[str, object]],
) -> None:
    """GIVEN a customer request for another customer WHEN GET /orders THEN 403."""
    assert seeded_target_customer_orders[0]["customer_id"] == CUSTOMER_ID
    assert seeded_other_customer_orders[0]["customer_id"] == OTHER_CUSTOMER_ID

    response = api_client.get(
        "/orders",
        params={"customer_id": CUSTOMER_ID},
        headers=customer_headers(customer_id=OTHER_CUSTOMER_ID),
    )

    assert response.status_code == 403


@pytest.mark.integration
def test_http_support_agent_sees_full_order_data(api_client: TestClient) -> None:
    """GIVEN a support agent HTTP request WHEN GET /orders THEN return all fields."""
    response = api_client.get(
        "/orders",
        params={"customer_id": CUSTOMER_ID},
        headers=support_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["orders"]) > 0
    order_with_extra_fields = next(
        order
        for order in body["orders"]
        if order.get("refund_reason") is not None or order.get("note") is not None
    )
    assert "id" in order_with_extra_fields
    assert "customer_id" in order_with_extra_fields
    assert set(CUSTOMER_VISIBLE_FIELDS).issubset(order_with_extra_fields)


@pytest.mark.integration
def test_http_support_agent_can_query_any_customer(api_client: TestClient) -> None:
    """GIVEN a support agent WHEN querying any customer THEN return their orders."""
    response = api_client.get(
        "/orders",
        params={"customer_id": CUSTOMER_ID},
        headers=support_headers(),
    )

    assert response.status_code == 200
    assert response.json()["total_orders_for_customer"] > 0


@pytest.mark.integration
def test_http_filters_by_status_and_order_date(api_client: TestClient) -> None:
    """GIVEN status and order_date params WHEN GET /orders THEN filter results."""
    response = api_client.get(
        "/orders",
        params={
            "customer_id": CUSTOMER_ID,
            "status": "completed",
            "order_date": "2026-03-15",
        },
        headers=support_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["orders"]) > 0
    for order in body["orders"]:
        assert order["status"] == "completed"
        assert order["created_at"].startswith("2026-03-15")


@pytest.mark.integration
def test_http_filter_by_order_id(api_client: TestClient) -> None:
    """GIVEN an order_id param WHEN GET /orders THEN return only the matching order."""
    all_orders_response = api_client.get(
        "/orders",
        params={"customer_id": CUSTOMER_ID},
        headers=support_headers(),
    )
    target_id = all_orders_response.json()["orders"][0]["id"]

    response = api_client.get(
        "/orders",
        params={"customer_id": CUSTOMER_ID, "order_id": target_id},
        headers=support_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["orders"]) == 1
    assert body["orders"][0]["id"] == target_id


@pytest.mark.integration
def test_http_pagination_with_page_tokens(api_client: TestClient) -> None:
    """GIVEN paginated history WHEN using page_token THEN navigate pages via HTTP."""
    first_page = api_client.get(
        "/orders",
        params={"customer_id": CUSTOMER_ID},
        headers=support_headers(),
    )
    assert first_page.status_code == 200
    first_body = first_page.json()
    assert first_body["total_orders_for_customer"] > 50
    assert len(first_body["orders"]) == 50
    assert first_body["next_page_token"] is not None

    second_page = api_client.get(
        "/orders",
        params={
            "customer_id": CUSTOMER_ID,
            "page_token": first_body["next_page_token"],
        },
        headers=support_headers(),
    )

    assert second_page.status_code == 200
    second_body = second_page.json()
    assert second_body["previous_page_token"] is not None
    first_ids = {order["id"] for order in first_body["orders"]}
    second_ids = {order["id"] for order in second_body["orders"]}
    assert first_ids.isdisjoint(second_ids)


@pytest.mark.integration
def test_http_customer_response_excludes_support_only_fields(
    api_client: TestClient,
) -> None:
    """GIVEN a customer HTTP request WHEN orders have support metadata THEN omit it."""
    response = api_client.get(
        "/orders",
        params={"customer_id": CUSTOMER_ID},
        headers=customer_headers(),
    )

    assert response.status_code == 200
    for order in response.json()["orders"]:
        assert SUPPORT_ONLY_FIELDS.isdisjoint(order.keys())


@pytest.mark.integration
def test_http_invalid_requester_profile_rejected(api_client: TestClient) -> None:
    """GIVEN an invalid requester profile WHEN GET /orders THEN reject."""
    response = api_client.get(
        "/orders",
        params={"customer_id": CUSTOMER_ID},
        headers={
            "X-Requester-Profile": "invalid",
            "X-Requester-Id": "user_1",
        },
    )

    assert response.status_code in {400, 403, 422}


@pytest.mark.integration
def test_database_is_preloaded_with_customer_orders(api_client: TestClient) -> None:
    """GIVEN a fresh app WHEN querying THEN seeded customer order data is available."""
    response = api_client.get(
        "/orders",
        params={"customer_id": CUSTOMER_ID},
        headers=support_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_orders_for_customer"] >= len(body["orders"])
    known_order = next(
        (order for order in body["orders"] if order["id"] == "ord_1001"),
        None,
    )
    assert known_order is not None
    assert known_order["customer_id"] == CUSTOMER_ID
    assert known_order["status"] == "completed"
    assert known_order["total"] == 129.99
