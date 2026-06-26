import sqlite3
from pathlib import Path

from order_history.access import verify_requester_access
from order_history.models import (
    OrderListResponse,
    OrderQuery,
    Requester,
    RequesterRole,
)
from order_history.pagination import (
    decode_page_offset,
    page_tokens,
    total_pages,
)
from order_history.repository import count_orders_for_customer, fetch_orders


def _serialize_order(row: sqlite3.Row, *, for_customer: bool) -> dict[str, object]:
    if for_customer:
        return {
            "status": row["status"],
            "total": row["total"],
            "items": row["items"],
            "created_at": row["created_at"],
            "delivered_at": row["delivered_at"],
        }

    order: dict[str, object] = {
        "id": row["id"],
        "customer_id": row["customer_id"],
        "status": row["status"],
        "total": row["total"],
        "items": row["items"],
        "created_at": row["created_at"],
        "delivered_at": row["delivered_at"],
    }
    if row["refund_reason"] is not None:
        order["refund_reason"] = row["refund_reason"]
    if row["note"] is not None:
        order["note"] = row["note"]
    return order


def get_orders(
    requester: Requester,
    query: OrderQuery,
    *,
    db_path: Path,
) -> OrderListResponse:
    """Return filtered, paginated orders according to requester profile."""
    verify_requester_access(requester, query.customer_id)

    for_customer = requester.role == RequesterRole.CUSTOMER
    total_orders_for_customer = count_orders_for_customer(
        db_path,
        query,
        include_order_id=False,
    )
    paginated_total = count_orders_for_customer(
        db_path,
        query,
        include_order_id=True,
    )
    offset = decode_page_offset(query.page_token)
    rows = fetch_orders(
        db_path,
        query,
        offset=offset,
        limit=query.page_size,
    )
    next_page_token, previous_page_token = page_tokens(
        offset=offset,
        page_size=query.page_size,
        total_items=paginated_total,
    )

    return OrderListResponse(
        orders=[_serialize_order(row, for_customer=for_customer) for row in rows],
        total_orders_for_customer=total_orders_for_customer,
        total_pages=total_pages(paginated_total, query.page_size),
        next_page_token=next_page_token,
        previous_page_token=previous_page_token,
    )
