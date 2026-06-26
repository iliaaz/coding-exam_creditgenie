"""Unit tests — positive and negative cases from SPEC.md scenarios."""

from datetime import date
from pathlib import Path

import pytest

from order_history import (
    CUSTOMER_VISIBLE_FIELDS,
    SUPPORT_ONLY_FIELDS,
    AccessDeniedError,
    InvalidRequesterError,
    OrderQuery,
    Requester,
    RequesterRole,
    get_orders,
)
from tests.conftest import CUSTOMER_ID, OTHER_CUSTOMER_ID


def _assert_customer_visible_order(order: dict[str, object]) -> None:
    assert set(order) == CUSTOMER_VISIBLE_FIELDS
    assert isinstance(order["status"], str)
    assert isinstance(order["total"], (int, float))
    assert isinstance(order["items"], int)
    assert isinstance(order["created_at"], str)
    assert order["delivered_at"] is None or isinstance(order["delivered_at"], str)


@pytest.mark.unit
def test_customer_returns_own_filtered_orders(
    db_path: Path,
    customer_requester: Requester,
    base_query: OrderQuery,
) -> None:
    """GIVEN a valid customer request WHEN querying own orders THEN return data."""
    response = get_orders(customer_requester, base_query, db_path=db_path)

    assert response.total_orders_for_customer > 0
    assert len(response.orders) > 0
    assert response.total_pages >= 1
    for order in response.orders:
        _assert_customer_visible_order(order)


@pytest.mark.unit
def test_customer_cannot_access_other_customer_orders(
    db_path: Path,
    other_customer_requester: Requester,
    seeded_target_customer_orders: list[dict[str, object]],
    seeded_other_customer_orders: list[dict[str, object]],
) -> None:
    """GIVEN a customer request for another customer WHEN querying THEN deny."""
    assert seeded_target_customer_orders[0]["customer_id"] == CUSTOMER_ID
    assert seeded_other_customer_orders[0]["customer_id"] == OTHER_CUSTOMER_ID
    assert other_customer_requester.customer_id != CUSTOMER_ID
    query = OrderQuery(customer_id=CUSTOMER_ID)

    with pytest.raises(AccessDeniedError):
        get_orders(other_customer_requester, query, db_path=db_path)


@pytest.mark.unit
def test_support_agent_sees_all_order_fields(
    db_path: Path,
    support_requester: Requester,
    base_query: OrderQuery,
) -> None:
    """GIVEN a support agent request WHEN querying THEN return full order records."""
    response = get_orders(support_requester, base_query, db_path=db_path)

    assert len(response.orders) > 0
    order_with_support_fields = next(
        order
        for order in response.orders
        if order.get("refund_reason") is not None or order.get("note") is not None
    )
    assert "id" in order_with_support_fields
    assert "customer_id" in order_with_support_fields
    assert CUSTOMER_VISIBLE_FIELDS.issubset(order_with_support_fields.keys())


@pytest.mark.unit
def test_support_agent_can_query_any_customer(
    db_path: Path,
    support_requester: Requester,
) -> None:
    """GIVEN a support agent WHEN querying any customer THEN return their data."""
    query = OrderQuery(customer_id=CUSTOMER_ID)

    response = get_orders(support_requester, query, db_path=db_path)

    assert response.total_orders_for_customer > 0
    assert len(response.orders) > 0


@pytest.mark.unit
def test_customer_response_excludes_support_only_fields(
    db_path: Path,
    customer_requester: Requester,
    base_query: OrderQuery,
) -> None:
    """GIVEN a customer request WHEN orders have extra metadata THEN hide it."""
    response = get_orders(customer_requester, base_query, db_path=db_path)

    for order in response.orders:
        assert SUPPORT_ONLY_FIELDS.isdisjoint(order.keys())


@pytest.mark.unit
def test_filter_by_order_id(
    db_path: Path,
    support_requester: Requester,
) -> None:
    """GIVEN an order_id filter WHEN querying THEN return only the matching order."""
    all_orders = get_orders(
        support_requester,
        OrderQuery(customer_id=CUSTOMER_ID),
        db_path=db_path,
    )
    target_id = all_orders.orders[0]["id"]
    assert isinstance(target_id, str)

    response = get_orders(
        support_requester,
        OrderQuery(customer_id=CUSTOMER_ID, order_id=target_id),
        db_path=db_path,
    )

    assert len(response.orders) == 1
    assert response.orders[0]["id"] == target_id


@pytest.mark.unit
def test_filter_by_status(
    db_path: Path,
    support_requester: Requester,
) -> None:
    """GIVEN a status filter WHEN querying THEN return only orders with that status."""
    status = "completed"

    response = get_orders(
        support_requester,
        OrderQuery(customer_id=CUSTOMER_ID, status=status),
        db_path=db_path,
    )

    assert len(response.orders) > 0
    assert all(order["status"] == status for order in response.orders)


@pytest.mark.unit
def test_filter_by_order_date(
    db_path: Path,
    support_requester: Requester,
) -> None:
    """GIVEN an order_date filter WHEN querying THEN return orders on that date."""
    order_date = date(2026, 3, 15)

    response = get_orders(
        support_requester,
        OrderQuery(customer_id=CUSTOMER_ID, order_date=order_date),
        db_path=db_path,
    )

    assert len(response.orders) > 0
    for order in response.orders:
        created_at = order["created_at"]
        assert isinstance(created_at, str)
        assert created_at.startswith("2026-03-15")


@pytest.mark.unit
def test_customer_missing_customer_id_rejected(db_path: Path) -> None:
    """GIVEN a customer without customer_id WHEN querying THEN reject the request."""
    requester = Requester(id="user_1", role=RequesterRole.CUSTOMER, customer_id=None)
    query = OrderQuery(customer_id=CUSTOMER_ID)

    with pytest.raises((InvalidRequesterError, AccessDeniedError, ValueError)):
        get_orders(requester, query, db_path=db_path)


@pytest.mark.unit
def test_pagination_defaults_to_page_size_fifty(
    db_path: Path,
    support_requester: Requester,
) -> None:
    """GIVEN more than 50 orders WHEN querying THEN return 50 per page by default."""
    response = get_orders(
        support_requester,
        OrderQuery(customer_id=CUSTOMER_ID),
        db_path=db_path,
    )

    assert response.total_orders_for_customer > 50
    assert len(response.orders) == 50
    assert response.total_pages == (response.total_orders_for_customer + 49) // 50
    assert response.next_page_token is not None
    assert response.previous_page_token is None


@pytest.mark.unit
def test_pagination_next_and_previous_tokens(
    db_path: Path,
    support_requester: Requester,
) -> None:
    """GIVEN paginated results WHEN using page tokens THEN navigate between pages."""
    first_page = get_orders(
        support_requester,
        OrderQuery(customer_id=CUSTOMER_ID),
        db_path=db_path,
    )
    second_page = get_orders(
        support_requester,
        OrderQuery(
            customer_id=CUSTOMER_ID,
            page_token=first_page.next_page_token,
        ),
        db_path=db_path,
    )

    assert first_page.next_page_token is not None
    assert second_page.previous_page_token is not None
    assert len(second_page.orders) > 0
    first_page_ids = {order["id"] for order in first_page.orders}
    second_page_ids = {order["id"] for order in second_page.orders}
    assert first_page_ids.isdisjoint(second_page_ids)


@pytest.mark.unit
def test_empty_result_for_non_matching_filters(
    db_path: Path,
    support_requester: Requester,
) -> None:
    """GIVEN filters that match no orders WHEN querying THEN return an empty page."""
    response = get_orders(
        support_requester,
        OrderQuery(customer_id=CUSTOMER_ID, order_id="ord_does_not_exist"),
        db_path=db_path,
    )

    assert response.orders == []
    assert response.total_orders_for_customer > 0
    assert response.total_pages >= 1


@pytest.mark.unit
def test_response_includes_total_orders_for_customer(
    db_path: Path,
    customer_requester: Requester,
    base_query: OrderQuery,
) -> None:
    """GIVEN a valid request WHEN querying THEN include total_orders_for_customer."""
    response = get_orders(customer_requester, base_query, db_path=db_path)

    assert response.total_orders_for_customer >= len(response.orders)
