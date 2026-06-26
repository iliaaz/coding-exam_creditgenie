import sqlite3
from pathlib import Path

from order_history.database import connect
from order_history.models import OrderQuery


def _build_filters(
    query: OrderQuery,
    *,
    include_order_id: bool,
) -> tuple[str, list[object]]:
    clauses = ["customer_id = ?"]
    params: list[object] = [query.customer_id]

    if query.status is not None:
        clauses.append("status = ?")
        params.append(query.status)

    if query.order_date is not None:
        clauses.append("substr(created_at, 1, 10) = ?")
        params.append(query.order_date.isoformat())

    if include_order_id and query.order_id is not None:
        clauses.append("id = ?")
        params.append(query.order_id)

    return " AND ".join(clauses), params


def count_orders_for_customer(
    db_path: Path,
    query: OrderQuery,
    *,
    include_order_id: bool,
) -> int:
    where_clause, params = _build_filters(query, include_order_id=include_order_id)
    sql = f"SELECT COUNT(*) FROM orders WHERE {where_clause}"

    with connect(db_path) as connection:
        row = connection.execute(sql, params).fetchone()

    return int(row[0])


def fetch_orders(
    db_path: Path,
    query: OrderQuery,
    *,
    offset: int,
    limit: int,
) -> list[sqlite3.Row]:
    where_clause, params = _build_filters(query, include_order_id=True)
    sql = f"""
        SELECT
            id, customer_id, status, total, items,
            created_at, delivered_at, refund_reason, note
        FROM orders
        WHERE {where_clause}
        ORDER BY created_at DESC, id DESC
        LIMIT ? OFFSET ?
    """

    with connect(db_path) as connection:
        rows = connection.execute(sql, [*params, limit, offset]).fetchall()

    return list(rows)
