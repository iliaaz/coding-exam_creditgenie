"""Seed order data — 5000 orders across 500 customers."""

from datetime import UTC, datetime, timedelta
from typing import Any

NUM_CUSTOMERS = 500
ORDERS_PER_CUSTOMER = 10
CUST_42_ORDER_COUNT = 847

STATUSES = ("completed", "refunded", "canceled", "processing")
REFUND_REASONS = ("damaged", "wrong_item", "late_delivery")
NOTES = ("free promotional item", "gift wrap requested", "priority shipping")

# Canonical orders for cust_42 from sample_output.json.
CANONICAL_CUST_42_ORDERS: tuple[dict[str, Any], ...] = (
    {
        "id": "ord_1001",
        "customer_id": "cust_42",
        "status": "completed",
        "total": 129.99,
        "items": 3,
        "created_at": "2026-03-15T14:30:00Z",
        "delivered_at": "2026-03-18T09:00:00Z",
    },
    {
        "id": "ord_1002",
        "customer_id": "cust_42",
        "status": "refunded",
        "total": 49.99,
        "items": 1,
        "created_at": "2026-03-10T08:15:00Z",
        "delivered_at": "2026-03-12T11:00:00Z",
        "refund_reason": "damaged",
    },
    {
        "id": "ord_1003",
        "customer_id": "cust_42",
        "status": "canceled",
        "total": 299.00,
        "items": 5,
        "created_at": "2026-03-08T22:45:00Z",
        "delivered_at": None,
    },
    {
        "id": "ord_1004",
        "customer_id": "cust_42",
        "status": "processing",
        "total": 74.50,
        "items": 2,
        "created_at": "2026-04-01T16:20:00Z",
        "delivered_at": None,
    },
    {
        "id": "ord_1005",
        "customer_id": "cust_42",
        "status": "completed",
        "total": 0.00,
        "items": 1,
        "created_at": "2026-02-14T00:00:00Z",
        "delivered_at": "2026-02-14T00:00:00Z",
        "note": "free promotional item",
    },
    {
        "id": "ord_1006",
        "customer_id": "cust_42",
        "status": "completed",
        "total": 1249.99,
        "items": 12,
        "created_at": "2025-06-01T10:00:00Z",
        "delivered_at": "2025-06-05T14:30:00Z",
    },
)

_BASE_CREATED_AT = datetime(2021, 6, 1, 10, 0, tzinfo=UTC)
_DATE_RANGE_DAYS = 5 * 365


def _format_timestamp(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _customer_id(customer_number: int) -> str:
    return f"cust_{customer_number}"


RESERVED_ORDER_NUMBERS = frozenset(range(1001, 1007))


def _order_id(order_number: int) -> str:
    if order_number in RESERVED_ORDER_NUMBERS:
        return f"ord_{order_number + 5000}"
    return f"ord_{order_number}"


def _generate_order(
    *,
    order_number: int,
    customer_number: int,
    sequence: int,
) -> dict[str, Any]:
    status = STATUSES[(customer_number + sequence) % len(STATUSES)]
    created_at = _BASE_CREATED_AT + timedelta(
        days=(order_number * 17 + customer_number * 3) % _DATE_RANGE_DAYS,
        hours=(sequence * 5) % 24,
        minutes=(order_number * 11) % 60,
    )
    items = (order_number % 12) + 1
    total = round(((order_number * 13) % 12500) / 100, 2)

    order: dict[str, Any] = {
        "id": _order_id(order_number),
        "customer_id": _customer_id(customer_number),
        "status": status,
        "total": total,
        "items": items,
        "created_at": _format_timestamp(created_at),
        "delivered_at": None,
    }

    if status in {"completed", "refunded"}:
        delivered_at = created_at + timedelta(days=(sequence % 7) + 1)
        order["delivered_at"] = _format_timestamp(delivered_at)

    if status == "refunded":
        order["refund_reason"] = REFUND_REASONS[sequence % len(REFUND_REASONS)]

    if status == "completed" and sequence % 17 == 0:
        order["note"] = NOTES[sequence % len(NOTES)]

    return order


def generate_seed_orders() -> list[dict[str, Any]]:
    """Return seed orders: 10 per customer, with cust_42 expanded to 847 orders."""
    orders: list[dict[str, Any]] = []

    for customer_number in range(1, NUM_CUSTOMERS + 1):
        start_order_number = (customer_number - 1) * ORDERS_PER_CUSTOMER + 1
        customer_id = _customer_id(customer_number)

        if customer_id == "cust_42":
            orders.extend(CANONICAL_CUST_42_ORDERS)
            for sequence in range(CUST_42_ORDER_COUNT - len(CANONICAL_CUST_42_ORDERS)):
                order_number = 50_000 + sequence
                orders.append(
                    _generate_order(
                        order_number=order_number,
                        customer_number=customer_number,
                        sequence=len(CANONICAL_CUST_42_ORDERS) + sequence,
                    )
                )
            continue

        for offset in range(ORDERS_PER_CUSTOMER):
            order_number = start_order_number + offset
            orders.append(
                _generate_order(
                    order_number=order_number,
                    customer_number=customer_number,
                    sequence=offset,
                )
            )

    return orders


SEED_ORDERS: list[dict[str, Any]] = generate_seed_orders()
NUM_ORDERS = len(SEED_ORDERS)


def orders_for_customer(customer_id: str) -> list[dict[str, Any]]:
    """Return all seed orders for a customer."""
    return [order for order in SEED_ORDERS if order["customer_id"] == customer_id]
